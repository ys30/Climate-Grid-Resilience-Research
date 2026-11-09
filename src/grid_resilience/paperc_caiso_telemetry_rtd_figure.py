"""CAISO historical battery telemetry versus preliminary LESR RTD EN figure.

Predeclared temporal shift sensitivity -10,-5,0,+5,+10 minutes. Do not
reinterpret high association as meter-level calibration or dispatch error:
outlook supplies actual-oriented informational aggregates including hybrids,
whereas RTD LESR EN is market award for a different resource population.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

YEARS=(2023,2024)
LAGS=(-10,-5,0,5,10)


def analyze(frame,scope):
    if not scope.get("market_EN_is_preliminary_not_settlement_metering"):
        raise ValueError("Original market source quality caveat missing")
    if not scope.get("rtd_lesr_is_market_resource_type_not_identical_scope"):
        raise ValueError("Resource scope not properly separated")
    cols={"year","utc_5min_start","total_batteries_5min_mw",
          "standalone_batteries_5min_mw","hybrid_batteries_5min_mw",
          "rtd_lesr_en_preliminary_market_value","market_record_present"}
    if not cols.issubset(frame):raise ValueError("Missing source-audited five-minute fields")
    x=frame.copy()
    x["utc_5min_start"]=pd.to_datetime(x.utc_5min_start,utc=True,errors="raise")
    x["market_record_present"]=x.market_record_present.map(
        {True:True,False:False,"True":True,"False":False})
    if x.market_record_present.isna().any():
        raise ValueError("Market source presence flag malformed")
    if x.duplicated(["year","utc_5min_start"]).any():
        raise ValueError("Duplicate source UTC five-minute keys")
    if not x.loc[x.market_record_present,
                 "rtd_lesr_en_preliminary_market_value"].notna().all():
        raise ValueError("Observed market value absent")
    if x.loc[~x.market_record_present,
             "rtd_lesr_en_preliminary_market_value"].notna().any():
        raise ValueError("Unreported source market record filled")
    details=[]
    summary=[]
    for year in YEARS:
        subset=x.loc[x.year.eq(year)].sort_values("utc_5min_start").copy()
        if len(subset)!=2016:raise ValueError("Expected 2016 original telemetry time keys")
        if not subset.utc_5min_start.diff().iloc[1:].eq(pd.Timedelta(minutes=5)).all():
            raise ValueError("Non-contiguous five minute telemetry")
        if not np.isfinite(subset.total_batteries_5min_mw).all():
            raise ValueError("Nonfinite raw telemetry values")
        measured=subset.set_index("utc_5min_start").total_batteries_5min_mw
        market=subset.set_index("utc_5min_start").rtd_lesr_en_preliminary_market_value
        for lag in LAGS:
            shifted=market.copy()
            shifted.index=shifted.index+pd.Timedelta(minutes=lag)
            pairs=pd.concat([measured,shifted.rename("market")],axis=1,join="inner").dropna()
            corr=float(pairs.iloc[:,0].corr(pairs.market))
            summary.append({"year":year,"rtd_market_utc_shift_minutes_for_sensitivity":lag,
                            "paired_source_five_minute_points":len(pairs),
                            "pearson_correlation_descriptive_only":corr,
                            "market_and_telemetry_not_same_physical_population":True,
                            "real_dispatch_error_calibrated":False})
        subset["relative_five_minute_index"]=range(2016)
        details.append(subset)
    return pd.concat(details,ignore_index=True),pd.DataFrame(summary)


def graph(frame,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    path=Path(out);path.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(2,1,figsize=(11,6.4),sharex=True,layout="constrained")
    for ax,year in zip(axes,YEARS):
        s=frame.loc[frame.year.eq(year)].sort_values("relative_five_minute_index")
        ax.plot(s.relative_five_minute_index/12,s.total_batteries_5min_mw,
                linewidth=.85,label="CAISO Outlook total batteries (5min informational MW)")
        ax.plot(s.relative_five_minute_index/12,
                s.rtd_lesr_en_preliminary_market_value,
                linewidth=.85,alpha=.72,label="CAISO RTD LESR EN (preliminary market VALUE)")
        ax.set_title(f"{year} distinct seven-day UTC study window",loc="left")
        ax.set_ylabel("Original source numeric MW / market VALUE")
        ax.axhline(0,linewidth=.55,color="grey")
        ax.grid(alpha=.2)
        ax.set_axisbelow(True)
    axes[-1].set_xlabel("Hours since start of each distinct UTC week")
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,ncol=1,loc="outside upper right",fontsize=8,frameon=False)
    fig.text(.5,-.018,"Comparative source signature only. Different resource scopes: telemetry includes "
             "some hybrids; market EN is preliminary LESR RTD. Missing market intervals stay blank. "
             "Not meter-level dispatch validation, battery SOC, physical adequacy or EENS.",
             fontsize=8,ha="center",wrap=True)
    for ext in ("png","pdf"):
        fig.savefig(path/f"fig_paperc_caiso_five_minute_battery_outlook_vs_rtd.{ext}",
                    dpi=215,bbox_inches="tight")
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    for key in ("source","manifest","output"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    source=pd.read_csv(a.source)
    scope=json.loads(Path(a.manifest).read_text())
    full,stats=analyze(source,scope)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    full.to_csv(out/"paperc_caiso_five_minute_battery_vs_rtd_plot_data.csv",index=False)
    stats.to_csv(out/"paperc_caiso_battery_rtd_5min_shift_sensitivity.csv",index=False)
    graph(full,out)
    meta={"source_records":len(full),"lag_minute_grid":list(LAGS),
          "telemetry_and_market_not_same_resource_population":True,
          "preliminary_market_value_not_metered_dispatch":True,
          "no_actual_hourly_available_capacity_or_EENS_claim":True}
    (out/"paperc_battery_telemetry_market_figure_scope.json").write_text(
        json.dumps(meta,indent=2)+"\n")
    print("CAISO FIVEMINUTE SHIFT SENSITIVITY",stats.to_string(index=False))


if __name__=="__main__":main()
