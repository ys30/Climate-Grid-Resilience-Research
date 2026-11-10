"""Supplementary figure: original EIA-930 signed reporting arithmetic, not EENS.

Inputs MUST be the CI-verified hourly and summary tables from the same run.
Blanks are never converted to physical zeros. A missing cohort is hatched.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd


BAS = ("AZPS", "BPAT", "CISO", "SRP")
SEVEN = "net_minus_six_plus_other_mwh"
EIGHT = "net_minus_six_plus_other_petroleum_mwh"


def validate(hourly, summary):
    keys = ["ba", "utc_hour_start"]
    if not set(keys + [SEVEN, EIGHT, "seven_numeric", "eight_numeric"]).issubset(hourly):
        raise ValueError("Required hourly source columns absent")
    if hourly.duplicated(keys).any():
        raise ValueError("Duplicate BA-hour evidence")
    times = pd.to_datetime(hourly.utc_hour_start, utc=True)
    hourly = hourly.copy()
    hourly["utc_hour_start"] = times
    expected = pd.date_range("2024-07-01T07:00:00Z", periods=161, freq="h")
    for ba in BAS:
        x = hourly[hourly.ba.eq(ba)].sort_values("utc_hour_start")
        if len(x) != 161 or not x.utc_hour_start.reset_index(drop=True).equals(pd.Series(expected, name="utc_hour_start")):
            raise ValueError("Original 161-hour source keys incomplete")
    if len(hourly) != 644 or set(hourly.ba) != set(BAS):
        raise ValueError("Original four-BA cohort missing")
    s = summary.set_index("ba")
    if set(s.index) != set(BAS):
        raise ValueError("Summary BA cohort mismatch")
    for ba in BAS:
        x = hourly.loc[hourly.ba.eq(ba)]
        for label, field in [("seven", SEVEN), ("eight", EIGHT)]:
            reported = x[f"{label}_numeric"].astype(str).str.lower().map({"true":True,"false":False})
            if reported.isna().any() or not x[field].notna().equals(reported):
                raise ValueError("Reported mask and original source nulls differ")
            if int(reported.sum()) != int(s.loc[ba, f"{label}_numeric_hours"]):
                raise ValueError("Summary numeric hour count disagrees")
            signed = x[field].sum(min_count=1)
            absolute = x[field].abs().sum(min_count=1)
            for actual, name in [(signed, f"signed_{label}_difference_mwh"),
                                 (absolute, f"abs_{label}_difference_mwh")]:
                ref = s.loc[ba, name]
                if not (pd.isna(actual) and pd.isna(ref)) and not np.isclose(actual, ref, atol=1e-6):
                    raise ValueError(f"Summary mismatch for {ba}: {name}")
    return hourly


def draw(hourly, summary, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    data = validate(hourly, summary)
    s = summary.set_index("ba")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.3, 7.2),
                                    gridspec_kw={"height_ratios": [1, 1.25]})
    colors = {"seven": "#527f9a", "eight": "#ba744f"}
    width = 0.32
    positions = np.arange(len(BAS))
    for j, (label, col) in enumerate([("seven", SEVEN), ("eight", EIGHT)]):
        for k, ba in enumerate(BAS):
            val = s.loc[ba, f"abs_{label}_difference_mwh"]
            xpos = positions[k] + (j - 0.5) * width
            if pd.isna(val):
                ax1.bar(xpos, 0.001, width, color="white", edgecolor="#777777", hatch="///")
                ax1.text(xpos, 0.85, "N/A", ha="center", va="bottom", fontsize=8)
            else:
                ax1.bar(xpos, val, width, color=colors[label], label=None)
                ax1.annotate(f"{val:,.0f}", (xpos, val), xytext=(0, 3),
                             textcoords="offset points", ha="center", fontsize=8)
    ax1.set_xticks(positions, BAS)
    ax1.set_ylabel("Sum of absolute hourly differences (MWh)")
    ax1.set_title("A  |  Source-reported 7/8-category arithmetic")
    ax1.set_ylim(0, 12500)
    ax1.grid(axis="y", alpha=0.2)
    ax1.set_axisbelow(True)
    ax1.legend(handles=[Patch(color=colors["seven"], label="Six + Other"),
                        Patch(color=colors["eight"], label="Six + Other + Petroleum"),
                        Patch(facecolor="white", edgecolor="#777", hatch="///", label="Original fields missing")],
               loc="upper right", fontsize=8, frameon=False)
    ciso = data.loc[data.ba.eq("CISO")].sort_values("utc_hour_start")
    ax2.plot(np.arange(161), ciso[EIGHT].to_numpy(), color="#ba744f",
             lw=1.2, marker=".", markersize=3)
    ax2.axhline(0, color="#444444", lw=0.8)
    ax2.set_xlabel("Hour index within original modern-taxonomy cohort (0–160)")
    ax2.set_ylabel("CISO net − eight-category reported sum (MWh)")
    ax2.set_title("B  |  CISO signed original hourly residual (161 hours)")
    ax2.grid(alpha=0.2)
    fig.text(0.01, 0.012, "Source: original EIA-930 July 2024 (Jul–Dec taxonomy), 4 BAs × 161 UTC hours.\n"
             "Reported-category accounting only; missing ≠ zero. Not physical generator availability, outages or EENS.",
             fontsize=8, va="bottom")
    fig.tight_layout(rect=(0, 0.065, 1, 1), h_pad=2)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out/"paper_c_original_fuel_reconciliation_supplement.png", dpi=250)
    fig.savefig(out/"paper_c_original_fuel_reconciliation_supplement.pdf")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hourly", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    draw(pd.read_csv(args.hourly), pd.read_csv(args.summary), args.output)


if __name__ == "__main__":
    main()
