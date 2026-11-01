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
    merged["reported_balance_residual_absolute_mw"]=merged.reported_balance_residual_if_ti_outflow_mw.abs()
    merged["reported_balance_closure_flag"]=merged.reported_balance_residual_absolute_mw<=merged.demand_mw.mul(0.01).clip(lower=1)
    merged["charging_during_nonclosure"]= (merged.simulated_charge_mw>1e-5)&(~merged.reported_balance_closure_flag)
    summary=merged.groupby(["scenario","ba"]).agg(
        hours=("timestamp","size"),modeled_charge_mwh=("simulated_charge_mw","sum"),
        observed_net_generation_mwh=("eia930_ng_mw","sum"),
        observed_demand_mwh=("demand_mw","sum"),
        observed_total_interchange_mwh=("eia930_ti_mw","sum"),
        charging_hours_when_ng_below_demand=("charging_with_reported_generation_below_demand","sum"),
        hours_balance_nonclosure=("reported_balance_closure_flag",lambda x:int((~x).sum())),
        charging_hours_during_balance_nonclosure=("charging_during_nonclosure","sum"),
        max_absolute_reported_balance_residual_mw=("reported_balance_residual_absolute_mw","max")).reset_index()
    # Do not silently choose interchange sign: publish both accounting hypotheses.
    merged["balance_residual_ti_plus_mw"]=merged.eia930_ng_mw-merged.demand_mw+merged.eia930_ti_mw
    diagnostics=[]
    for ba,part in merged[merged.scenario=="baseline"].groupby("ba"):
        threshold=part.demand_mw.mul(0.01).clip(lower=1)
        minus=part.reported_balance_residual_if_ti_outflow_mw
        plus=part.balance_residual_ti_plus_mw
        diagnostics.append({"ba":ba,"hours":len(part),
          "ng_minus_d_minus_ti_nonclosing_hours":int((minus.abs()>threshold).sum()),
          "ng_minus_d_plus_ti_nonclosing_hours":int((plus.abs()>threshold).sum()),
          "ng_minus_d_minus_ti_abs_sum_mwh":float(minus.abs().sum()),
          "ng_minus_d_plus_ti_abs_sum_mwh":float(plus.abs().sum()),
          "ng_minus_d_minus_ti_signed_sum_mwh":float(minus.sum()),
          "ng_minus_d_plus_ti_signed_sum_mwh":float(plus.sum())})
    diagnostic=pd.DataFrame(diagnostics)
    assert len(diagnostic)==4 and diagnostic.hours.eq(168).all()
    diagnostic.to_csv(out/"eia930_interchange_sign_hypotheses.csv",index=False)
    print("ALTERNATIVE INTERCHANGE SIGN HYPOTHESES (not physical calibration):")
    print(diagnostic.to_string(index=False))
    # Diagnose UTC timestamp alignment as an alternative cause of hourly
    # nonclosure. Report every lag, never choose the best lag automatically.
    alignment=[]
    for ba,part in merged[merged.scenario=="baseline"].groupby("ba"):
        part=part.sort_values("timestamp").reset_index(drop=True)
        observed_times=pd.DatetimeIndex(part.timestamp)
        assert (observed_times[1:]-observed_times[:-1]==pd.Timedelta(hours=1)).all()
        for shift_hours in (-2,-1,0,1,2):
            shifted=part.eia930_ti_mw.shift(shift_hours)
            valid=shifted.notna()
            residual=part.eia930_ng_mw[valid]-part.demand_mw[valid]-shifted[valid]
            limit=part.demand_mw[valid].mul(0.01).clip(lower=1)
            alignment.append({"ba":ba,"ti_shift_hours_diagnostic_only":shift_hours,
                "paired_hours":int(valid.sum()),
                "nonclosing_hours":int((residual.abs()>limit).sum()),
                "absolute_residual_sum_mwh":float(residual.abs().sum()),
                "signed_residual_sum_mwh":float(residual.sum()),
                "mean_absolute_residual_mw":float(residual.abs().mean())})
    lag=pd.DataFrame(alignment)
    assert len(lag)==20
    lag.to_csv(out/"eia930_interchange_timestamp_shift_diagnostic.csv",index=False)
    print("UTC INTERCHANGE ALIGNMENT DIAGNOSTIC (do not shift source data for calibration):")
    print(lag.to_string(index=False))
    summary.to_csv(out/"charging_vs_observed_eia930_summary.csv",index=False)
    assert len(summary)==16 and summary.hours.eq(168).all()
    print("Caution: TI sign convention and BA accounting closure must be independently verified.")
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
