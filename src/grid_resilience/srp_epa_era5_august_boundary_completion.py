"""Strictly extend a verified July-only EPA/ERA5 panel with observed Aug-1 UTC ERA5.

This is a data-admission gate, not a temperature derating estimator. It will
never interpolate, backfill, infer missing source hours, or invent weather.
"""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
import numpy as np

SITES = {"141", "55129", "147"}
EXPECTED = pd.date_range("2024-08-01T00:00:00Z", periods=7, freq="h")


def complete_july_panel(july_panel, august_weather, provenance):
    """Return complete local-July hourly panel and provenance flags or fail closed."""
    x, w = july_panel.copy(), august_weather.copy()
    required = {"facility_id", "unit_id", "timestamp_utc",
                "era5_july_hour_matched", "temperature_2m_c"}
    w_required = {"plant_id", "timestamp_utc", "temperature_2m_c"}
    if not required.issubset(x.columns) or not w_required.issubset(w.columns):
        raise ValueError("Missing input source fields")
    if not isinstance(provenance, dict) or not provenance.get("source_url") or not provenance.get("sha256"):
        raise ValueError("Actual August ERA5 source provenance URL and SHA256 required")
    for df, idcol in ((x, "facility_id"), (w, "plant_id")):
        df[idcol] = df[idcol].astype("string").str.strip()
    x["unit_id"] = x.unit_id.astype("string").str.strip()
    x["timestamp_utc"] = pd.to_datetime(x.timestamp_utc, utc=True, errors="raise")
    w["timestamp_utc"] = pd.to_datetime(w.timestamp_utc, utc=True, errors="raise")
    x["temperature_2m_c"] = pd.to_numeric(x.temperature_2m_c, errors="coerce")
    w["temperature_2m_c"] = pd.to_numeric(w.temperature_2m_c, errors="coerce")
    if set(x.facility_id) != SITES or set(w.plant_id) != SITES:
        raise ValueError("Missing or extra target plants")
    if x[["facility_id", "unit_id"]].isna().any().any():
        raise ValueError("Missing EPA source identity")
    if x.duplicated(["facility_id", "unit_id", "timestamp_utc"]).any():
        raise ValueError("Duplicate EPA unit hour")
    if w.duplicated(["plant_id", "timestamp_utc"]).any():
        raise ValueError("Duplicate actual August site hour")
    for site, group in w.groupby("plant_id"):
        if not pd.DatetimeIndex(group.timestamp_utc.sort_values()).equals(EXPECTED):
            raise ValueError("August weather must contain precisely 00-06 UTC August 1")
    if not np.isfinite(w.temperature_2m_c.to_numpy(dtype=float)).all():
        raise ValueError("Incomplete or nonfinite observed August weather")
    if x.era5_july_hour_matched.dtype != bool or x.era5_july_hour_matched.isna().any():
        raise ValueError("Invalid July match flags")
    for (plant, unit), group in x.groupby(["facility_id", "unit_id"]):
        if len(group) != 744 or int(group.era5_july_hour_matched.sum()) != 737:
            raise ValueError("Unverified local-July source calendar")
        expected_full = pd.date_range("2024-07-01T07:00:00Z", periods=744, freq="h")
        if not pd.DatetimeIndex(group.timestamp_utc.sort_values()).equals(expected_full):
            raise ValueError("EPA local-July timestamp conservation failed")
        unmatched = group.loc[~group.era5_july_hour_matched]
        if not pd.DatetimeIndex(unmatched.timestamp_utc.sort_values()).equals(EXPECTED):
            raise ValueError("Unexpected EPA weather-missing boundary")
    if x.loc[x.era5_july_hour_matched, "temperature_2m_c"].isna().any():
        raise ValueError("Verified July matched weather is missing")
    if x.loc[~x.era5_july_hour_matched, "temperature_2m_c"].notna().any():
        raise ValueError("July missing boundary has already been filled")
    missing = x.loc[~x.era5_july_hour_matched, ["facility_id", "unit_id", "timestamp_utc"]]
    joined = missing.merge(w.rename(columns={"plant_id": "facility_id"}),
                           on=["facility_id", "timestamp_utc"],
                           how="left", validate="many_to_one", indicator=True)
    if not joined._merge.eq("both").all() or joined.temperature_2m_c.isna().any():
        raise ValueError("Actual August weather has not covered EPA boundary")
    y = x.merge(w.rename(columns={"plant_id": "facility_id", "temperature_2m_c": "august_observed_temp_c"}),
                on=["facility_id", "timestamp_utc"], how="left", validate="many_to_one")
    if y.loc[y.era5_july_hour_matched, "august_observed_temp_c"].notna().any():
        raise ValueError("August source overlaps July matched hours")
    y["era5_august_boundary_matched"] = ~y.era5_july_hour_matched
    y.loc[y.era5_august_boundary_matched, "temperature_2m_c"] = y.loc[
        y.era5_august_boundary_matched, "august_observed_temp_c"]
    y = y.drop(columns=["august_observed_temp_c"])
    y["era5_full_local_july_matched"] = y.temperature_2m_c.notna()
    if not y.era5_full_local_july_matched.all():
        raise AssertionError("Incomplete non-imputed July 744-hour panel")
    summary = y.groupby(["facility_id", "unit_id"], as_index=False).agg(
        source_local_july_hours=("timestamp_utc", "size"),
        jul_utc_source_matched=("era5_july_hour_matched", "sum"),
        aug_utc_observed_boundary_matched=("era5_august_boundary_matched", "sum"),
        complete_matched_hours=("era5_full_local_july_matched", "sum"))
    if not summary.aug_utc_observed_boundary_matched.eq(7).all():
        raise AssertionError("Boundary hours not conserved")
    manifest = {
        "actual_august_era5_source_url": provenance["source_url"],
        "actual_august_era5_sha256": provenance["sha256"],
        "july_source_hours_per_unit": 737,
        "august_boundary_source_hours_per_unit": 7,
        "complete_local_july_hours_per_unit": 744,
        "observed_august_source_required": True,
        "weather_interpolation_or_imputation_used": False,
        "epa_unit_is_verified_eia_generator": False,
        "gross_load_is_eia_net_mw": False,
        "thermal_derating_identified": False,
    }
    return y, summary, manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--july-panel", required=True)
    p.add_argument("--august-weather", required=True)
    p.add_argument("--august-source-url", required=True)
    p.add_argument("--august-sha256", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    path = Path(a.august_weather)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if a.august_sha256.lower() != actual:
        raise ValueError("Observed August ERA5 source SHA256 mismatch")
    y, s, m = complete_july_panel(
        pd.read_csv(a.july_panel),
        pd.read_csv(path),
        {"source_url": a.august_source_url, "sha256": actual})
    out = Path(a.output)
    out.mkdir(parents=True, exist_ok=True)
    y.to_csv(out / "epa_local_july_744h_observed_era5.csv", index=False)
    s.to_csv(out / "epa_local_july_744h_observed_summary.csv", index=False)
    (out / "epa_local_july_744h_source_manifest.json").write_text(json.dumps(m, indent=2) + "\n")


if __name__ == "__main__":
    main()
