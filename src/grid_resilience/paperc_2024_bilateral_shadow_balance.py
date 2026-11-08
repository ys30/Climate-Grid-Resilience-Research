"""Paper C unfilled CISO BA-balance counterfactual using EIA bilateral totals.

A bilateral SUM is not a verified substitute for missing original BA Total
Interchange. Report shadow arithmetic only, with no original column edits,
no EENS or physical calibration inference.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd


def compare(original, bilateral):
    needed_a={"utc_hour_start","ba","demand_mw","net_generation_mw",
              "net_interchange_mw","raw_triplet_present"}
    needed_b={"utc_hour_start","ba","sum_reported_bilateral_mw",
              "bilateral_all_present_counterparty_values_reported",
              "balance_total_interchange_reported"}
    if not needed_a.issubset(original) or not needed_b.issubset(bilateral):
        raise ValueError("Original BA and bilateral hour source fields required")
    if len(original)!=672 or len(bilateral)!=672:
        raise ValueError("Missing 168h x 4BA original evidence")
    keys=["utc_hour_start","ba"]
    if original.duplicated(keys).any() or bilateral.duplicated(keys).any():
        raise ValueError("Duplicate BA/hour")
    x=original.merge(bilateral[list(needed_b)],on=keys,how="inner",validate="one_to_one")
    if len(x)!=672:raise ValueError("Missing exact original/bilateral match")
    for col in ("demand_mw","net_generation_mw"):
        x[col]=pd.to_numeric(x[col],errors="coerce")
    if not np.isfinite(x[["demand_mw","net_generation_mw"]].to_numpy(float)).all():
        raise ValueError("Incomplete original BA demand/net-generation")
    x["shadow_usable"]=x.bilateral_all_present_counterparty_values_reported.eq(True)
    b=pd.to_numeric(x.sum_reported_bilateral_mw,errors="coerce")
    x["shadow_bilateral_minus_original_total_mw"]=b-x.net_interchange_mw
    x["shadow_demand_generation_minus_bilateral_mw"]=(
        x.net_generation_mw-x.demand_mw-b)
    x.loc[~x.shadow_usable,"shadow_demand_generation_minus_bilateral_mw"]=np.nan
    x["shadow_tolerance_mw"]=x.demand_mw.abs().mul(.01).clip(lower=1.0)
    x["shadow_closes"]=x.shadow_usable & (
        x.shadow_demand_generation_minus_bilateral_mw.abs().le(x.shadow_tolerance_mw))
    x["raw_total_missing_with_shadow_available"]=(
        x.net_interchange_mw.isna()&x.shadow_usable)
    summary=[]
    for ba,g in x.groupby("ba",sort=True):
        missing=g.loc[g.raw_total_missing_with_shadow_available]
        v=missing.shadow_demand_generation_minus_bilateral_mw
        summary.append({
            "ba":ba,"original_ba_hours":len(g),
            "original_total_interchange_missing_hours":int(g.net_interchange_mw.isna().sum()),
            "source_missing_with_bilateral_sum_hours":len(missing),
            "candidate_shadow_arithmetic_closing_missing_total_hours":int(
                missing.shadow_closes.sum()),
            "candidate_shadow_arithmetic_nonclosing_missing_total_hours":int(
                len(missing)-missing.shadow_closes.sum()),
            "candidate_shadow_signed_residual_on_missing_total_hours_mwh":float(v.sum()),
            "candidate_shadow_absolute_residual_on_missing_total_hours_mwh":float(v.abs().sum()),
            "original_raw_total_unchanged":True,
            "reported_bilateral_partner_universe_fully_verified":False,
            "physical_transmission_or_EENS_calibrated":False})
    return x,pd.DataFrame(summary)


def main():
    p=argparse.ArgumentParser()
    for field in ("original","bilateral","output"):p.add_argument("--"+field,required=True)
    a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    full,summary=compare(pd.read_csv(a.original),pd.read_csv(a.bilateral))
    full.to_csv(out/"july2024_shadow_bilateral_balance_hourly.csv",index=False)
    summary.to_csv(out/"july2024_shadow_bilateral_balance_by_ba.csv",index=False)
    (out/"july2024_shadow_bilateral_scope.json").write_text(json.dumps({
        "original_raw_demand_generation_total_interchange_preserved":True,
        "shadow_bilateral_is_hypothetical_reporting_reconstruction":True,
        "official_missing_total_interchange_imputed":False,
        "counterparty_universe_complete_proven":False,
        "historical_reliability_or_EENS_calibrated":False
    },indent=2)+"\n")
    print(summary.to_string(index=False))


if __name__=="__main__":main()
