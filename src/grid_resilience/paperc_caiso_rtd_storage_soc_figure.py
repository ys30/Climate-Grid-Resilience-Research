"""CAISO RTD LESR 2023/24 energy and SOC: exact interval completeness and figures.

Each recorded 5-minute RTD interval is a CAISO preliminary MARKET result.
All 12 observations per UTC hour are required for hourly mean visualization.
Hourly means are descriptive raw VALUE statistics, not delivered MWh,
metered charging/discharging, certified physical SOC, or EENS.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

STUDIES={2023:"2023-07-10T00:00:00Z",2024:"2024-07-01T00:00:00Z"}
TYPES=("EN","SOC")


def evaluate(source,scope):
    if not scope.get("utc_hour_join_uses_los_angeles_summer_dst"):
        raise ValueError("Unverified UTC-to-PDT source mapping")
    if not scope.get("market_result_source_not_actual_metered_charge_discharge"):
        raise ValueError("Missing source market-output nature")
    fields={"eia930_study_year","utc_hour_start_from_local_trade_date","market",
            "resource_type","output_type","interval_index","original_market_value"}
    if not fields.issubset(source):raise ValueError("Original CAISO market output columns missing")
    subset=source.loc[source.market.eq("RTD")&source.resource_type.eq("LESR")&
                      source.output_type.isin(TYPES)].copy()
    subset["utc_hour"]=pd.to_datetime(subset.utc_hour_start_from_local_trade_date,utc=True)
    if subset.duplicated(["eia930_study_year","utc_hour",
                          "output_type","interval_index"]).any():
        raise ValueError("Repeated RTD source interval")
    expected=[]
    actual=[]
    for year,start in STUDIES.items():
        hours=pd.date_range(start,periods=168,freq="h")
        frame=subset.loc[subset.eia930_study_year.eq(year)]
        if set(frame.utc_hour)!=set(hours):
            raise ValueError("Source RTD interval hours do not cover each UTC study week")
        if not frame.interval_index.between(1,12).all():
            raise ValueError("Invalid RTD interval number")
        for typ in TYPES:
            for t in hours:
                selected=frame.loc[frame.utc_hour.eq(t)&frame.output_type.eq(typ)]
                actual_intervals=set(selected.interval_index.astype(int))
                missing=sorted(set(range(1,13))-actual_intervals)
                if selected.original_market_value.isna().any():
                    raise ValueError("Raw market value missing; not imputable")
                valid=len(missing)==0 and len(selected)==12
                expected.append({"year":year,"utc_hour":t.isoformat(),
                    "rtd_output_type":typ,"recorded_5min_intervals":len(selected),
                    "missing_rtd_intervals":len(missing),
                    "missing_interval_identifiers":",".join(map(str,missing)),
                    "complete_twelve_intervals":valid,
                    "mean_raw_market_value_complete_hour_only":
                     float(selected.original_market_value.mean()) if valid else None,
                    "no_physical_soc_or_metered_output_inferred":True})
                for x in missing:
                    actual.append({"year":year,"utc_hour":t.isoformat(),
                                   "rtd_output_type":typ,"missing_interval":x,
                                   "original_value_preserved_missing":True})
    diag=pd.DataFrame(expected)
    missing=pd.DataFrame(actual,columns=["year","utc_hour","rtd_output_type",
                                          "missing_interval","original_value_preserved_missing"])
    if len(diag)!=2*168*2:
        raise ValueError("Expected 672 source reporting diagnostic rows")
    metadata={"cohorts":list(STUDIES),
        "rtd_expected_intervals_each_type_year":2016,
        "hourly_mean_requires_all_twelve_original_intervals":True,
        "incomplete_hour_displayed_as_nan_not_zero":True,
        "raw_CAiSO_value_is_preliminary_market_output_not_metered_generation":True,
        "source_SOC_market_value_not_physical_battery_soc_verified":True,
        "reliability_or_eens_calibrated":False}
    return diag,missing,metadata


def figure(diag,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    p=Path(out);p.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(2,2,figsize=(11,7),layout="constrained",sharex=True)
    for i,year in enumerate(STUDIES):
        for j,typ in enumerate(TYPES):
            ax=axes[i,j]
            x=diag.loc[diag.year.eq(year)&diag.rtd_output_type.eq(typ)].copy()
            x["utc_hour"]=pd.to_datetime(x.utc_hour,utc=True)
            x=x.sort_values("utc_hour")
            ax.plot(np.arange(168),x.mean_raw_market_value_complete_hour_only,
                    linewidth=1.2)
            ax.axhline(0,color="grey",linewidth=.65)
            ax.set_title(f"{year} CAISO RTD LESR {typ} · preliminary market output",loc="left")
            ax.set_ylabel("Raw VALUE, complete-hour mean")
            ax.set_xlabel("Hours since the respective 168h UTC cohort start")
            ax.grid(alpha=.2)
            ax.set_axisbelow(True)
    fig.text(.5,-.015,
             "No missing intervals replaced by zero; EN/SOC are CAISO preliminary market outputs, "
             "not metered battery flow, certified physical SOC, actual shortages or EENS.",
             fontsize=8,ha="center",wrap=True)
    for ext in ("png","pdf"):
        fig.savefig(p/f"fig_paperc_caiso_2023_2024_storage_rtd_market_en_soc.{ext}",
                    bbox_inches="tight",dpi=230)
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    for k in ("source","manifest","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    d,m,scope=evaluate(pd.read_csv(a.source),
        json.loads(Path(a.manifest).read_text()))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    d.to_csv(out/"paperc_caiso_rtd_lesr_en_soc_complete_hour_gate.csv",index=False)
    m.to_csv(out/"paperc_caiso_rtd_missing_interval_keys.csv",index=False)
    (out/"paperc_caiso_rtd_hourly_completeness_scope.json").write_text(
        json.dumps(scope,indent=2)+"\n")
    figure(d,out)
    print("CAISO ORIGINAL RTD COMPLETENESS",d.groupby(
        ["year","rtd_output_type"]).agg(
        recorded_intervals=("recorded_5min_intervals","sum"),
        complete_hours=("complete_twelve_intervals","sum"),
        missing_intervals=("missing_rtd_intervals","sum")).to_string())
    print("MISSING ORIGINAL RTD INTERVAL KEYS",m.to_string(index=False))


if __name__=="__main__":main()
