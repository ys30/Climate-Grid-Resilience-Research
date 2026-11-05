"""Join observed SRP BA demand to EPA/ERA5 site weather on exact UTC hour.

EIA-930 is balancing-authority aggregate demand, not generation dispatch
at the sampled plants. Only UTC July source observations are in scope;
the seven UTC-August hours of EPA local-July remain unmatched to EIA demand.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

PLANTS = {"141", "55129", "147"}
JULY = pd.date_range("2024-07-01T00:00:00Z", periods=744, freq="h")
EPA_JULY = pd.date_range("2024-07-01T07:00:00Z", periods=744, freq="h")
BINS = [-np.inf, 35.0, 40.0, np.inf]
LABELS = ["below_35_c", "35_to_below_40_c", "at_least_40_c"]


def summarize(epa_panel, eia_balance):
    needed = {"facility_id", "unit_id", "timestamp_utc",
              "temperature_2m_c", "era5_full_local_july_matched"}
    eia_needed = {"UTC Time at End of Hour", "Balancing Authority",
                  "Demand (MW)"}
    if not needed.issubset(epa_panel.columns) or not eia_needed.issubset(eia_balance.columns):
        raise ValueError("Missing verified EPA ERA5 or EIA930 fields")
    x, e = epa_panel.copy(), eia_balance.copy()
    x["facility_id"] = x.facility_id.astype("string").str.strip()
    x["unit_id"] = x.unit_id.astype("string").str.strip()
    x["timestamp_utc"] = pd.to_datetime(x.timestamp_utc, utc=True, errors="raise")
    x["temperature_2m_c"] = pd.to_numeric(x.temperature_2m_c, errors="coerce")
    if set(x.facility_id) != PLANTS:
        raise ValueError("Unexpected EPA plant set")
    if x.duplicated(["facility_id", "unit_id", "timestamp_utc"]).any():
        raise ValueError("Duplicate EPA unit UTC hour")
    if x.era5_full_local_july_matched.dtype != bool or not x.era5_full_local_july_matched.all():
        raise ValueError("Not a certified full 744-hour EPA ERA5 panel")
    for (plant, unit), g in x.groupby(["facility_id", "unit_id"]):
        if not pd.DatetimeIndex(g.timestamp_utc.sort_values()).equals(EPA_JULY):
            raise ValueError("Incomplete EPA local-July calendar")
    weather = x[["facility_id", "timestamp_utc", "temperature_2m_c"]].drop_duplicates()
    if weather.duplicated(["facility_id", "timestamp_utc"]).any():
        raise ValueError("Colocated EPA units disagree on temperature")
    if not weather.groupby("facility_id").size().eq(744).all():
        raise ValueError("Incomplete site hourly weather")
    if not np.isfinite(weather.temperature_2m_c.to_numpy(dtype=float)).all():
        raise ValueError("Invalid observed weather")
    e = e.loc[e["Balancing Authority"].astype("string").str.strip().eq("SRP")].copy()
    e["timestamp_utc"] = pd.to_datetime(
        e["UTC Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p",
        utc=True, errors="raise") - pd.Timedelta(hours=1)
    e = e.loc[e.timestamp_utc.isin(JULY)].copy()
    if len(e) != 744 or e.timestamp_utc.duplicated().any():
        raise ValueError("Incomplete or duplicate official SRP July EIA930 hours")
    if not pd.DatetimeIndex(e.timestamp_utc.sort_values()).equals(JULY):
        raise ValueError("Incomplete official SRP source time grid")
    e["srp_demand_mw"] = pd.to_numeric(e["Demand (MW)"], errors="coerce")
    if not np.isfinite(e.srp_demand_mw.to_numpy(dtype=float)).all() or e.srp_demand_mw.lt(0).any():
        raise ValueError("Missing or invalid official SRP demand")
    joined = weather.merge(e[["timestamp_utc", "srp_demand_mw"]],
                           on="timestamp_utc", how="left", validate="many_to_one",
                           indicator=True)
    joined["srp_demand_source_matched"] = joined._merge.eq("both")
    joined = joined.drop(columns="_merge")
    observed = joined.loc[joined.srp_demand_source_matched].copy()
    unmatched = joined.loc[~joined.srp_demand_source_matched].copy()
    expected_overlap = JULY[7:]
    for plant, g in observed.groupby("facility_id"):
        if not pd.DatetimeIndex(g.timestamp_utc.sort_values()).equals(expected_overlap):
            raise ValueError("SRP demand and local July EPA July UTC overlap differs")
    expected_aug = pd.date_range("2024-08-01T00:00:00Z", periods=7, freq="h")
    for plant, g in unmatched.groupby("facility_id"):
        if not pd.DatetimeIndex(g.timestamp_utc.sort_values()).equals(expected_aug):
            raise ValueError("Unmatched EIA930 source hours not exact August boundary")
    if observed.srp_demand_mw.isna().any() or unmatched.srp_demand_mw.notna().any():
        raise ValueError("EIA source intersection missing or silently filled")
    observed["heat_bin"] = pd.cut(observed.temperature_2m_c,
                                  bins=BINS, labels=LABELS, right=False)
    result = observed.groupby(["facility_id", "heat_bin"], observed=True).agg(
        unique_site_weather_hours=("timestamp_utc", "size"),
        mean_srp_ba_demand_mw=("srp_demand_mw", "mean"),
        median_srp_ba_demand_mw=("srp_demand_mw", "median"),
        min_srp_ba_demand_mw=("srp_demand_mw", "min"),
        max_srp_ba_demand_mw=("srp_demand_mw", "max")).reset_index()
    if not result.groupby("facility_id").unique_site_weather_hours.sum().eq(737).all():
        raise AssertionError("No site-hour conservation")
    manifest = {
        "eia930_source": "official 2024 July H1/H2 merged EIA930 BALANCE source",
        "eia930_time_convention": "UTC Time at End of Hour minus one hour",
        "epa_local_standard_time_to_utc_applied_upstream": True,
        "epa_source_site_weather_hours_per_plant": 744,
        "eia930_july_utc_matched_hours_per_plant": 737,
        "utc_august_boundary_hours_per_plant_unmatched_to_july_eia930": 7,
        "site_weather_sample_is_independent_per_epa_unit": False,
        "eia930_srp_demand_is_plant_dispatch": False,
        "srp_ba_demand_attribution_to_all_plants_proven": False,
        "dispatch_or_outage_causal_control_estimated": False,
        "thermal_derating_calibrated": False,
    }
    return joined, result, manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epa-era5-panel", required=True)
    parser.add_argument("--eia930-july", required=True)
    parser.add_argument("--output", required=True)
    a = parser.parse_args()
    joined, result, manifest = summarize(
        pd.read_csv(a.epa_era5_panel, dtype={"facility_id": "string", "unit_id": "string"}),
        pd.read_csv(a.eia930_july, dtype="string"))
    root = Path(a.output)
    root.mkdir(parents=True, exist_ok=True)
    joined.to_csv(root / "srp_demand_era5_site_hour_intersection.csv", index=False)
    result.to_csv(root / "srp_demand_by_site_era5_heat_bin_descriptive.csv", index=False)
    (root / "srp_demand_era5_site_hour_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
