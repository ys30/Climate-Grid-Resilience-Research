"""Independent January 2024 EPA/ERA5 source-unit temperature associations.

Uses authentic January SRP EIA-930 UTC hour-start demand with the already
verified January EPA/ERA5 744-local-hour panel. Fits the same exploratory
OLS controls as July, without implying comparable temperature support,
causal identification, or true generator capacity.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from grid_resilience.srp_epa_2024_january_july_observed_seasonal import EXPECTED_UNITS
from grid_resilience.srp_epa_era5_eia930_temporal_controls import design, fit

EXPECTED_UTC = pd.date_range("2024-01-01T07:00:00Z", periods=737, freq="h")


def analyze(january, demand, july_coefficients):
    required = {"facility_id", "unit_id", "timestamp_utc", "temperature_2m_c",
                "operating_time", "gross_load_mw", "observed_utc_month_weather_matched"}
    if not required.issubset(january):
        raise ValueError("Missing certified January EPA ERA5 fields")
    x = january.copy()
    x["facility_id"] = x.facility_id.astype("string").str.strip()
    x["unit_id"] = x.unit_id.astype("string").str.strip()
    x["timestamp_utc"] = pd.to_datetime(x.timestamp_utc, utc=True, errors="raise")
    observed = {str(fac):set(ids) for fac,ids in
                x.groupby("facility_id").unit_id.unique().items()}
    if observed != EXPECTED_UNITS or x.duplicated(["facility_id", "unit_id", "timestamp_utc"]).any():
        raise ValueError("Unexpected January EPA unit identities or duplicate UTC hours")
    if x.observed_utc_month_weather_matched.dtype != bool:
        raise ValueError("January source weather match flag must be boolean")
    for (_, _), group in x.groupby(["facility_id","unit_id"]):
        expected_full = pd.date_range("2024-01-01T07:00:00Z", periods=744, freq="h")
        if not pd.DatetimeIndex(group.timestamp_utc.sort_values()).equals(expected_full):
            raise ValueError("Incomplete January EPA source unit calendar")
    x = x.loc[x.observed_utc_month_weather_matched].copy()
    if len(x)!=7370 or x.groupby(["facility_id","unit_id"]).size().ne(737).any():
        raise ValueError("January weather intersection not exactly 737 per unit")
    for col in ("temperature_2m_c", "operating_time", "gross_load_mw"):
        x[col] = pd.to_numeric(x[col], errors="coerce")
    if not np.isfinite(x.temperature_2m_c.to_numpy(float)).all():
        raise ValueError("January ERA5 temperature not fully observed")
    if not x.operating_time.dropna().between(0,1).all():
        raise ValueError("Invalid January EPA Operating Time")
    if not np.isfinite(x.gross_load_mw.dropna().to_numpy(float)).all():
        raise ValueError("Invalid January EPA source Gross Load")
    needed_demand={"timestamp","ba","demand_mw"}
    if not needed_demand.issubset(demand):
        raise ValueError("Missing official 744h normalized EIA930 January columns")
    d=demand.copy()
    d["timestamp"]=pd.to_datetime(d.timestamp, utc=True, errors="raise")
    if len(d)!=744 or d.timestamp.duplicated().any() or set(d.ba)!={"SRP"}:
        raise ValueError("Official EIA930 January source 744h identity/size invalid")
    full_utc=pd.date_range("2024-01-01T00:00:00Z", periods=744, freq="h")
    if not pd.DatetimeIndex(d.timestamp.sort_values()).equals(full_utc):
        raise ValueError("Official January EIA930 hourly source timestamps incomplete")
    d["srp_demand_mw"]=pd.to_numeric(d.demand_mw,errors="coerce")
    if not np.isfinite(d.srp_demand_mw.to_numpy(float)).all() or d.srp_demand_mw.lt(0).any():
        raise ValueError("Official January demand missing or invalid")
    data=x.merge(d[["timestamp","srp_demand_mw"]],
         left_on="timestamp_utc",right_on="timestamp",how="left",
         indicator=True,validate="many_to_one")
    if not data._merge.eq("both").all():
        raise ValueError("January EPA/ERA5 source hours not fully joined to demand")
    if data.srp_demand_mw.isna().any():
        raise ValueError("Missing matched January SRP demand")
    data=data.drop(columns=["_merge","timestamp"])
    rows=[]
    for (plant,unit),g in data.groupby(["facility_id","unit_id"],sort=True):
        g=g.sort_values("timestamp_utc").reset_index(drop=True)
        if not pd.DatetimeIndex(g.timestamp_utc).equals(EXPECTED_UTC):
            raise ValueError("Unexpected source calendar after 737h join")
        controls,temp=design(g)
        operation=np.where(g.operating_time.notna(),(g.operating_time>0).astype(float),np.nan)
        gross=np.where(g.operating_time.gt(0),g.gross_load_mw,np.nan).astype(float)
        a,b=fit(operation,controls,temp),fit(gross,controls,temp)
        # An all-zero/all-one outcome has no winter operational variation.
        # A numerical zero OLS slope is not an estimable temperature response.
        eligible=operation[np.isfinite(operation)]
        if len(eligible) and np.unique(eligible).size==1:
            a={"status":"constant_outcome_no_operational_variation",
               "temp_coef":None,"r2":None}
        rows.append({
            "facility_id":str(plant),"epa_unit_id":str(unit),
            "source_matched_hours":len(g),
            "source_operating_positive_hours":int(np.nansum(operation)),
            "source_conditional_gross_valid_hours":int(np.isfinite(gross).sum()),
            "mean_era5_temperature_c":float(g.temperature_2m_c.mean()),
            "min_era5_temperature_c":float(g.temperature_2m_c.min()),
            "max_era5_temperature_c":float(g.temperature_2m_c.max()),
            "january_operation_model_status":a["status"],
            "january_operation_temperature_lpm_per_c":a["temp_coef"],
            "january_gross_model_status":b["status"],
            "january_gross_temperature_mw_per_c":b["temp_coef"]})
    result=pd.DataFrame(rows)
    target={"facility_id","epa_unit_id","operation_model_status","gross_load_model_status",
            "operation_lpm_temperature_coefficient_per_c",
            "gross_load_temperature_coefficient_mw_per_c"}
    if not target.issubset(july_coefficients) or len(july_coefficients)!=10:
        raise ValueError("Missing actual July model source results")
    j=july_coefficients.copy()
    j["facility_id"]=j.facility_id.astype("string").str.strip()
    j["epa_unit_id"]=j.epa_unit_id.astype("string").str.strip()
    if j.duplicated(["facility_id","epa_unit_id"]).any():
        raise ValueError("Duplicate July original model source unit")
    joined=result.merge(j[list(target)],on=["facility_id","epa_unit_id"],
         how="left",validate="one_to_one",indicator=True)
    if not joined._merge.eq("both").all():
        raise ValueError("January and July unit source cohorts not identical")
    joined=joined.drop(columns="_merge")
    joined["winter_summer_operating_slope_same_sign_descriptively"]=np.where(
        joined.january_operation_model_status.eq("descriptive_ols_only")&
        joined.operation_model_status.eq("descriptive_ols_only"),
        np.sign(joined.january_operation_temperature_lpm_per_c)==
        np.sign(joined.operation_lpm_temperature_coefficient_per_c),np.nan)
    joined["winter_summer_conditional_gross_slope_same_sign_descriptively"]=np.where(
        joined.january_gross_model_status.eq("descriptive_ols_only")&
        joined.gross_load_model_status.eq("descriptive_ols_only"),
        np.sign(joined.january_gross_temperature_mw_per_c)==
        np.sign(joined.gross_load_temperature_coefficient_mw_per_c),np.nan)
    manifest={
       "months":["2024-01","2024-07"],
       "source_units_identical":10,
       "january_epa_era5_eia930_intersection_hours_per_unit":737,
       "july_model_source_run":41967906150,
       "january_official_eia930_archive_run":41407182014,
       "january_epa_era5_source_run":42072156313,
       "temperature_slope_method":"per-EPA-unit exploratory OLS; SRP BA demand GW + MST hour and date indicators",
       "january_calendar_source_is_not_full_local_month_demand":True,
       "january_gross_conditioned_on_positive_operation":True,
       "unobserved_running_gross_not_imputed":True,
       "seasonal_temperature_support_overlap_not_assumed":True,
       "causal_effect_or_transfer_predictive_validity_claimed":False,
       "generator_thermal_derating_or_net_mw_calibrated":False,
       "actual_outages_or_eens_observed":False
    }
    return joined,manifest


def main():
    parser=argparse.ArgumentParser()
    for key in ("january-panel","january-demand","july-model","output"):
        parser.add_argument("--"+key,required=True)
    a=parser.parse_args()
    result,meta=analyze(
       pd.read_csv(a.january_panel,dtype={"facility_id":"string","unit_id":"string"}),
       pd.read_csv(a.january_demand),
       pd.read_csv(a.july_model,dtype={"facility_id":"string","epa_unit_id":"string"}))
    dest=Path(a.output);dest.mkdir(parents=True,exist_ok=True)
    result.to_csv(dest/"epa_january_july_demand_hour_day_controlled_ols_comparison.csv",index=False)
    (dest/"epa_january_july_controlled_ols_comparison_manifest.json").write_text(
      json.dumps(meta,indent=2)+"\n")
    print(result.to_string(index=False))

if __name__=="__main__":
    main()
