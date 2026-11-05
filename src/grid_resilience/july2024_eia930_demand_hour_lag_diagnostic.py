"""Lag diagnostic for original vs officially re-extracted 2024 July BA demand.

A one-hour end-hour versus start-hour reporting convention can appear as 168
changed values at the same UTC keys, even if original values are identical
at an offset. Compare only genuinely overlapping source timestamps; do not
fill first/last hours or assert which time convention is correct on fit alone.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

LAGS=(-2,-1,0,1,2)
BAS=("AZPS","BPAT","CISO","SRP")


def audit(original,refetched):
    cols={"timestamp","ba","demand_mw"}
    if not cols.issubset(original) or not cols.issubset(refetched):
        raise ValueError("Missing observed EIA930 source timestamp/BA/demand")
    old,new=original.copy(),refetched.copy()
    for frame in (old,new):
        frame["timestamp"]=pd.to_datetime(frame.timestamp,utc=True,errors="raise")
        frame["demand_mw"]=pd.to_numeric(frame.demand_mw,errors="coerce")
        if frame.duplicated(["timestamp","ba"]).any():
            raise ValueError("Duplicated source BA hour")
        if not np.isfinite(frame.demand_mw.to_numpy(float)).all():
            raise ValueError("Missing actual demand source value")
        if len(frame)!=4*168 or set(frame.ba)!=set(BAS):
            raise ValueError("Expected original first-week 4 BA source")
    records=[]
    for ba in BAS:
        a=old.loc[old.ba.eq(ba),["timestamp","demand_mw"]].copy()
        b=new.loc[new.ba.eq(ba),["timestamp","demand_mw"]].copy()
        if len(a)!=168 or len(b)!=168:
            raise ValueError("Unexpected source BA coverage")
        for lag in LAGS:
            shifted=a.assign(timestamp=a.timestamp+pd.Timedelta(hours=lag))
            joined=shifted.merge(b,on="timestamp",how="inner",
                                 suffixes=("_original","_refetched"),
                                 validate="one_to_one")
            if len(joined)!=168-abs(lag):
                raise ValueError("Original and new observed source UTC grids not aligned")
            diff=joined.demand_mw_refetched-joined.demand_mw_original
            records.append({
                "ba":ba,"old_source_timestamp_shift_hours":lag,
                "overlapping_real_hour_pairs":len(joined),
                "exact_match_hour_pairs_tolerance_1e8":int(np.isclose(
                    joined.demand_mw_original,joined.demand_mw_refetched,
                    rtol=0,atol=1e-8).sum()),
                "demand_mae_mw":float(diff.abs().mean()),
                "demand_rmse_mw":float(np.sqrt(np.mean(diff**2))),
                "demand_max_absolute_diff_mw":float(diff.abs().max())
            })
    result=pd.DataFrame(records)
    best=result.sort_values(["ba","demand_mae_mw",
                             "old_source_timestamp_shift_hours"]).groupby("ba").head(1)
    manifest={
        "lag_alignment_is_diagnostic_not_proof_of_source_hour_convention":True,
        "all_input_windows_real_and_overlapping":True,
        "zero_padding_or_demand_interpolation":False,
        "all_four_bas_examined":True,
        "lag_trials_hours":list(LAGS),
        "model_physical_calibration_or_historical_eens_claimed":False
    }
    return result,best,manifest


def main():
    p=argparse.ArgumentParser()
    for key in ("original","refetched","output"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    d,b,m=audit(pd.read_csv(a.original),pd.read_csv(a.refetched))
    root=Path(a.output);root.mkdir(parents=True,exist_ok=True)
    d.to_csv(root/"original_refetched_eia930_utc_lag_diagnostics.csv",index=False)
    b.to_csv(root/"original_refetched_eia930_best_lag_by_ba.csv",index=False)
    (root/"original_refetched_eia930_lag_manifest.json").write_text(
        json.dumps(m,indent=2)+"\n")
    print("REAL SOURCE EIA930 LAG COMPARISON")
    print(d.to_string(index=False))
    print("BEST EIA930 LAG DIAGNOSTIC")
    print(b.to_string(index=False))


if __name__=="__main__":
    main()
