"""Compare modelled hourly battery charging against observed EIA-930 BA accounting.

Reported generation, load and interchange are observed contemporaneous values,
not a marginal charging-availability counterfactual.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .eia930_hourly import fetch

BAS=("AZPS","BPAT","CISO","SRP")
def run(artifact, output, api_key):
    root=Path(artifact);out=Path(output);out.mkdir(parents=True,exist_ok=True)
    demand=pd.read_csv(root/"demand.csv")
    times=pd.to_datetime(demand.timestamp,utc=True)
    start=times.min();end=times.max()+pd.Timedelta(hours=1)
    assert len(times.unique())==168 and set(demand.ba)==set(BAS)
    observed=[]
    for kind in ("NG","TI"):
        f,meta=fetch(BAS,start.isoformat(),end.isoformat(),api_key,data_type=kind)
        observed.append((kind,f,meta))
    records=demand[["timestamp","ba","demand_mw"]].copy()
    records["timestamp"]=pd.to_datetime(records.timestamp,utc=True)
    for kind,frame,meta in observed:
        observed_frame=frame.rename(columns={"demand_mw":f"eia930_{kind.lower()}_mw"})
        records=records.merge(observed_frame,on=["timestamp","ba"],how="left",validate="one_to_one")
    assert len(records)==672 and records.notna().all().all()
    records["reported_generation_minus_demand_mw"]=records.eia930_ng_mw-records.demand_mw
    # EIA-930 total interchange is a reported accounting observation, NOT a verified
    # transfer capacity. Do not assume a sign-based net import without reconciling.
    records["reported_balance_residual_if_ti_outflow_mw"]=(records.eia930_ng_mw-records.demand_mw-records.eia930_ti_mw)
    charge=[]
    for scenario in ("baseline","heat_only","wind_only","heat_wind"):
        df=pd.read_csv(root/"with_storage"/"solved"/scenario/"storage_charge_mw.csv")
        df["timestamp"]=pd.to_datetime(df.timestamp,utc=True)
        for ba in BAS:
            sub=df[["timestamp",f"{ba}_battery"]].rename(columns={f"{ba}_battery":"simulated_charge_mw"})
            sub["ba"]=ba;sub["scenario"]=scenario;charge.append(sub)
    charging=pd.concat(charge,ignore_index=True)
    merged=charging.merge(records,on=["timestamp","ba"],validate="many_to_one")
    assert len(merged)==2688
    merged["charging_with_reported_generation_below_demand"]=(merged.simulated_charge_mw>1e-5)&(merged.reported_generation_minus_demand_mw<0)
    merged.to_csv(out/"observed_generation_interchange_vs_simulated_charge_hourly.csv",index=False)
    summary=merged.groupby(["scenario","ba"]).agg(
        hours=("timestamp","size"),modeled_charge_mwh=("simulated_charge_mw","sum"),
        observed_net_generation_mwh=("eia930_ng_mw","sum"),
        observed_demand_mwh=("demand_mw","sum"),
        observed_total_interchange_mwh=("eia930_ti_mw","sum"),
        charging_hours_when_ng_below_demand=("charging_with_reported_generation_below_demand","sum")).reset_index()
    summary.to_csv(out/"charging_vs_observed_eia930_summary.csv",index=False)
    manifest={"source":"EIA-930 API NG and TI for same UTC hour and BA",
        "time_window_utc":[start.isoformat(),end.isoformat()],
        "interpretation":"Diagnostic comparison only. NG minus demand is NOT available charging headroom; observed imports, intra-hour operations and market conditions are not represented by this isolated BA optimization.",
        "observed_dispatch_calibrated":False,"storage_charge_observed":False,
        "interchange_not_physical_rating":True,"response_meta":{k:v for k,_,v in observed}}
    (out/"charging_observation_comparison_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(summary.to_string(index=False));return summary
def main():
    import os
    p=argparse.ArgumentParser();p.add_argument("--artifact",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();run(a.artifact,a.output,os.getenv("EIA_API_KEY"))
if __name__=="__main__":main()
