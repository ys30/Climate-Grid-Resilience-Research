"""Leave-one-local-date-out descriptive robustness of EPA source OLS fits.

Each fit drops one original 2024 local-standard day in turn. Checks whether a
single date drives the temperature association; does not correct confounding,
forecast heat impacts, or estimate physical generator availability.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from grid_resilience.srp_epa_era5_eia930_demand_context import summarize as validate_sources
from grid_resilience.srp_epa_eia930_day_block_bootstrap import partial_temperature_coef


def leave_one_day(g):
    f = g.sort_values("timestamp_utc").reset_index(drop=True).copy()
    local = f.timestamp_utc.dt.tz_convert("Etc/GMT+7")
    f["local_hour"] = local.dt.hour
    f["local_date"] = local.dt.strftime("%Y-%m-%d")
    dates = sorted(f.local_date.unique())
    if len(dates) != 31:
        raise ValueError("Expected 31 local July day blocks")
    outcomes = {
        "reported_operation_lpm": np.where(
            f.operating_time.notna(), (f.operating_time > 0).astype(float), np.nan),
        "gross_load_given_positive_operation_mw": np.where(
            f.operating_time.gt(0), f.gross_load_mw, np.nan).astype(float),
    }
    rows = []
    for label, y in outcomes.items():
        full = partial_temperature_coef(f, y, f.local_date.to_numpy())
        trials = []
        for excluded in dates:
            keep = f.local_date.ne(excluded).to_numpy()
            sample = f.loc[keep].reset_index(drop=True)
            beta = partial_temperature_coef(sample, y[keep], sample.local_date.to_numpy())
            trials.append({"excluded_date": excluded, "coefficient": beta})
        valid = np.array([q["coefficient"] for q in trials
                          if q["coefficient"] is not None], dtype=float)
        if full is None:
            classification = "full_model_insufficient_or_unidentified"
        elif len(valid) < len(dates):
            classification = "at_least_one_date_deletion_unidentified"
        elif all(np.sign(valid) == np.sign(full)):
            classification = "all_date_deletions_same_sign"
        else:
            classification = "direction_sensitive_to_day_deletion"
        rows.append({
            "outcome": label,
            "source_valid_outcome_rows": int(np.isfinite(y).sum()),
            "full_sample_coef_per_c": full,
            "local_days_tested": len(dates),
            "date_deletions_identified": len(valid),
            "min_date_deleted_coef_per_c": float(np.min(valid)) if len(valid) else np.nan,
            "max_date_deleted_coef_per_c": float(np.max(valid)) if len(valid) else np.nan,
            "max_abs_change_from_full_per_c": (
                float(np.max(np.abs(valid-full))) if len(valid) and full is not None else np.nan),
            "status": classification,
        })
    return pd.DataFrame(rows)


def audit(epa, eia):
    validate_sources(epa, eia)
    x = epa.copy()
    x["facility_id"] = x.facility_id.astype("string").str.strip()
    x["unit_id"] = x.unit_id.astype("string").str.strip()
    x["timestamp_utc"] = pd.to_datetime(x.timestamp_utc, utc=True)
    for col in ("temperature_2m_c", "operating_time", "gross_load_mw"):
        x[col] = pd.to_numeric(x[col], errors="coerce")
    if not x.operating_time.dropna().between(0, 1).all():
        raise ValueError("Invalid EPA Operating Time")
    raw = eia.loc[eia["Balancing Authority"].astype("string").str.strip().eq("SRP")].copy()
    raw["timestamp_utc"] = pd.to_datetime(raw["UTC Time at End of Hour"],
        utc=True, format="%m/%d/%Y %I:%M:%S %p")-pd.Timedelta(hours=1)
    raw["srp_demand_mw"] = pd.to_numeric(raw["Demand (MW)"], errors="raise")
    x = x.merge(raw[["timestamp_utc", "srp_demand_mw"]], how="inner",
        on="timestamp_utc", validate="many_to_one")
    if len(x) != 7370:
        raise ValueError("Expected 7370 matched source unit-hours")
    outputs = []
    for (plant, unit), g in x.groupby(["facility_id","unit_id"]):
        if len(g) != 737:
            raise ValueError("Incomplete source unit matched coverage")
        frame=leave_one_day(g)
        frame.insert(0,"epa_unit_id",str(unit))
        frame.insert(0,"facility_id",str(plant))
        outputs.append(frame)
    result = pd.concat(outputs, ignore_index=True)
    manifest = {
        "source_units": 10, "source_matched_hours_per_unit": 737,
        "local_dates_examined_per_unit": 31,
        "date_deletion_model": "EPA unit, SRP BA demand GW, MST hour FE, MST calendar-day FE, ERA5 temperature",
        "outcomes":["EPA positive Operating Time indicator",
                    "EPA reported gross load conditional on positive operation"],
        "causal_heat_effect_estimated": False,
        "physically_verified_eia_generator_identity": False,
        "power_or_outage_pypsa_calibration_allowed": False,
        "statistical_significance_claimed": False,
    }
    return result, manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--epa-era5-panel", required=True)
    p.add_argument("--eia930-july", required=True)
    p.add_argument("--output", required=True)
    a=p.parse_args()
    output,meta=audit(
        pd.read_csv(a.epa_era5_panel,dtype={"facility_id":"string","unit_id":"string"}),
        pd.read_csv(a.eia930_july,dtype="string"))
    dest=Path(a.output)
    dest.mkdir(parents=True,exist_ok=True)
    output.to_csv(dest/"epa_eia930_leave_one_local_day_out.csv",index=False)
    (dest/"epa_eia930_lodo_scope.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(output.to_string(index=False))


if __name__=="__main__":
    main()
