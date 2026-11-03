"""Counterfactual, hourly-resolved firm-capacity contribution frontier.

This computes an *idealized upper bound* on how much incremental perfectly
available firm capacity could reduce the SCREENING MODEL's unmet requirement.
It does not imply observed unserved electricity, deployable capacity, or
historical generation. Works without PyPSA.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def frontier(hourly, additions_mw, *, year=2024, month=1):
    needed={"timestamp_utc", "modeled_unserved_mw", "bus_balance_residual_mw"}
    if not needed.issubset(hourly.columns):
        raise ValueError("Missing source fields: " + str(sorted(needed-set(hourly.columns))))
    d=hourly.copy()
    d["timestamp_utc"]=pd.to_datetime(d.timestamp_utc, utc=True, errors="raise")
    expected=pd.date_range(f"{year}-{month:02d}-01",
                           periods=pd.Period(f"{year}-{month:02d}").days_in_month*24,
                           freq="h",tz="UTC")
    if len(d)!=len(expected) or d.timestamp_utc.duplicated().any():
        raise ValueError("Missing or duplicate source hours")
    if not pd.DatetimeIndex(d.timestamp_utc).equals(expected):
        raise ValueError("Unexpected source hour order or UTC period")
    for k in ("modeled_unserved_mw","bus_balance_residual_mw"):
        d[k]=pd.to_numeric(d[k],errors="raise")
    u=d.modeled_unserved_mw.to_numpy(dtype=float)
    residual=d.bus_balance_residual_mw.to_numpy(dtype=float)
    if not np.isfinite(u).all() or not np.isfinite(residual).all():
        raise ValueError("Nonfinite source diagnostics")
    if (u < -1e-6).any() or abs(residual).max()>1e-4:
        raise ValueError("Negative gap or non-conserved source network")
    u=np.maximum(u,0)
    options=np.asarray(list(additions_mw),dtype=float)
    if options.ndim!=1 or len(options)==0 or not np.isfinite(options).all() or (options<0).any():
        raise ValueError("Invalid incremental firm capacity scenarios")
    if len(np.unique(options))!=len(options):
        raise ValueError("Duplicate capacity scenarios")
    baseline=float(u.sum())
    rows=[]
    for value in sorted(options):
        remaining=np.maximum(u-value,0)
        delta=baseline-float(remaining.sum())
        rows.append({
          "incremental_firm_capacity_mw":float(value),
          "baseline_model_gap_mwh":baseline,
          "remaining_model_gap_mwh":float(remaining.sum()),
          "maximum_gap_reduction_mwh":delta,
          "maximum_gap_reduction_share":delta/baseline if baseline>0 else None,
          "remaining_positive_gap_hours":int(np.count_nonzero(remaining>1e-6)),
          "peak_remaining_gap_mw":float(remaining.max()),
          "hypothetical_full_output_month_mwh":float(value*len(u))
        })
    return pd.DataFrame(rows),{
       "period":f"{year}-{month:02d}", "hours":len(u),
       "baseline_model_gap_mwh":baseline,
       "minimum_additional_perfectly_firm_mw_to_eliminate_all_model_gaps":float(u.max()),
       "baseline_positive_gap_hours":int(np.count_nonzero(u>1e-6)),
       "assumptions":"Additional capacity perfectly available in every hour, dispatched only to offset screened deficits; no fuel, unit commitment, storage, network or real-world capacity eligibility",
       "actual_outages_observed":False,
       "historical_calibration_certified":False
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--month",type=int,default=1)
    p.add_argument("--additions-mw",type=float,nargs="+",
                   default=[0,100,250,390.4,500,1000,1500,2025.955])
    args=p.parse_args()
    rows,manifest=frontier(pd.read_csv(args.hourly),args.additions_mw,
                           year=args.year,month=args.month)
    folder=Path(args.output);folder.mkdir(parents=True,exist_ok=True)
    rows.to_csv(folder/"firm_capacity_frontier.csv",index=False)
    (folder/"firm_capacity_frontier_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(rows.to_string(index=False))
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
