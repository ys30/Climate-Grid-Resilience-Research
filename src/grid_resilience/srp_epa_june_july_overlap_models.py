"""Compare June and July EPA source associations on *observed joint support*.

Inputs are independently pinned June and July ERA5/EPA/EIA930 hourly source
panels from real CI 42092282072. Only identical occupied 2°C × 500-MW
BA-demand × 4h MST bins are admitted. Source-specific adjusted OLS diagnostics
are observational, conditional on selected operating records for gross load.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from grid_resilience.srp_epa_june_july_2024_common_support import (
    JUNE_UTC, JULY_UTC, EXPECTED_UNITS, common_support)
from grid_resilience.srp_epa_era5_eia930_temporal_controls import design, fit

KEYS=["facility_id","unit_id"]
BINS=["temp_bin","demand_bin","hour_bin"]
NEEDED={"facility_id","unit_id","timestamp_utc","temperature_2m_c",
        "srp_ba_demand_mw","operating_time","gross_load_mw"}

def validate(df, month):
    if not NEEDED.issubset(df):
        raise ValueError("Missing verified EPA/EIA930/ERA5 source-hour fields")
    x=df.copy()
    x["facility_id"]=x.facility_id.astype("string").str.strip()
    x["unit_id"]=x.unit_id.astype("string").str.strip()
    x["timestamp_utc"]=pd.to_datetime(x.timestamp_utc,utc=True,errors="raise")
    for c in ("temperature_2m_c","srp_ba_demand_mw","operating_time","gross_load_mw"):
        x[c]=pd.to_numeric(x[c],errors="coerce")
    if x.duplicated(KEYS+["timestamp_utc"]).any():
        raise ValueError("Duplicate source unit-hour")
    cohort={str(k):set(v) for k,v in x.groupby("facility_id").unit_id.unique().items()}
    expected=JUNE_UTC if month=="June" else JULY_UTC
    if cohort!=EXPECTED_UNITS or len(x)!=len(expected)*10:
        raise ValueError("Wrong EPA source-unit cohort/UTC source coverage")
    for (_, _),g in x.groupby(KEYS):
        if not pd.DatetimeIndex(g.timestamp_utc.sort_values()).equals(expected):
            raise ValueError("Unverified source month hour grid")
    if not np.isfinite(x[["temperature_2m_c","srp_ba_demand_mw"]].to_numpy(float)).all():
        raise ValueError("Missing ERA5 weather or BA demand")
    if x.srp_ba_demand_mw.lt(0).any() or not x.operating_time.dropna().between(0,1).all():
        raise ValueError("Invalid original BA demand or EPA operating fraction")
    if not np.isfinite(x.gross_load_mw.dropna().to_numpy(float)).all():
        raise ValueError("Nonfinite EPA gross source value")
    return x

def overlap_models(june,july):
    a,b=validate(june,"June"),validate(july,"July")
    support,_=common_support(a,b) # Adds deterministic original joint bin columns.
    rows=[]
    for s in support.itertuples(index=False):
        unit_a=a.loc[a.facility_id.eq(s.facility_id)&a.unit_id.eq(s.epa_unit_id)]
        unit_b=b.loc[b.facility_id.eq(s.facility_id)&b.unit_id.eq(s.epa_unit_id)]
        common=set(unit_a[BINS].itertuples(index=False,name=None))&set(
            unit_b[BINS].itertuples(index=False,name=None))
        for month,g in (("June",unit_a),("July",unit_b)):
            in_bins=g[BINS].apply(tuple,axis=1).isin(common)
            x=g.loc[in_bins].sort_values("timestamp_utc").reset_index(drop=True).copy()
            if len(x)!=(s.june_joint_hours if month=="June" else s.july_joint_hours):
                raise ValueError("Binned source coverage inconsistent")
            x["srp_demand_mw"]=x.srp_ba_demand_mw
            controls,temp=design(x)
            operation=np.where(x.operating_time.notna(),
                               (x.operating_time>0).astype(float),np.nan)
            gross=np.where(x.operating_time.gt(0),x.gross_load_mw,np.nan).astype(float)
            o=fit(operation,controls,temp)
            l=fit(gross,controls,temp)
            observed=operation[np.isfinite(operation)]
            if len(observed)>0 and len(np.unique(observed))==1:
                o={"status":"constant_outcome_no_operational_variation",
                   "n":len(observed),"temp_coef":None,"r2":None}
            if not s.covariate_screen_pass:
                # Do not report coefficients on source cohorts that fail the
                # prespecified overlap eligibility threshold.
                o={"status":"joint_support_screen_failed","n":o["n"],
                   "temp_coef":None,"r2":None}
                l={"status":"joint_support_screen_failed","n":l["n"],
                   "temp_coef":None,"r2":None}
            if not s.operating_gross_screen_pass:
                l={"status":"conditional_gross_support_screen_failed",
                   "n":l["n"],"temp_coef":None,"r2":None}
            rows.append({
              "facility_id":s.facility_id,"epa_unit_id":s.epa_unit_id,
              "month":month,"observed_joint_source_hours":len(x),
              "joint_source_dates":int(x.timestamp_utc.dt.tz_convert(
                  "Etc/GMT+7").dt.normalize().nunique()),
              "joint_reported_positive_operation_hours":int(np.nansum(operation)),
              "joint_conditional_gross_valid_hours":int(np.isfinite(gross).sum()),
              "operating_model_status":o["status"],
              "operating_model_n":o["n"],
              "operating_temperature_lpm_per_c":o["temp_coef"],
              "gross_model_status":l["status"],
              "gross_model_n":l["n"],
              "gross_temperature_mw_per_c":l["temp_coef"],
              "joint_support_screen_pass":bool(s.covariate_screen_pass),
              "joint_conditional_gross_screen_pass":bool(s.operating_gross_screen_pass)
            })
    result=pd.DataFrame(rows)
    if len(result)!=20 or result.groupby("month").size().ne(10).any():
        raise ValueError("Source-month output not conserved")
    pairs=result.pivot(index=["facility_id","epa_unit_id"],columns="month",
                       values=["operating_temperature_lpm_per_c","gross_temperature_mw_per_c"])
    paired=pd.DataFrame({
        "facility_id":pairs.index.get_level_values(0),
        "epa_unit_id":pairs.index.get_level_values(1),
        "june_operation_temp_per_c":pairs[("operating_temperature_lpm_per_c","June")].to_numpy(),
        "july_operation_temp_per_c":pairs[("operating_temperature_lpm_per_c","July")].to_numpy(),
        "june_conditional_gross_temp_mw_per_c":pairs[("gross_temperature_mw_per_c","June")].to_numpy(),
        "july_conditional_gross_temp_mw_per_c":pairs[("gross_temperature_mw_per_c","July")].to_numpy(),
    })
    manifest={
      "months":["2024-06","2024-07"],
      "source_observed_june_hours_per_unit":713,
      "source_observed_july_hours_per_unit":737,
      "identical_ten_epa_source_units":True,
      "common_source_bin_widths":{"temperature_c":2,"srp_ba_demand_mw":500,"mst_hour":4},
      "joint_supported_gross_model_scope_predefined":True,
      "reported_operating_state_not_unit_availability":True,
      "gross_source_mw_not_eia_generator_net_mw":True,
      "source_units_share_site_weather_and_ba_demand":True,
      "within_common_cells_is_not_matching_or_causal_identification":True,
      "time_autocorrelation_robust_inference_estimated":False,
      "predictive_out_of_sample_validation_performed":False,
      "physical_thermal_derating_or_observed_eens_estimated":False
    }
    return result,paired,support,manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--june-panel",required=True)
    p.add_argument("--july-panel",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result,paired,support,m=overlap_models(
        pd.read_csv(a.june_panel,dtype={"facility_id":"string","unit_id":"string"}),
        pd.read_csv(a.july_panel,dtype={"facility_id":"string","unit_id":"string"}))
    path=Path(a.output);path.mkdir(parents=True,exist_ok=True)
    result.to_csv(path/"epa_june_july_joint_support_controlled_ols.csv",index=False)
    paired.to_csv(path/"epa_june_july_joint_support_paired_coefficients.csv",index=False)
    support.to_csv(path/"epa_june_july_source_support_recheck.csv",index=False)
    (path/"epa_june_july_joint_support_ols_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print(result.to_string(index=False))
    print(paired.to_string(index=False))

if __name__=="__main__":
    main()
