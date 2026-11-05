"""Descriptive site-hour and EPA source-unit operating summaries from a full July panel.

This is observational and dispatch-selected; it cannot estimate available
generator capacity or heat-driven derating. Site-weather counts are deduplicated.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

SITES = {"141", "55129", "147"}
BINS = [-np.inf, 35.0, 40.0, np.inf]
LABELS = ["below_35_c", "35_to_below_40_c", "at_least_40_c"]


def summarize(panel):
    required = {"facility_id", "unit_id", "timestamp_utc", "temperature_2m_c",
                "operating_time", "gross_load_mw", "era5_full_local_july_matched"}
    if not required.issubset(panel.columns):
        raise ValueError("Required completed source fields missing")
    x = panel.copy()
    x["facility_id"] = x.facility_id.astype("string").str.strip()
    x["unit_id"] = x.unit_id.astype("string").str.strip()
    x["timestamp_utc"] = pd.to_datetime(x.timestamp_utc, utc=True, errors="raise")
    for col in ("temperature_2m_c", "operating_time", "gross_load_mw"):
        x[col] = pd.to_numeric(x[col], errors="coerce")
    match = x.era5_full_local_july_matched
    # CSV import produces booleans in normal conditions; fail closed otherwise.
    if match.dtype != bool or match.isna().any() or not match.all():
        raise ValueError("Incomplete or invalid 744h source-weather match")
    if set(x.facility_id) != SITES or x.duplicated(["facility_id", "unit_id", "timestamp_utc"]).any():
        raise ValueError("Unexpected plants or duplicate EPA unit-hour")
    expected = pd.date_range("2024-07-01T07:00:00Z", periods=744, freq="h")
    for (_, _), group in x.groupby(["facility_id", "unit_id"]):
        if not pd.DatetimeIndex(group.timestamp_utc.sort_values()).equals(expected):
            raise ValueError("Incomplete EPA local July unit calendar")
    if x[["facility_id", "unit_id"]].isna().any().any() or (x.unit_id == "").any():
        raise ValueError("Missing EPA unit identifiers")
    if not np.isfinite(x.temperature_2m_c.to_numpy(dtype=float)).all():
        raise ValueError("Missing or invalid observed ERA5 temperature")
    if not x.operating_time.dropna().between(0, 1).all():
        raise ValueError("EPA operating fraction must be within 0 and 1")
    if not np.isfinite(x.gross_load_mw.dropna().to_numpy(dtype=float)).all():
        raise ValueError("Invalid EPA gross load")
    site = x[["facility_id", "timestamp_utc", "temperature_2m_c"]].drop_duplicates()
    if site.duplicated(["facility_id", "timestamp_utc"]).any():
        raise ValueError("Colocated EPA units disagree on weather")
    if not site.groupby("facility_id").size().eq(744).all():
        raise ValueError("Incomplete independent site-hour weather")
    x["heat_bin"] = pd.cut(x.temperature_2m_c, bins=BINS, labels=LABELS, right=False)
    site["heat_bin"] = pd.cut(site.temperature_2m_c, bins=BINS, labels=LABELS, right=False)
    if x.heat_bin.isna().any() or site.heat_bin.isna().any():
        raise ValueError("Unclassified temperatures")
    x["positive_operating"] = x.operating_time.gt(0)
    rows = []
    for (plant, unit, heat_bin), group in x.groupby(
        ["facility_id", "unit_id", "heat_bin"], observed=True
    ):
        running = group.loc[group.positive_operating]
        gross = running.gross_load_mw.dropna()
        rows.append({
            "facility_id": str(plant), "epa_unit_id": str(unit), "heat_bin": str(heat_bin),
            "source_hours": len(group),
            "reported_operating_fraction_hours": float(group.operating_time.sum()),
            "positive_operating_hours": int(group.positive_operating.sum()),
            "positive_operating_share": float(group.positive_operating.mean()),
            "gross_load_observed_given_operation": len(gross),
            "mean_gross_load_mw_given_operation": float(gross.mean()) if len(gross) else np.nan,
        })
    units = pd.DataFrame(rows).sort_values(["facility_id", "epa_unit_id", "heat_bin"])
    check = units.groupby(["facility_id", "epa_unit_id"]).source_hours.sum()
    if not check.eq(744).all() or len(check) != x.groupby(["facility_id", "unit_id"]).ngroups:
        raise AssertionError("Source hour conservation failed")
    weather = site.groupby(["facility_id", "heat_bin"], observed=True).agg(
        distinct_site_weather_hours=("timestamp_utc", "size")
    ).reset_index()
    if not weather.groupby("facility_id").distinct_site_weather_hours.sum().eq(744).all():
        raise AssertionError("Site-weather hour conservation failed")
    manifest = {
        "observed_local_july_hours_per_epa_unit": 744,
        "observed_distinct_weather_hours_per_site": 744,
        "temperature_edges_c": [35, 40],
        "weather_replication_across_colocated_units": True,
        "gross_load_conditioned_on_positive_operation": True,
        "dispatch_selection_adjusted": False,
        "statistical_significance_or_causal_derating_estimated": False,
        "unit_to_eia_generator_physical_mapping_established": False,
        "epa_gross_load_equals_eia_net_mw": False,
        "observed_outages_or_eens_estimated": False,
    }
    return units, weather, manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--panel", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    units, weather, manifest = summarize(pd.read_csv(args.panel,
        dtype={"facility_id": "string", "unit_id": "string"}))
    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)
    units.to_csv(root / "epa_744h_unit_heat_strata_descriptive.csv", index=False)
    weather.to_csv(root / "era5_744h_unique_site_heat_hours.csv", index=False)
    (root / "epa_744h_heat_strata_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(weather.to_string(index=False))
    print(units.to_string(index=False))


if __name__ == "__main__":
    main()
