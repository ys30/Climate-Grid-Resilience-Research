"""Exploratory day-block bootstrap of within-unit EPA source associations.

Day fixed effects are absorbed by within-resampled-day demeaning. Resampling
local-standard calendar-day blocks preserves within-day serial dependence,
but is NOT a causal design, independent-year validation or a proof of valid
coverage with 31 serially related hot-season days. Do not pool colocated units.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from grid_resilience.srp_epa_era5_eia930_demand_context import summarize as check_sources
from grid_resilience.srp_epa_era5_eia930_temporal_controls import design, fit


def partial_temperature_coef(frame, outcome, group_ids, *, min_n=80):
    """Day-within transformed regression: y ~ temperature + demand + hour FE + day FE."""
    y = np.asarray(outcome, dtype=float)
    t = frame.temperature_2m_c.to_numpy(dtype=float)
    d = frame.srp_demand_mw.to_numpy(dtype=float) / 1000.0
    hours = frame.local_hour.to_numpy(int)
    groups = np.asarray(group_ids)
    valid = np.isfinite(y) & np.isfinite(t) & np.isfinite(d)
    if valid.sum() < min_n:
        return None
    y, t, d, hours, groups = y[valid], t[valid], d[valid], hours[valid], groups[valid]
    if len(np.unique(groups)) < 3:
        return None
    h = (hours[:, None] == np.arange(1, 24)[None, :]).astype(float)
    matrix = np.column_stack([y, t, d, h])
    # One group per *bootstrap draw of a day*. Repeated day draws must not
    # share the same fixed-effect identifier.
    _, inverse = np.unique(groups, return_inverse=True)
    counts = np.bincount(inverse)
    totals = np.zeros((len(counts), matrix.shape[1]))
    np.add.at(totals, inverse, matrix)
    residual = matrix - totals[inverse] / counts[inverse, None]
    yr = residual[:, 0]
    tr = residual[:, 1]
    controls = residual[:, 2:]
    # Frisch-Waugh-Lovell residualization guards against a near-unidentified
    # temperature column in the specified controls.
    beta_t = np.linalg.lstsq(controls, tr, rcond=None)[0]
    beta_y = np.linalg.lstsq(controls, yr, rcond=None)[0]
    rt = tr - controls @ beta_t
    ry = yr - controls @ beta_y
    denom = float(rt @ rt)
    if denom < 1e-10 or not np.isfinite(denom):
        return None
    return float((rt @ ry) / denom)


def bootstrap_unit(frame, *, n_rep=120, seed=20261105):
    if n_rep < 50:
        raise ValueError("At least 50 replicate draws required")
    g = frame.sort_values("timestamp_utc").reset_index(drop=True).copy()
    local = g.timestamp_utc.dt.tz_convert("Etc/GMT+7")
    g["local_hour"] = local.dt.hour
    g["local_date"] = local.dt.strftime("%Y-%m-%d")
    days = g.local_date.unique()
    if len(days) != 31:
        raise ValueError("Expected exactly 31 local July day clusters")
    positions = [np.flatnonzero(g.local_date.to_numpy() == day) for day in days]
    outcomes = {
        "reported_operation_lpm": np.where(g.operating_time.notna(),
                                          (g.operating_time > 0).astype(float), np.nan),
        "gross_load_given_positive_operation_mw": np.where(
            g.operating_time.gt(0), g.gross_load_mw, np.nan).astype(float)
    }
    rng = np.random.default_rng(seed)
    # A shared draw sequence across both outcomes within a unit; each
    # repetition resamples 31 day blocks with replacement, not 737 hours.
    draws = rng.integers(0, len(days), size=(n_rep, len(days)))
    rows = []
    for outcome_name, values in outcomes.items():
        source_n = int(np.isfinite(values).sum())
        original = partial_temperature_coef(g, values, g.local_date.to_numpy())
        # Independently cross-check against the existing dummy-variable model.
        controls, temp = design(g)
        baseline = fit(values, controls, temp)
        if original is not None and baseline["status"] == "descriptive_ols_only":
            if not np.isclose(original, baseline["temp_coef"], atol=1e-7, rtol=1e-6):
                raise ValueError("Within-day estimate differs from original model")
        if (original is None) != (baseline["status"] != "descriptive_ols_only"):
            raise ValueError("Baseline admission differs from within-day estimator")
        accepted = []
        if original is not None:
            for draw in draws:
                indices = np.concatenate([positions[int(j)] for j in draw])
                groups = np.concatenate([
                    np.full(len(positions[int(j)]), k, dtype=int)
                    for k, j in enumerate(draw)
                ])
                selected = g.iloc[indices].reset_index(drop=True)
                sampled_y = values[indices]
                coef = partial_temperature_coef(selected, sampled_y, groups)
                if coef is not None and np.isfinite(coef):
                    accepted.append(coef)
        # No percentile interval from too few qualified draws.
        enough = len(accepted) >= int(np.ceil(n_rep * .90))
        lo, hi = (np.percentile(accepted, [2.5, 97.5])
                  if enough else (np.nan, np.nan))
        rows.append({
            "outcome": outcome_name,
            "source_valid_observations": source_n,
            "days_in_source": len(days),
            "point_estimate_per_c": original,
            "replicates_requested": n_rep,
            "replicates_admitted": len(accepted),
            "percentile_2_5": float(lo),
            "percentile_97_5": float(hi),
            "interval_reportable": bool(enough),
            "interval_excludes_zero_descriptively": bool(enough and lo*hi > 0),
        })
    return pd.DataFrame(rows)


def audit(epa, eia, *, n_rep=120, seed=20261105):
    # Reuse the certified exact-hour source audit; avoid any fabricated Aug 1 demand.
    _, _, gate = check_sources(epa, eia)
    x = epa.copy()
    for col in ("temperature_2m_c", "operating_time", "gross_load_mw"):
        x[col] = pd.to_numeric(x[col], errors="coerce")
    if x.operating_time.dropna().lt(0).any() or x.operating_time.dropna().gt(1).any():
        raise ValueError("Invalid operating fraction")
    x["facility_id"] = x.facility_id.astype("string").str.strip()
    x["unit_id"] = x.unit_id.astype("string").str.strip()
    x["timestamp_utc"] = pd.to_datetime(x.timestamp_utc, utc=True)
    e = eia.loc[eia["Balancing Authority"].astype("string").str.strip().eq("SRP")].copy()
    e["timestamp_utc"] = pd.to_datetime(
        e["UTC Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p",
        utc=True) - pd.Timedelta(hours=1)
    e["srp_demand_mw"] = pd.to_numeric(e["Demand (MW)"], errors="raise")
    matched = x.merge(e[["timestamp_utc", "srp_demand_mw"]],
                      on="timestamp_utc", how="inner", validate="many_to_one")
    if len(matched) != 7370:
        raise ValueError("Expected exactly 7370 matched unit-hours")
    all_results = []
    for (plant, unit), g in matched.groupby(["facility_id", "unit_id"], sort=True):
        if len(g) != 737:
            raise ValueError("EPA source-unit time coverage changed")
        result = bootstrap_unit(g, n_rep=n_rep, seed=seed)
        result.insert(0, "epa_unit_id", str(unit))
        result.insert(0, "facility_id", str(plant))
        all_results.append(result)
    out = pd.concat(all_results, ignore_index=True)
    manifest = {
        "source_matched_hours_per_epa_unit": 737,
        "source_units": 10,
        "source_local_day_clusters_per_unit": 31,
        "resampling_unit": "local standard date; day-specific FE relabeled at each resample",
        "seed": seed, "replicates_requested": n_rep,
        "method": "day-block percentile bootstrap with within-day FE demeaning",
        "point_estimate_matches_previous_controlled_ols": True,
        "interval_type": "descriptive exploratory percentile sensitivity, not validated inferential CI",
        "no_cross_unit_independence_assumed": True,
        "longer_than_day_dependence_unaddressed": True,
        "conditional_gross_load_dispatch_selected": True,
        "causal_temperature_derating_identified": False,
        "eia_generator_net_mw_or_outage_calibrated": False,
        "pypsa_reliability_calibration_authorized": False,
        "august_eia_demand_imputed": False
    }
    return out, manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epa-era5-panel", required=True)
    parser.add_argument("--eia930-july", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--replicates", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20261105)
    args = parser.parse_args()
    result, manifest = audit(
        pd.read_csv(args.epa_era5_panel, dtype={"facility_id":"string","unit_id":"string"}),
        pd.read_csv(args.eia930_july, dtype="string"),
        n_rep=args.replicates, seed=args.seed)
    dest = Path(args.output)
    dest.mkdir(parents=True, exist_ok=True)
    result.to_csv(dest / "epa_eia930_local_day_block_bootstrap.csv", index=False)
    (dest / "epa_eia930_local_day_block_bootstrap_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
