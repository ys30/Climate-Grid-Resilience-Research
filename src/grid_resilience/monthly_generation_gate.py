"""Conservative gate for comparing full-calendar-month EIA-923 with PyPSA outputs.

Fail closed when hourly model records do not cover an entire UTC calendar
month. Actual EIA-923 data still require upstream plant/BA crosswalk audit.
"""
import argparse
import calendar
import json
from pathlib import Path
import pandas as pd

def monthly_generation(hourly_csv, output_dir):
    df = pd.read_csv(hourly_csv)
    required = {"timestamp", "ba", "technology", "generation_mwh"}
    if not required.issubset(df):
        raise ValueError(f"Missing {sorted(required-set(df))}")
    if df.empty or df[list(required)].isna().any().any():
        raise ValueError("Missing hourly generation data")
    df["timestamp"] = pd.to_datetime(df.timestamp, utc=True, errors="raise")
    if df.duplicated(["timestamp", "ba", "technology"]).any():
        raise ValueError("Duplicate technology-hour records")
    df["generation_mwh"] = pd.to_numeric(df.generation_mwh, errors="raise")
    if not df.generation_mwh.map(lambda x: -float("inf") < float(x) < float("inf")).all():
        raise ValueError("Nonfinite generation")
    df["period"] = df.timestamp.dt.strftime("%Y-%m")
    all_periods = sorted(df.period.unique())
    keys = df[["ba", "technology"]].drop_duplicates()
    rows = []
    for period in all_periods:
        year, month = map(int, period.split("-"))
        first = pd.Timestamp(year=year, month=month, day=1, tz="UTC")
        n_hours = calendar.monthrange(year, month)[1] * 24
        expected = pd.date_range(first, periods=n_hours, freq="h")
        sub = df[df.period == period]
        for row in keys.itertuples(index=False):
            block = sub[(sub.ba == row.ba) & (sub.technology == row.technology)]
            if len(block) != n_hours or set(block.timestamp) != set(expected):
                raise ValueError(
                    f"Incomplete calendar month {period} for {row.ba}/{row.technology}: "
                    f"{len(block)} of {n_hours} hourly records"
                )
            rows.append({"ba": row.ba, "technology": row.technology,
                         "period": period,
                         "generation_mwh": float(block.generation_mwh.sum())})
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).sort_values(["ba", "technology", "period"]).to_csv(
        out / "modeled_generation_full_months.csv", index=False
    )
    manifest = {"periods": all_periods, "full_month_utc_coverage": True,
                "historical_calibration_certified": False,
                "warning": "Calendar completeness does not validate EIA-923 BA mapping, "
                           "net/gross generation conventions or fleet coverage."}
    (out / "monthly_coverage_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly", required=True)
    p.add_argument("--output", required=True)
    a=p.parse_args()
    print(json.dumps(monthly_generation(a.hourly,a.output),indent=2))

if __name__=="__main__":
    main()
