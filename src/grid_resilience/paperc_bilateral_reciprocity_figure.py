"""Paper C supplemental original bilateral reciprocity source-quality figure.

Never treat missing reverse reporting as 0 MW. Never interpret a disparity
as a transmission thermal rating or energy actually lost.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

TARGET={"AZPS","BPAT","CISO","SRP"}


def select(detail, manifest):
    needed={"utc_hour_start","ba_a","ba_b","both_direction_values_present",
            "absolute_reciprocity_sum_mw"}
    if not needed.issubset(detail):
        raise ValueError("Missing official counterparty source columns")
    if (manifest.get("unordered_pair_hour_keys")!=6888 or
        manifest.get("pair_groups")!=41 or
        manifest.get("historical_eens_validated") is not False):
        raise ValueError("Unverified source pair-hour cohort")
    if len(detail)!=6888 or detail.duplicated(["utc_hour_start","ba_a","ba_b"]).any():
        raise ValueError("Pair-hour cohort missing or duplicated")
    detail=detail.copy()
    detail["both_direction_values_present"]=detail.both_direction_values_present.map(
        {True:True,False:False,"True":True,"False":False})
    if detail.both_direction_values_present.isna().any():
        raise ValueError("Invalid reciprocal reporting status")
    if detail.loc[~detail.both_direction_values_present,"absolute_reciprocity_sum_mw"].notna().any():
        raise ValueError("Missing counterpart was inappropriately set to zero")
    inside=detail.loc[detail.ba_a.isin(TARGET)&detail.ba_b.isin(TARGET)].copy()
    if inside.empty:
        raise ValueError("No internal BA source pairs")
    grouped=inside.groupby(["ba_a","ba_b"],sort=True)
    out=grouped.apply(lambda g:pd.Series({
        "pair_hours":len(g),
        "both_numeric_hours":int(g.both_direction_values_present.sum()),
        "missing_or_blank_direction_hours":int((~g.both_direction_values_present).sum()),
        "sum_absolute_reciprocal_discrepancy_mwh":float(
            g.absolute_reciprocity_sum_mw.sum(min_count=1))
            if g.both_direction_values_present.any() else np.nan,
        "reporting_is_physical_line_capacity":False
    }),include_groups=False).reset_index()
    if out.pair_hours.ne(168).any():
        raise ValueError("Unexpected internal pair hours")
    return out.sort_values(["ba_a","ba_b"]).reset_index(drop=True)


def render(table,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    folder=Path(out);folder.mkdir(parents=True,exist_ok=True)
    labels=[f"{a}–{b}" for a,b in zip(table.ba_a,table.ba_b)]
    x=np.arange(len(table))
    fig,(ax1,ax2)=plt.subplots(2,1,figsize=(8,6.6),layout="constrained")
    ax1.bar(x,table.sum_absolute_reciprocal_discrepancy_mwh/1000)
    ax1.set_ylabel("Absolute reciprocal difference\n(thousand MWh / 168 h)")
    ax1.set_title("A  Reciprocal source-report discrepancy",loc="left")
    ax2.bar(x,table.both_numeric_hours,label="Both directions numeric")
    ax2.bar(x,table.missing_or_blank_direction_hours,bottom=table.both_numeric_hours,
            label="One direction missing or blank")
    ax2.set_ylabel("Pair-hour reporting status (h)")
    ax2.set_title("B  Counterparty-hour evidence completeness",loc="left")
    ax2.legend(frameon=False,fontsize=8)
    ax2.set_ylim(0,178)
    for ax in (ax1,ax2):
        ax.set_xticks(x,labels)
        ax.grid(axis="y",alpha=.2)
        ax.set_axisbelow(True)
    fig.text(.5,-.025,"Original EIA-930 directed BA reporting; includes only paired reported values. "
             "Not transmission ratings, measured energy loss, or EENS.",
             ha="center",va="top",fontsize=8,wrap=True)
    for ext in ("png","pdf"):
        fig.savefig(folder/f"fig_paperc_bilateral_reciprocity_source_quality.{ext}",
                    dpi=230,bbox_inches="tight")
    plt.close(fig)
    table.to_csv(folder/"table_paperc_bilateral_reciprocity_source_quality.csv",index=False)


def main():
    p=argparse.ArgumentParser()
    for k in ("hourly","manifest","output"):
        p.add_argument("--"+k,required=True)
    a=p.parse_args()
    table=select(pd.read_csv(a.hourly),json.loads(Path(a.manifest).read_text()))
    render(table,a.output)
    print(table.to_string(index=False))


if __name__=="__main__":main()
