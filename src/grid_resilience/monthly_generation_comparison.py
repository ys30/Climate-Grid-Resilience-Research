"""Fail-closed monthly generation comparison; does not certify calibration.

The caller must supply independently audited observed monthly net electric MWh
and simulated monthly net generation at matching BA/technology/month keys.
No source downloading, imputation or capacity adjustment is performed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

KEYS = ["year", "month", "ba", "technology"]
OBS = {"net_generation_mwh", "source"}
MOD = {"modeled_generation_mwh"}

def compare(observed: pd.DataFrame, modeled: pd.DataFrame, *, holdout_years: set[int]):
    o, m = observed.copy(), modeled.copy()
    for label, frame, fields in (("observed", o, set(KEYS)|OBS),
                                 ("modeled", m, set(KEYS)|MOD)):
        missing = fields-set(frame.columns)
        if missing: raise ValueError(f"{label}: missing {sorted(missing)}")
        if frame.empty or frame[list(fields)].isna().any().any():
            raise ValueError(f"{label}: empty/null records")
        if frame.duplicated(KEYS).any():
            raise ValueError(f"{label}: duplicate monthly BA/technology keys")
        frame["year"] = pd.to_numeric(frame.year, errors="raise").astype(int)
        frame["month"] = pd.to_numeric(frame.month, errors="raise").astype(int)
        if not frame.month.between(1,12).all():
            raise ValueError(f"{label}: invalid calendar month")
        if frame.ba.astype(str).str.strip().eq("").any() or frame.technology.astype(str).str.strip().eq("").any():
            raise ValueError(f"{label}: blank BA or technology")
    if o.source.astype(str).str.strip().eq("").any():
        raise ValueError("Observed source provenance must be nonblank")
    for frame,col in ((o,"net_generation_mwh"),(m,"modeled_generation_mwh")):
        frame[col]=pd.to_numeric(frame[col],errors="raise")
        if not np.isfinite(frame[col].to_numpy(dtype=float)).all():
            raise ValueError(f"Nonfinite {col}")
    if set(map(tuple,o[KEYS].itertuples(index=False,name=None))) != set(map(tuple,m[KEYS].itertuples(index=False,name=None))):
        raise ValueError("Incomplete or extra modeled/observed BA-technology-month keys")
    if not holdout_years or not (holdout_years & set(o.year)):
        raise ValueError("At least one holdout year must exist in both datasets")
    if not (set(o.year)-holdout_years):
        raise ValueError("Training/comparison years are absent")
    merged=o.merge(m,on=KEYS,validate="one_to_one")
    merged["period"]=np.where(merged.year.isin(holdout_years),"holdout","training")
    merged["error_mwh"]=merged.modeled_generation_mwh-merged.net_generation_mwh
    merged["absolute_error_mwh"]=merged.error_mwh.abs()
    merged["squared_error_mwh2"]=merged.error_mwh**2
    def summarize(group):
        return pd.Series({
            "n_months":len(group),
            "signed_bias_mwh":float(group.error_mwh.mean()),
            "mae_mwh":float(group.absolute_error_mwh.mean()),
            "rmse_mwh":float(np.sqrt(group.squared_error_mwh2.mean())),
            "observed_total_mwh":float(group.net_generation_mwh.sum()),
            "modeled_total_mwh":float(group.modeled_generation_mwh.sum())})
    metrics=merged.groupby(["period","ba","technology"],sort=True)[["net_generation_mwh","modeled_generation_mwh","error_mwh","absolute_error_mwh","squared_error_mwh2"]].apply(summarize).reset_index()
    return merged.sort_values(KEYS),metrics

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--observed",type=Path,required=True)
    p.add_argument("--modeled",type=Path,required=True)
    p.add_argument("--holdout-year",type=int,action="append",required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    rows,metrics=compare(pd.read_csv(a.observed),pd.read_csv(a.modeled),holdout_years=set(a.holdout_year))
    a.output_dir.mkdir(parents=True,exist_ok=True)
    rows.to_csv(a.output_dir/"generation_monthly_comparison.csv",index=False)
    metrics.to_csv(a.output_dir/"generation_monthly_metrics.csv",index=False)
    (a.output_dir/"calibration_status.json").write_text(json.dumps({
        "comparison_computed":True,"historical_calibration_certified":False,
        "limitations":"Independent source reconciliation and holdout validation must be documented separately.",
        "holdout_years":sorted(set(a.holdout_year))},indent=2)+"\n")

if __name__=="__main__":
    main()
