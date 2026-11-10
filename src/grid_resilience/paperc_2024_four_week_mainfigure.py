"""Paper C Fig. 2: July 2024 four-week matched factorial screening results.

Strictly recompute factorial second differences from archived solver outputs.
Conditional, partial-fleet, hypothetical-links scenarios; NOT actual EENS.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from grid_resilience.july2024_four_week_factorial_replication import summarize

EVENTS = tuple(f"JULY2024_WEEK_{i}" for i in range(1, 5))
BAS = ("AZPS", "BPAT", "CISO", "SRP")
VARIANTS = ("isolated", "links_10pct")
SCENARIOS = ("baseline", "heat_only", "wind_only", "heat_wind")
REQUIRED_META = {
    "distinct_real_july_weeks": 4,
    "source_distinct_hours": 672,
    "same_partial_eia860_annual_capacity_all_events": True,
    "same_hypothetical_intertie_rating_all_events": True,
    "same_assumed_heat_load_wind_response_all_events": True,
    "real_historical_generator_availability_calibrated": False,
    "physical_intertie_ratings_verified": False,
    "modeled_shortage_is_observed_eens": False,
    "intra_july_consecutive_weeks_independent_weather_events_assumed": False,
}


def prepare(dispatch, reported_by_ba, reported_contrast, scope):
    for key, expected in REQUIRED_META.items():
        if scope.get(key) is not expected and scope.get(key) != expected:
            raise ValueError(f"Source scope gate failed: {key}")
    required = {"event_id", "network_variant", "ba", "scenario",
                "unserved_energy_mwh", "shortage_hours", "peak_shortfall_mw"}
    if not required.issubset(dispatch):
        raise ValueError("Missing original solver output columns")
    if set(dispatch.event_id) != set(EVENTS) or set(dispatch.ba) != set(BAS):
        raise ValueError("Unexpected event or BA cohort")
    if set(dispatch.network_variant) != set(VARIANTS) or set(dispatch.scenario) != set(SCENARIOS):
        raise ValueError("Unexpected scenario or network configuration")
    independent, contrasts = summarize(dispatch)
    key = ["event_id", "network_variant", "ba"]
    measures = ["baseline_shortage_mwh", "heat_only_shortage_mwh",
                "wind_only_shortage_mwh", "compound_shortage_mwh",
                "modeled_factorial_interaction_mwh"]
    if reported_by_ba.duplicated(key).any() or len(reported_by_ba) != 40:
        raise ValueError("Reported model summary has duplicate/missing keys")
    joined = independent.merge(reported_by_ba, on=key, how="outer",
                               validate="one_to_one", suffixes=("_computed", "_archive"), indicator=True)
    if len(joined) != 40 or not joined._merge.eq("both").all():
        raise ValueError("Original BA factorial summary cohort mismatch")
    for col in measures:
        a = joined[f"{col}_computed"].to_numpy(dtype=float)
        b = joined[f"{col}_archive"].to_numpy(dtype=float)
        if not np.isfinite(a).all() or not np.isfinite(b).all() or not np.allclose(a, b, atol=1e-6, rtol=1e-10):
            raise ValueError(f"Original solver and archived summary disagree: {col}")
    if reported_contrast.duplicated(["event_id"]).any() or set(reported_contrast.event_id) != set(EVENTS):
        raise ValueError("Four original-week contrasts not unique")
    check = contrasts.merge(reported_contrast, on="event_id", how="outer", validate="one_to_one",
                            suffixes=("_computed", "_archive"), indicator=True)
    if len(check) != 4 or not check._merge.eq("both").all():
        raise ValueError("Original contrasts have missing week")
    for col in ["isolated", "links_10pct", "links_minus_isolated_interaction_mwh"]:
        if not np.allclose(check[f"{col}_computed"], check[f"{col}_archive"], atol=1e-6, rtol=1e-10):
            raise ValueError(f"Original system interaction mismatch: {col}")
    independent["week"] = independent.event_id.map({name: i + 1 for i, name in enumerate(EVENTS)})
    independent = independent.sort_values(["week", "network_variant", "ba"]).reset_index(drop=True)
    return independent, contrasts.sort_values("event_id").reset_index(drop=True)


def draw(independent, contrasts, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    colors = {"isolated": "#527f9a", "links_10pct": "#bb7455"}
    fig = plt.figure(figsize=(9.4, 8.7), layout="constrained")
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 1.2, 0.22])
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0])]
    foot = fig.add_subplot(gs[2, 0])
    foot.axis("off")
    pos = np.arange(4)
    for delta, variant in [(-0.19, "isolated"), (+0.19, "links_10pct")]:
        vals = contrasts[variant].to_numpy(dtype=float) / 1000
        axes[0].bar(pos + delta, vals, width=0.36, color=colors[variant])
        for p, value in zip(pos + delta, vals):
            axes[0].text(p, value + 0.3, f"{value:.1f}", ha="center", fontsize=8)
    axes[0].set_xticks(pos, [f"Jul {1 + 7 * i}–{7 + 7 * i}" for i in range(4)])
    axes[0].set_ylabel("System factorial second difference (10³ MWh)")
    axes[0].set_title("A  |  Frozen partial fleet, two assumed network variants")
    axes[0].legend(handles=[Patch(color=colors["isolated"], label="Isolated BAs"),
                            Patch(color=colors["links_10pct"], label="Illustrative frozen 10%-peak links")],
                   frameon=False, fontsize=9)
    axes[0].grid(axis="y", alpha=0.2)
    axes[0].set_axisbelow(True)

    sub = independent[(independent.ba != "SYSTEM") &
                      (independent.network_variant == "links_10pct")].copy()
    width = 0.19
    cmap = {"AZPS": "#4d8a89", "BPAT": "#bc7955", "CISO": "#576fa3", "SRP": "#999054"}
    for j, ba in enumerate(BAS):
        subba = sub[sub.ba.eq(ba)].sort_values("week")
        if len(subba) != 4:
            raise ValueError(f"Missing original BA week: {ba}")
        v = subba.modeled_factorial_interaction_mwh.to_numpy(float) / 1000
        axes[1].bar(pos + (j - 1.5) * width, v, width=width * 0.92, label=ba, color=cmap[ba])
    axes[1].axhline(0, color="#303030", lw=0.8)
    axes[1].set_xticks(pos, [f"W{i}" for i in range(1, 5)])
    axes[1].set_ylabel("BA factorial second difference (10³ MWh)")
    axes[1].set_xlabel("Consecutive 168-hour windows, 1–28 July 2024 (UTC)")
    axes[1].set_title("B  |  Local heterogeneity under identical illustrative link ratings")
    axes[1].legend(ncol=4, frameon=False, fontsize=9, loc="upper center")
    axes[1].grid(axis="y", alpha=0.2)
    axes[1].set_axisbelow(True)
    foot.text(0.0, 0.65,
             "I = U(heat + wind) − U(heat) − U(wind) + U(baseline). U is modeled unserved energy.\n"
             "Partial 2024 EIA860 capacity and hypothetical links; four adjacent weeks are NOT independent events.\n"
             "Not measured power shortages, actual outages, or probabilistic EENS.",
             fontsize=8, va="bottom")
    fig.savefig(out / "paper_c_july2024_four_week_factorial_main.png", dpi=250)
    fig.savefig(out / "paper_c_july2024_four_week_factorial_main.pdf")
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dispatch", required=True)
    p.add_argument("--by-ba", required=True)
    p.add_argument("--contrast", required=True)
    p.add_argument("--scope", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    with open(args.scope, encoding="utf-8") as f:
        scope = json.load(f)
    source, totals = prepare(pd.read_csv(args.dispatch), pd.read_csv(args.by_ba),
                             pd.read_csv(args.contrast), scope)
    draw(source, totals, args.output)
    print("RECOMPUTED ORIGINAL FOUR-WEEK CONTRAST")
    print(totals.to_string(index=False))


if __name__ == "__main__":
    main()
