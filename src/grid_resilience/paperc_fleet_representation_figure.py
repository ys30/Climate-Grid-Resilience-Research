"""Journal-ready model sensitivity figure: cross-year climate interaction vs fleet representation.

Never promotes nameplate candidate scenarios into calibrated historical reliability.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def compare_models(frozen, annual):
    need_f={"network_variant","july2023_interaction_model_mwh","july2024_interaction_model_mwh",
            "frozen_2024_partial_fleet_used_in_2023","real_grid_calibration","historical_eens"}
    need_a={"source_year","variant","interaction_model_mwh","year_specific_eia860_nameplate_used",
            "all_historical_generation_fleet_calibrated","historical_eens_or_outages_identified"}
    if not need_f.issubset(frozen) or not need_a.issubset(annual):
        raise ValueError("Required verified model columns missing")
    variants={"isolated","links_10pct"}
    if len(frozen)!=2 or set(frozen.network_variant)!=variants or frozen.network_variant.duplicated().any():
        raise ValueError("Incomplete frozen capacity model")
    if (len(annual)!=4 or annual.duplicated(["source_year","variant"]).any()
            or set(zip(annual.source_year,annual.variant))!={(y,v) for y in (2023,2024) for v in variants}):
        raise ValueError("Incomplete annual nameplate model")
    if (not frozen.frozen_2024_partial_fleet_used_in_2023.eq(True).all()
            or not frozen.real_grid_calibration.eq(False).all()
            or not frozen.historical_eens.eq(False).all()
            or not annual.year_specific_eia860_nameplate_used.eq(True).all()
            or not annual.all_historical_generation_fleet_calibrated.eq(False).all()
            or not annual.historical_eens_or_outages_identified.eq(False).all()):
        raise ValueError("Calibrated dispatch or provenance claim not supported")
    rows=[]
    for year in (2023,2024):
        for variant in ("isolated","links_10pct"):
            a=annual[(annual.source_year==year)&(annual.variant==variant)].iloc[0]
            b=frozen[frozen.network_variant==variant].iloc[0]
            key=f"july{year}_interaction_model_mwh"
            rows.append({"year":year,"network_variant":variant,
                         "frozen_proxy_model_interaction_mwh":float(b[key]),
                         "annual_nameplate_model_interaction_mwh":float(a.interaction_model_mwh),
                         "scenario_difference_mwh":float(a.interaction_model_mwh-b[key]),
                         "model_only_not_historical_eens":True})
    out=pd.DataFrame(rows)
    if not np.isfinite(out.select_dtypes("number").to_numpy()).all():
        raise ValueError("Nonfinite source-model result")
    return out


def render(t,output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dest=Path(output);dest.mkdir(parents=True,exist_ok=True)
    labels=[f"{int(r.year)}\n"+("Isolated" if r.network_variant=="isolated" else "Illustrative links")
            for r in t.itertuples()]
    x=np.arange(len(t))
    fig,ax=plt.subplots(figsize=(8.0,4.6),layout="constrained")
    ax.bar(x-.19,t.frozen_proxy_model_interaction_mwh/1000,width=.37,
           label="Frozen 2024 generic partial-fleet proxy")
    ax.bar(x+.19,t.annual_nameplate_model_interaction_mwh/1000,width=.37,
           label="Annual EIA-860 gas/wind nameplate candidate")
    ax.set_xticks(x,labels)
    ax.set_ylabel("Modeled heat–wind second difference (thousand MWh / 168 h)")
    ax.set_title("Sensitivity to annual generation-fleet representation",loc="left")
    ax.legend(fontsize=8,frameon=False,loc="upper left")
    ax.grid(axis="y",alpha=.2)
    ax.set_axisbelow(True)
    fig.text(.5,-.02,"Both fleets incomplete; annual nameplate is NOT hourly firm capacity. "
        "Transfers hypothetical. No observed EENS or blackout validation.",
        ha="center",va="top",fontsize=8,wrap=True)
    for ext in ("png","pdf"):
        fig.savefig(dest/f"fig_paperc_fleet_representation_sensitivity.{ext}",
                    dpi=220,bbox_inches="tight")
    plt.close(fig)
    t.to_csv(dest/"table_paperc_fleet_representation_sensitivity.csv",index=False)


def main():
    p=argparse.ArgumentParser()
    for arg in ("frozen","annual","output"):p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    t=compare_models(pd.read_csv(a.frozen),pd.read_csv(a.annual))
    render(t,a.output)
    print(t.to_string(index=False))


if __name__=="__main__":
    main()
