"""Diagnose EIA-930 directed reciprocal reporting by UTC day, hour and source half.

Derived solely from the 6,888 authenticated pair-hour rows, with explicit
missing directions. Descriptive reporting differences are not line losses,
transfer capabilities, or historical unserved energy.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

PAIRS=(("BPAT","GRID"),("BPAT","SCL"),("AZPS","CISO"),("AZPS","SRP"),
       ("CISO","SRP"),("BPAT","CISO"))
START=pd.Timestamp("2024-07-01T00:00:00Z")
HOURS=pd.date_range(START,periods=168,freq="h")


def analyze(hourly,manifest):
    required={"utc_hour_start","ba_a","ba_b","both_direction_values_present",
              "signed_reciprocity_sum_mw","absolute_reciprocity_sum_mw"}
    if not required.issubset(hourly):
        raise ValueError("Source pair-hour columns unavailable")
    if (manifest.get("unordered_pair_hour_keys")!=6888 or
        manifest.get("pair_groups")!=41 or
        manifest.get("historical_eens_validated") is not False or
        manifest.get("missing_direction_never_converted_to_zero") is not True):
        raise ValueError("Source provenance or scope gate failed")
    if len(hourly)!=6888:
        raise ValueError("Expected original authenticated 6,888 pair-hour observations")
    x=hourly.copy()
    x["utc_hour_start"]=pd.to_datetime(x.utc_hour_start,utc=True,errors="raise")
    if x.duplicated(["utc_hour_start","ba_a","ba_b"]).any():
        raise ValueError("Duplicate official pair-hour source")
    x["both_direction_values_present"]=x.both_direction_values_present.map(
        {True:True,False:False,"True":True,"False":False})
    if x.both_direction_values_present.isna().any():
        raise ValueError("Invalid direction completeness flag")
    for col in ("signed_reciprocity_sum_mw","absolute_reciprocity_sum_mw"):
        x[col]=pd.to_numeric(x[col],errors="coerce")
    missing=x.loc[~x.both_direction_values_present]
    if missing[["signed_reciprocity_sum_mw","absolute_reciprocity_sum_mw"]].notna().any().any():
        raise ValueError("Missing bilateral direction must not become zero residual")
    complete=x.loc[x.both_direction_values_present]
    if not np.isfinite(complete[["signed_reciprocity_sum_mw","absolute_reciprocity_sum_mw"]]).all().all():
        raise ValueError("Complete pairs need finite reporting values")
    if not np.allclose(complete.signed_reciprocity_sum_mw.abs(),
                       complete.absolute_reciprocity_sum_mw,atol=1e-6,rtol=0):
        raise ValueError("Signed and absolute reporting discrepancies disagree")
    chosen=x.loc[pd.MultiIndex.from_frame(x[["ba_a","ba_b"]]).isin(PAIRS)].copy()
    if len(chosen)!=168*len(PAIRS):
        raise ValueError("Selected six pair-week source cohort not complete")
    if not set(chosen.utc_hour_start)==set(HOURS):
        raise ValueError("Hourly source UTC calendar not exact")
    chosen["pair"]=chosen.ba_a+" / "+chosen.ba_b
    chosen["utc_date"]=chosen.utc_hour_start.dt.strftime("%Y-%m-%d")
    chosen["utc_hour"]=chosen.utc_hour_start.dt.hour
    chosen["partition"]=np.where(chosen.utc_hour_start<START+pd.Timedelta(hours=7),
                                 "2024_Jan_Jun","2024_Jul_Dec")
    pair_rows=[]
    for (a,b),g in chosen.groupby(["ba_a","ba_b"],sort=True):
        known=g[g.both_direction_values_present]
        v=known.signed_reciprocity_sum_mw
        pair_rows.append({"ba_a":a,"ba_b":b,"source_hours":len(g),
                          "both_numeric_hours":len(known),"missing_direction_hours":len(g)-len(known),
                          "signed_pair_discrepancy_mwh":float(v.sum()),
                          "absolute_pair_discrepancy_mwh":float(v.abs().sum()),
                          "positive_residual_hours":int((v>1).sum()),
                          "negative_residual_hours":int((v< -1).sum()),
                          "within_1mw_hours":int((v.abs()<=1).sum()),
                          "first_partition_hours":int(g.partition.eq("2024_Jan_Jun").sum()),
                          "second_partition_hours":int(g.partition.eq("2024_Jul_Dec").sum()),
                          "physical_transmission_loss_identified":False})
    group_cols=["pair","utc_date"]
    daily=chosen.groupby(group_cols,sort=True).agg(
        numeric_hours=("both_direction_values_present","sum"),
        missing_direction_hours=("both_direction_values_present",lambda v:int((~v).sum())),
        signed_difference_reported_hours_mwh=("signed_reciprocity_sum_mw",lambda v:v.sum(min_count=1)),
        absolute_difference_reported_hours_mwh=("absolute_reciprocity_sum_mw",lambda v:v.sum(min_count=1))
    ).reset_index()
    hourly_pattern=chosen.groupby(["pair","utc_hour"],sort=True).agg(
        numeric_hour_records=("both_direction_values_present","sum"),
        missing_direction_records=("both_direction_values_present",lambda v:int((~v).sum())),
        mean_signed_difference_reported_hours_mw=("signed_reciprocity_sum_mw","mean"),
        mean_absolute_difference_reported_hours_mw=("absolute_reciprocity_sum_mw","mean")
    ).reset_index()
    partition=chosen.groupby(["pair","partition"],sort=True).agg(
        source_hours=("both_direction_values_present","size"),
        numeric_hours=("both_direction_values_present","sum"),
        absolute_reported_difference_mwh=("absolute_reciprocity_sum_mw",lambda v:v.sum(min_count=1)),
        signed_reported_difference_mwh=("signed_reciprocity_sum_mw",lambda v:v.sum(min_count=1))
    ).reset_index()
    pair_df=pd.DataFrame(pair_rows)
    if pair_df.first_partition_hours.ne(7).any() or pair_df.second_partition_hours.ne(161).any():
        raise ValueError("Source half-year boundary differs from archival cohort")
    return pair_df,daily,hourly_pattern,partition,chosen


def plot(pair,daily,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dest=Path(out);dest.mkdir(parents=True,exist_ok=True)
    names=[" / ".join(p) for p in PAIRS]
    fig,axes=plt.subplots(2,1,figsize=(9.4,6.5),layout="constrained")
    x=np.arange(len(names))
    indices=pair.set_index(["ba_a","ba_b"])
    abs_values=[indices.loc[p,"absolute_pair_discrepancy_mwh"]/1000 for p in PAIRS]
    axes[0].bar(x,abs_values)
    axes[0].set_xticks(x,names,rotation=17,ha="right")
    axes[0].set_ylabel("Sum absolute reporting mismatch (thousand MWh)")
    axes[0].set_title("A  Selected reported BA-pair reciprocity",loc="left")
    for p in PAIRS[:5]:
        d=daily.loc[daily.pair.eq(" / ".join(p))].sort_values("utc_date")
        axes[1].plot(pd.to_datetime(d.utc_date),d.absolute_difference_reported_hours_mwh/1000,
                     marker="o",markersize=3,label=" / ".join(p))
    axes[1].legend(ncol=3,fontsize=8,frameon=False)
    axes[1].set_ylabel("Daily sum absolute mismatch (thousand MWh)")
    axes[1].set_title("B  UTC-day pattern of reported reciprocity differences",loc="left")
    for a in axes:
        a.grid(axis="y",alpha=.2)
        a.set_axisbelow(True)
    fig.text(.5,-.015,"Original EIA-930 BA-directed reports; both numeric directions only. "
             "Not physical loss, rated transmission capacity or historical EENS.",
             ha="center",fontsize=8,wrap=True)
    for ext in ("png","pdf"):
        fig.savefig(dest/f"fig_paperc_2024_bilateral_reciprocity_temporal.{ext}",
                    dpi=220,bbox_inches="tight")
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    for k in ("source","manifest","output"):p.add_argument("--"+k,required=True)
    args=p.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    result=analyze(pd.read_csv(args.source),json.loads(Path(args.manifest).read_text()))
    for name,frame in zip(("pair_summary","daily","utc_hour_pattern","source_partition","selected_hourly"),result):
        frame.to_csv(out/f"paperc_reciprocity_{name}.csv",index=False)
    plot(result[0],result[1],out)
    scope={"authentic_41_pair_cohort":True,"selected_pairs":[list(p) for p in PAIRS],
           "first_partition_hours_per_pair":7,"second_partition_hours_per_pair":161,
           "unpaired_values_not_zeroed":True,"reporting_discrepancy_not_physical_loss":True,
           "historical_eens_calibrated":False}
    (out/"paperc_reciprocity_temporal_scope.json").write_text(json.dumps(scope,indent=2)+"\n")
    print(result[0].to_string(index=False))
    print(result[3].to_string(index=False))


if __name__=="__main__":
    main()
