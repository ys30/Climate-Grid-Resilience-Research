"""Render explicitly modeled SRP hourly adequacy figures from validated CI tables.

Figures are descriptive scenario diagnostics, not historical outage estimates.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def render(hourly_csv: Path, diurnal_csv: Path, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    hourly = pd.read_csv(hourly_csv, parse_dates=["timestamp"])
    diurnal = pd.read_csv(diurnal_csv)
    expected_hourly = {"case", "timestamp", "demand_mw", "assumed_solar_availability_pu", "shortfall_mw"}
    expected_diurnal = {"case", "hour_utc", "shortfall_mwh", "mean_demand_mw",
                        "mean_assumed_solar_availability_pu"}
    if not expected_hourly.issubset(hourly) or not expected_diurnal.issubset(diurnal):
        raise ValueError("Missing required figure fields")
    if set(hourly.case) != set(diurnal.case):
        raise ValueError("Case mismatch between hourly and diurnal inputs")
    for case, part in hourly.groupby("case"):
        summary = diurnal.loc[diurnal.case.eq(case)]
        if len(part) != 168 or len(summary) != 24:
            raise ValueError(f"{case}: expected 168 and 24 rows")
        if summary.hour_utc.isna().any() or set(summary.hour_utc) != set(range(24)):
            raise ValueError(f"{case}: invalid or duplicate UTC hour-of-day bins")
        if part.timestamp.isna().any() or part.timestamp.duplicated().any():
            raise ValueError(f"{case}: missing or duplicate UTC timestamps")
        if not (part.timestamp.sort_values().diff().dropna() == pd.Timedelta(hours=1)).all():
            raise ValueError(f"{case}: nonconsecutive UTC hourly timestamps")

        if abs(float(part.shortfall_mw.sum()) - float(summary.shortfall_mwh.sum())) > 1e-4:
            raise ValueError(f"{case}: figure inputs disagree on shortage energy")
    out_dir.mkdir(parents=True, exist_ok=True)
    for case, part in hourly.groupby("case"):
        part = part.sort_values("timestamp")
        fig, ax = plt.subplots(figsize=(11, 4.2))
        ax.plot(part.timestamp, part.demand_mw, label="Demand input (MW)", linewidth=1.3)
        ax.set_ylabel("Demand (MW)")
        ax.set_xlabel("UTC timestamp")
        ax2 = ax.twinx()
        ax2.fill_between(part.timestamp, 0, part.shortfall_mw.to_numpy(),
                         alpha=0.3, label="Modeled shortfall (MW)")
        ax2.set_ylabel("Modeled shortfall (MW)")
        ax.set_title(f"SRP 168-hour adequacy diagnostic: {case}")
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(out_dir / f"{case}_hourly_shortfall.png", dpi=160)
        plt.close(fig)

        day = diurnal.loc[diurnal.case.eq(case)].sort_values("hour_utc")
        fig, ax = plt.subplots(figsize=(8.5, 4))
        ax.bar(day.hour_utc, day.shortfall_mwh, label="Modeled shortfall (MWh)")
        ax.set_xticks(range(0, 24, 2))
        ax.set_xlabel("Hour (UTC)")
        ax.set_ylabel("Total modeled shortfall over 168 h (MWh)")
        ax.set_title(f"SRP modeled shortfall by UTC hour: {case}")
        fig.tight_layout()
        fig.savefig(out_dir / f"{case}_diurnal_shortfall.png", dpi=160)
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hourly", type=Path, required=True)
    parser.add_argument("--diurnal", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    render(args.hourly, args.diurnal, args.output_dir)


if __name__ == "__main__":
    main()
