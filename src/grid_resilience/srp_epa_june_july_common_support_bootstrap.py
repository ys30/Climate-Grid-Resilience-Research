"""Descriptive paired June–July date-block uncertainty on verified common support.

Freeze the original overlapping 2°C / 500 MW / 4h source cells before any
resampling. Resample *complete observed local calendar-date contributions*
independently within each month, relabel date FE for repeated draws, and
preserve site-level source dependence by never pooling EPA units. This is an
exploratory percentile sensitivity for the July-minus-June gross temperature
slope difference, NOT a validated 95% CI, causal effect or physical derating.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from grid_resilience.srp_epa_june_july_overlap_models import (
    BINS, KEYS, overlap_models, validate)
from grid_resilience.srp_epa_june_july_2024_common_support import common_support
from grid_resilience.srp_epa_eia930_day_block_bootstrap import partial_temperature_coef


def selected_source_month(frame, common_cells):
    g=frame.loc[frame[BINS].apply(tuple,axis=1).isin(common_cells)].copy()
    g=g.sort_values("timestamp_utc").reset_index(drop=True)
    local=g.timestamp_utc.dt.tz_convert("Etc/GMT+7")
    g["local_date"]=local.dt.strftime("%Y-%m-%d")
    g["local_hour"]=local.dt.hour
    g["srp_demand_mw"]=g.srp_ba_demand_mw
    y=np.where(g.operating_time.gt(0),g.gross_load_mw,np.nan).astype(float)
    return g,y


def date_draws(frame, n_rep, rng):
    dates=frame.local_date.unique()
    if len(dates)<10:
        raise ValueError("Insufficient independent observed local dates")
    positions=[np.flatnonzero(frame.local_date.to_numpy()==d) for d in dates]
    draws=[]
    for _ in range(n_rep):
        selected=rng.integers(0,len(dates),size=len(dates))
        idx=np.concatenate([positions[int(j)] for j in selected])
        # New FE identifier for every drawn date occurrence, even if repeated.
        day_ids=np.concatenate([np.full(len(positions[int(j)]),k,dtype=int)
                                for k,j in enumerate(selected)])
        draws.append((idx,day_ids))
    return draws


def audit(june,july,baseline,*,replicates=120,seed=20261105):
    if replicates<50:
        raise ValueError("Require at least 50 date-block bootstrap repetitions")
    a,b=validate(june,"June"),validate(july,"July")
    screen,_=common_support(a,b)  # deterministic bin occupancy; frozen across draws
    targets=screen.loc[screen.operating_gross_screen_pass]
    if len(targets)!=6:
        raise ValueError("Previously source-verified six eligible units not conserved")
    if not {"facility_id","epa_unit_id","month","gross_temperature_mw_per_c",
            "gross_model_status"}.issubset(baseline) or len(baseline)!=20:
        raise ValueError("Expected exact source-verified June/July baseline coefficients")
    original=baseline.copy()
    original["facility_id"]=original.facility_id.astype("string").str.strip()
    original["epa_unit_id"]=original.epa_unit_id.astype("string").str.strip()
    if original.duplicated(["facility_id","epa_unit_id","month"]).any():
        raise ValueError("Duplicate regression baseline unit/month")
    records=[]
    for s in targets.itertuples(index=False):
        plant,unit=s.facility_id,s.epa_unit_id
        x=a.loc[a.facility_id.eq(plant)&a.unit_id.eq(unit)]
        y=b.loc[b.facility_id.eq(plant)&b.unit_id.eq(unit)]
        common=set(x[BINS].itertuples(index=False,name=None))&set(
            y[BINS].itertuples(index=False,name=None))
        samples={}
        for month,source in (("June",x),("July",y)):
            g,response=selected_source_month(source,common)
            if len(g)!=(s.june_joint_hours if month=="June" else s.july_joint_hours):
                raise ValueError("Original common-cell source observations changed")
            point=partial_temperature_coef(g,response,g.local_date.to_numpy())
            original_row=original.loc[original.facility_id.eq(plant)&
                                     original.epa_unit_id.eq(unit)&original.month.eq(month)]
            if len(original_row)!=1 or original_row.iloc[0].gross_model_status!="descriptive_ols_only":
                raise ValueError("Missing admitted original source gross model")
            expected=float(original_row.iloc[0].gross_temperature_mw_per_c)
            if point is None or not np.isclose(point,expected,rtol=1e-6,atol=1e-6):
                raise ValueError("Within-date FWL not equivalent to prior source OLS")
            samples[month]=(g,response,point)
        rng=np.random.default_rng(seed+int(plant)+sum(ord(ch) for ch in unit))
        independently_drawn={}
        for month in ("June","July"):
            g,response,point=samples[month]
            independently_drawn[month]=(g,response,date_draws(g,replicates,rng))
        accepted=[]
        for iteration in range(replicates):
            estimates={}
            for month in ("June","July"):
                g,response,draws=independently_drawn[month]
                indexes,ids=draws[iteration]
                selected=g.iloc[indexes].reset_index(drop=True)
                coef=partial_temperature_coef(selected,response[indexes],ids)
                if coef is None or not np.isfinite(coef):
                    break
                estimates[month]=coef
            if len(estimates)==2:
                accepted.append(estimates["July"]-estimates["June"])
        admitted=len(accepted)
        reportable=admitted>=int(np.ceil(.90*replicates))
        low,high=(np.percentile(accepted,[2.5,97.5])
                  if reportable else (np.nan,np.nan))
        difference=samples["July"][2]-samples["June"][2]
        records.append({
            "facility_id":plant,"epa_unit_id":unit,
            "june_gross_valid_original":int(np.isfinite(samples["June"][1]).sum()),
            "july_gross_valid_original":int(np.isfinite(samples["July"][1]).sum()),
            "june_full_source_coef_mw_per_c":samples["June"][2],
            "july_full_source_coef_mw_per_c":samples["July"][2],
            "july_minus_june_coef_mw_per_c":float(difference),
            "paired_date_block_replicates_requested":replicates,
            "paired_date_block_replicates_admitted":admitted,
            "descriptive_2_5_percentile_mw_per_c":float(low),
            "descriptive_97_5_percentile_mw_per_c":float(high),
            "percentile_sensitivity_reportable":bool(reportable),
            "exploratory_span_excludes_zero":bool(reportable and low*high>0)})
    out=pd.DataFrame(records)
    if len(out)!=6:
        raise ValueError("Unexpected observed source-unit cohort")
    manifest={
        "original_source_run":42092282072,
        "original_common_cell_ols_run":42093112865,
        "original_source_months":["2024-06","2024-07"],
        "original_hours_per_unit":{"June":713,"July":737},
        "prespecified_occupied_joint_bins":{
           "era5_temperature_c":2,"srp_demand_mw":500,"mst_local_hour":4},
        "eligible_gross_source_units":6,
        "resampling":"independent within-month complete observed MST date blocks; common bins frozen",
        "bootstrap_replicates":replicates,"seed":seed,
        "admission_fraction_minimum":0.90,
        "source_point_coefficients_fwl_match_prior_ols":True,
        "percentile_intervals_not_validated_confidence_intervals":True,
        "longer_than_day_serial_dependence_unresolved":True,
        "no_independent_site_or_epa_unit_assumption":True,
        "conditional_gross_load_dispatch_selected":True,
        "predictive_holdout_validation_performed":False,
        "causal_thermal_derating_or_generator_available_net_mw_estimated":False,
        "observed_eens_or_forced_outage_calibration_performed":False}
    return out,manifest


def main():
    p=argparse.ArgumentParser()
    for k in ("june-panel","july-panel","baseline","output"):
        p.add_argument("--"+k,required=True)
    p.add_argument("--replicates",type=int,default=120)
    p.add_argument("--seed",type=int,default=20261105)
    args=p.parse_args()
    out,m=audit(
        pd.read_csv(args.june_panel,dtype={"facility_id":"string","unit_id":"string"}),
        pd.read_csv(args.july_panel,dtype={"facility_id":"string","unit_id":"string"}),
        pd.read_csv(args.baseline,dtype={"facility_id":"string","epa_unit_id":"string"}),
        replicates=args.replicates,seed=args.seed)
    dest=Path(args.output);dest.mkdir(parents=True,exist_ok=True)
    out.to_csv(dest/"epa_june_july_common_support_gross_coef_difference_bootstrap.csv",index=False)
    (dest/"epa_june_july_common_support_difference_manifest.json").write_text(
        json.dumps(m,indent=2)+"\n")
    print(out.to_string(index=False))


if __name__=="__main__":
    main()
