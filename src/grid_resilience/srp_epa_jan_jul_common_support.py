"""Fail-closed January/July EPA–ERA5–EIA930 common-support diagnostic.

Same 10 EPA unit identities, different source UTC months, 737 hours per unit.
The 2D rectangle is necessary but NOT sufficient for overlap; additionally
intersect prespecified 2°C × 500-MW × 4h local-hour occupied bins. No source
interpolation, matching, causal effect or transferred regression is asserted.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from grid_resilience.srp_epa_2024_january_july_observed_seasonal import EXPECTED_UNITS

MONTHS={"January":("2024-01-01T07:00:00Z","2024-01-31T23:00:00Z"),
        "July":("2024-07-01T07:00:00Z","2024-07-31T23:00:00Z")}


def admitted_panel(df, month, demand):
    x=df.copy()
    required={"facility_id","unit_id","timestamp_utc","temperature_2m_c",
              "operating_time","gross_load_mw"}
    if not required.issubset(x):
        raise ValueError("Incomplete EPA/ERA5 source schema")
    x["facility_id"]=x.facility_id.astype("string").str.strip()
    x["unit_id"]=x.unit_id.astype("string").str.strip()
    x["timestamp_utc"]=pd.to_datetime(x.timestamp_utc,utc=True,errors="raise")
    if x.duplicated(["facility_id","unit_id","timestamp_utc"]).any():
        raise ValueError("Duplicate EPA source hour")
    if month=="January":
        if "observed_utc_month_weather_matched" not in x or x.observed_utc_month_weather_matched.dtype!=bool:
            raise ValueError("Uncertified January ERA5 weather coverage")
        if not x.observed_utc_month_weather_matched.sum()==7370:
            raise ValueError("January weather coverage differs")
        x=x.loc[x.observed_utc_month_weather_matched].copy()
    elif month=="July":
        if "era5_full_local_july_matched" not in x or x.era5_full_local_july_matched.dtype!=bool:
            raise ValueError("Uncertified July ERA5 source")
        if not x.era5_full_local_july_matched.all():
            raise ValueError("July weather not fully source matched")
        x=x.loc[x.timestamp_utc.dt.strftime("%Y-%m").eq("2024-07")].copy()
    else:
        raise ValueError("Unsupported source month")
    expected=pd.date_range(MONTHS[month][0],periods=737,freq="h")
    ids={str(plant):set(unitids) for plant,unitids in
         x.groupby("facility_id").unit_id.unique().items()}
    if ids!=EXPECTED_UNITS or len(x)!=7370:
        raise ValueError("Unexpected common source-unit cohort")
    for (_, _),g in x.groupby(["facility_id","unit_id"]):
        if not pd.DatetimeIndex(g.timestamp_utc.sort_values()).equals(expected):
            raise ValueError("Incomplete source UTC-month intersection")
    for col in ("temperature_2m_c","operating_time","gross_load_mw"):
        x[col]=pd.to_numeric(x[col],errors="coerce")
    if not np.isfinite(x.temperature_2m_c.to_numpy(dtype=float)).all():
        raise ValueError("Missing/nonfinite measured ERA5 source weather")
    if not x.operating_time.dropna().between(0,1).all():
        raise ValueError("Operating Time out of bounds")
    if not np.isfinite(x.gross_load_mw.dropna().to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite source gross MW")
    d=demand.copy()
    if month=="January":
        if not {"timestamp","ba","demand_mw"}.issubset(d):
            raise ValueError("Missing official January EIA930 fields")
        d["timestamp_utc"]=pd.to_datetime(d.timestamp,utc=True,errors="raise")
        if len(d)!=744 or set(d.ba)!={"SRP"}:
            raise ValueError("Incorrect official January BA source")
        d["value_mw"]=pd.to_numeric(d.demand_mw,errors="coerce")
    else:
        fields={"Balancing Authority","UTC Time at End of Hour","Demand (MW)"}
        if not fields.issubset(d):
            raise ValueError("Missing official July EIA930 fields")
        d=d.loc[d["Balancing Authority"].astype("string").str.strip().eq("SRP")].copy()
        d["timestamp_utc"]=pd.to_datetime(
            d["UTC Time at End of Hour"],utc=True,format="%m/%d/%Y %I:%M:%S %p",
            errors="raise")-pd.Timedelta(hours=1)
        d["value_mw"]=pd.to_numeric(d["Demand (MW)"],errors="coerce")
    expected_744=pd.date_range(f"2024-{1 if month=='January' else 7:02d}-01T00:00:00Z",
                               periods=744,freq="h")
    if d.timestamp_utc.duplicated().any() or len(d)!=744 or not pd.DatetimeIndex(
            d.timestamp_utc.sort_values()).equals(expected_744):
        raise ValueError("Official EIA930 744 UTC month source incomplete or duplicated")
    if not np.isfinite(d.value_mw.to_numpy(float)).all() or d.value_mw.lt(0).any():
        raise ValueError("Missing/invalid official BA demand")
    x=x.merge(d[["timestamp_utc","value_mw"]],on="timestamp_utc",
              how="left",validate="many_to_one",indicator=True)
    if not x._merge.eq("both").all():
        raise ValueError("Missing observed EIA930 demand at EPA UTC intersection")
    x=x.drop(columns="_merge").rename(columns={"value_mw":"srp_ba_demand_mw"})
    local=x.timestamp_utc.dt.tz_convert("Etc/GMT+7")
    x["local_date"]=local.dt.strftime("%Y-%m-%d")
    x["local_hour"]=local.dt.hour
    x["temperature_bin_2c"]=np.floor(x.temperature_2m_c/2).astype(int)
    x["demand_bin_500mw"]=np.floor(x.srp_ba_demand_mw/500).astype(int)
    x["hour_bin_4h"]=(x.local_hour//4).astype(int)
    return x


def support(january,july):
    keys=["facility_id","unit_id"]
    summaries=[]
    for (plant,unit),a in january.groupby(keys,sort=True):
        b=july.loc[july.facility_id.eq(plant)&july.unit_id.eq(unit)]
        if len(a)!=737 or len(b)!=737:
            raise ValueError("Unbalanced same-unit source cohorts")
        tlo=max(a.temperature_2m_c.min(),b.temperature_2m_c.min())
        thi=min(a.temperature_2m_c.max(),b.temperature_2m_c.max())
        dlo=max(a.srp_ba_demand_mw.min(),b.srp_ba_demand_mw.min())
        dhi=min(a.srp_ba_demand_mw.max(),b.srp_ba_demand_mw.max())
        temp_support=tlo<=thi
        demand_support=dlo<=dhi
        joint_rect=bool(temp_support and demand_support)
        levels=["temperature_bin_2c","demand_bin_500mw","hour_bin_4h"]
        set_a=set(map(tuple,a[levels].itertuples(index=False,name=None)))
        set_b=set(map(tuple,b[levels].itertuples(index=False,name=None)))
        shared=set_a&set_b
        in_a=a[levels].apply(tuple,axis=1).isin(shared)
        in_b=b[levels].apply(tuple,axis=1).isin(shared)
        # Separate observed operational support rather than quietly assuming
        # a positive-operating gross-load response exists at matched conditions.
        operation_a=a.operating_time.gt(0)
        operation_b=b.operating_time.gt(0)
        running_a=int((in_a&operation_a).sum())
        running_b=int((in_b&operation_b).sum())
        gross_a=int((in_a&operation_a&a.gross_load_mw.notna()).sum())
        gross_b=int((in_b&operation_b&b.gross_load_mw.notna()).sum())
        common_a=int(in_a.sum())
        common_b=int(in_b.sum())
        # Conservative prespecified descriptive screening conditions.
        admitted=bool(
            joint_rect and common_a>=80 and common_b>=80 and
            a.loc[in_a,"local_date"].nunique()>=10 and
            b.loc[in_b,"local_date"].nunique()>=10)
        gross_admitted=bool(admitted and gross_a>=80 and gross_b>=80)
        summaries.append({
          "facility_id":str(plant),"epa_unit_id":str(unit),
          "january_source_hours":737,"july_source_hours":737,
          "january_temperature_min_c":float(a.temperature_2m_c.min()),
          "january_temperature_max_c":float(a.temperature_2m_c.max()),
          "july_temperature_min_c":float(b.temperature_2m_c.min()),
          "july_temperature_max_c":float(b.temperature_2m_c.max()),
          "temperature_range_overlap_c":float(max(0,thi-tlo)),
          "temperature_ranges_intersect":bool(temp_support),
          "january_demand_min_mw":float(a.srp_ba_demand_mw.min()),
          "january_demand_max_mw":float(a.srp_ba_demand_mw.max()),
          "july_demand_min_mw":float(b.srp_ba_demand_mw.min()),
          "july_demand_max_mw":float(b.srp_ba_demand_mw.max()),
          "demand_ranges_intersect":bool(demand_support),
          "joint_temperature_demand_rectangle_intersects":joint_rect,
          "shared_2c_500mw_4h_bins":len(shared),
          "january_joint_cell_covered_hours":common_a,
          "july_joint_cell_covered_hours":common_b,
          "january_joint_cell_covered_dates":int(a.loc[in_a,"local_date"].nunique()),
          "july_joint_cell_covered_dates":int(b.loc[in_b,"local_date"].nunique()),
          "january_shared_bin_positive_operation_hours":running_a,
          "july_shared_bin_positive_operation_hours":running_b,
          "january_shared_bin_reported_gross_hours":gross_a,
          "july_shared_bin_reported_gross_hours":gross_b,
          "descriptive_covariate_common_support_screen_pass":admitted,
          "descriptive_running_gross_support_screen_pass":gross_admitted
        })
    result=pd.DataFrame(summaries)
    if len(result)!=10 or result.january_source_hours.sum()!=7370:
        raise ValueError("Source conservation failed")
    manifest={
       "source_utc_month_intersection_hours_per_unit":737,
       "source_units":10,
       "temperature_bin_width_c":2,
       "demand_bin_width_mw":500,
       "local_hour_bin_width_h":4,
       "joint_cell_definition":"exact occupancy in 2C by 500-MW by 4h same-bin cells",
       "covariate_screen_hours_min_each_month":80,
       "covariate_screen_dates_min_each_month":10,
       "conditional_gross_min_source_observations_each_month":80,
       "screen_is_not_a_proof_of_conditional_exchangeability":True,
       "support_screen_only_not_model_fit":True,
       "causal_temperature_derating_or_eens_claimed":False,
       "weather_imputation_or_matching":False,
       "interpolated_missing_eia930_hours":False,
       "ecmps_physical_generator_electrical_identity_admitted":False,
       "gross_load_is_not_available_net_power":True
    }
    return result,manifest


def audit(january,jan_demand,july,jul_demand):
    a=admitted_panel(january,"January",jan_demand)
    b=admitted_panel(july,"July",jul_demand)
    return support(a,b)


def main():
    p=argparse.ArgumentParser()
    for item in ("january-panel","january-demand","july-panel","july-demand","output"):
        p.add_argument("--"+item,required=True)
    a=p.parse_args()
    result,manifest=audit(
        pd.read_csv(a.january_panel,dtype={"facility_id":"string","unit_id":"string"}),
        pd.read_csv(a.january_demand),
        pd.read_csv(a.july_panel,dtype={"facility_id":"string","unit_id":"string"}),
        pd.read_csv(a.july_demand,dtype="string"))
    dst=Path(a.output);dst.mkdir(parents=True,exist_ok=True)
    result.to_csv(dst/"epa_jan_jul_joint_covariate_support_audit.csv",index=False)
    (dst/"epa_jan_jul_joint_support_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print(result.to_string(index=False))

if __name__=="__main__":
    main()
