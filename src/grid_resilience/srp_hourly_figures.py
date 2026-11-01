"""Prepare validated figure-ready SRP hourly context tables (modeled, not observed outages)."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

REQUIRED = {"case", "timestamp", "demand_mw", "assumed_solar_availability_pu", "shortfall_mw"}


def prepare(data: pd.DataFrame, expected_hours: int = 168) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing = REQUIRED - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    df = data.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="raise")
    if df.empty or df[list(REQUIRED)].isna().any().any():
        raise ValueError("Empty or missing context values")
    if df.duplicated(["case", "timestamp"]).any():
        raise ValueError("Duplicate case-timestamp keys")
    for col in ("demand_mw", "assumed_solar_availability_pu", "shortfall_mw"):
        df[col] = pd.to_numeric(df[col], errors="raise")
        if not df[col].map(lambda x: float("-inf") < float(x) < float("inf")).all():
            raise ValueError(f"Nonfinite {col}")
    if (df[["demand_mw", "shortfall_mw"]] < -1e-8).any().any():
        raise ValueError("Negative demand or shortfall")
    if not df.assumed_solar_availability_pu.between(0, 1).all():
        raise ValueError("Solar proxy outside [0,1]")
    df = df.sort_values(["case", "timestamp"]).reset_index(drop=True)
    frames = []
    for case, group in df.groupby("case", sort=True):
        if len(group) != expected_hours:
            raise ValueError(f"{case}: expected {expected_hours} hours, got {len(group)}")
        if not (group.timestamp.diff().dropna() == pd.Timedelta(hours=1)).all():
            raise ValueError(f"{case}: nonconsecutive hours")
        frame = group.copy()
        frame["hour_utc"] = frame.timestamp.dt.hour
        frame["demand_high_p75"] = frame.demand_mw >= float(frame.demand_mw.quantile(0.75))
        frame["solar_proxy_zero"] = frame.assumed_solar_availability_pu < 1e-8
        frame["shortfall_hour"] = frame.shortfall_mw > 1e-5
        frames.append(frame)
    hourly = pd.concat(frames, ignore_index=True)
    rows = []
    for (case, hour), group in hourly.groupby(["case", "hour_utc"], sort=True):
        rows.append({
            "case": case, "hour_utc": hour, "hours_in_bin": len(group),
            "mean_demand_mw": float(group.demand_mw.mean()),
            "mean_assumed_solar_availability_pu": float(group.assumed_solar_availability_pu.mean()),
            "shortfall_mwh": float(group.shortfall_mw.sum()),
            "shortfall_hours": int(group.shortfall_hour.sum()),
            "high_load_hours": int(group.demand_high_p75.sum()),
            "zero_solar_proxy_hours": int(group.solar_proxy_zero.sum()),
        })
    diurnal = pd.DataFrame(rows)
    check = diurnal.groupby("case").shortfall_mwh.sum()
    truth = hourly.groupby("case").shortfall_mw.sum()
    if not ((check - truth).abs() < 1e-5).all():
        raise AssertionError("Hour-of-day energy conservation failed")
    return hourly, diurnal


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    hourly, diurnal = prepare(pd.read_csv(args.input))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    hourly.to_csv(args.output_dir / "srp_hourly_figure_data.csv", index=False)
    diurnal.to_csv(args.output_dir / "srp_diurnal_figure_data.csv", index=False)
    print(f"Validated {hourly.case.nunique()} cases, {len(hourly)} hourly records")


if __name__ == "__main__":
    main()
