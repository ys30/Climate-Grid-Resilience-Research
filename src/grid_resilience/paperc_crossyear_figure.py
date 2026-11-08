"""Paper C cross-year conditional-model figure; no physical adequacy claims."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def summarize(source, source_gate, heat_gate):
    required={"network_variant","july2023_interaction_model_mwh",
              "july2024_interaction_model_mwh","july2023_baseline_model_gap_mwh",
              "july2024_baseline_model_gap_mwh","frozen_2024_partial_fleet_used_in_2023",
              "real_grid_calibration","historical_eens"}
    if not required.issubset(source.columns) or len(source)!=2:
        raise ValueError("Incomplete cross-year source-model results")
    if set(source.network_variant)!={"isolated","links_10pct"} or source.network_variant.duplicated().any():
        raise ValueError("Invalid comparison variants")
    if (not source.frozen_2024_partial_fleet_used_in_2023.eq(True).all()
            or not source.real_grid_calibration.eq(False).all()
            or not source.historical_eens.eq(False).all()):
        raise ValueError("Historical fleet or EENS misrepresented")
    if not (source_gate.get("cross_period_holdout_source_admitted") is True
            and source_gate.get("different_calendar_year_candidate_available") is True
            and source_gate.get("source_supported_physical_grid_adequacy") is False
            and source_gate.get("capacity_is_2024_partial_fleet_held_fixed_on_2023_not_true_2023_fleet") is True):
        raise ValueError("Cross-year source or capacity provenance not admitted")
    if (heat_gate.get("heat_load_response_active_ba_hours",0)<=0
            or heat_gate.get("total_four_ba_hours")!=672
            or heat_gate.get("measured_grid_heat_response") is not False):
        raise ValueError("Heat activation not independently evidenced")
    cols=[c for c in required if c.endswith("_mwh")]
    for c in cols:
        z=pd.to_numeric(source[c],errors="coerce")
        if not np.isfinite(z).all():
            raise ValueError("Nonfinite model comparison")
        if "baseline" in c and z.lt(0).any():
            raise ValueError("Negative baseline modeled shortfall")
    return source.sort_values("network_variant").reset_index(drop=True)


def figure(table, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dest=Path(out);dest.mkdir(parents=True,exist_ok=True)
    x=np.arange(2)
    fig,ax=plt.subplots(figsize=(7.4,4.8),layout="constrained")
    for idx,(year,col) in enumerate([
            ("2023 Jul 10–16","july2023_interaction_model_mwh"),
            ("2024 Jul 1–7","july2024_interaction_model_mwh")]):
        v=table[col].to_numpy()/1000
        shift=(-.19 if idx==0 else .19)
        ax.bar(x+shift,v,width=.36,label=year)
        for xx,yy in zip(x+shift,v):
            ax.annotate(f"{yy:.2f}",(xx,yy),xytext=(0,3),textcoords="offset points",
                        ha="center",fontsize=8)
    ax.set_xticks(x,["Isolated BAs","Illustrative fixed links"])
    ax.set_ylabel("Modeled heat–wind second difference (thousand MWh / 168 h)")
    ax.set_title("Cross-year summer source-input sensitivity",loc="left")
    ax.legend(frameon=False)
    ax.grid(axis="y",alpha=.2)
    ax.set_axisbelow(True)
    fig.text(.5,-.02,
        "Actual EIA-930 + ERA5 input periods; frozen 2024 partial fleet and hypothetical links. "
        "Not historical EENS, outages, or observed grid response.",
        ha="center",va="top",fontsize=8,wrap=True)
    for ext in ("png","pdf"):
        fig.savefig(dest/f"fig_paperc_2023_2024_crossyear_model_comparison.{ext}",
                    dpi=220,bbox_inches="tight")
    plt.close(fig)
    table.to_csv(dest/"table_paperc_2023_2024_crossyear_model_comparison.csv",index=False)


def main():
    p=argparse.ArgumentParser()
    for key in ("comparison","source-gate","heat-gate","output"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    t=summarize(pd.read_csv(a.comparison),
                json.loads(Path(a.source_gate).read_text()),
                json.loads(Path(a.heat_gate).read_text()))
    figure(t,a.output)
    print(t.to_string(index=False))


if __name__=="__main__":
    main()
