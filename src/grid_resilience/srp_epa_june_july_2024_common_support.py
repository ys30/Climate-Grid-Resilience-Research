"""June versus July 2024 observed EPA–ERA5–EIA930 support screening.

A new independent *shoulder/early-summer* month. Exact MST EPA -> UTC
hours and real UTC June SRP EIA930 reported demand, no imputed boundary.
This does NOT estimate physical generator derating or validate predictive fit.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from grid_resilience.srp_epa_2024_january_july_observed_seasonal import EXPECTED_UNITS
from grid_resilience.srp_epa_jan_jul_common_support import support as prior_support

JUNE_UTC=pd.date_range("2024-06-01T07:00:00Z",periods=713,freq="h")
JUNE_LOCAL_UTC=pd.date_range("2024-06-01T07:00:00Z",periods=720,freq="h")
JULY_UTC=pd.date_range("2024-07-01T07:00:00Z",periods=737,freq="h")

def extract_june(original):
    names=["Facility ID","Unit ID","Date","Hour","Operating Time","Gross Load (MW)"]
    if not set(names).issubset(pd.read_csv(original,nrows=0).columns):
        raise ValueError("Original EPA source lacks expected fields")
    parts=[]
    for block in pd.read_csv(original,usecols=names,dtype="string",chunksize=150000):
        facility=block["Facility ID"].str.strip().str.replace(r"^0+(?=[0-9])","",regex=True)
        x=block.loc[facility.isin(EXPECTED_UNITS) &
                    block.Date.str.contains("2024",na=False)].copy()
        if x.empty:continue
        dates=pd.to_datetime(x.Date,errors="raise")
        x=x.loc[dates.dt.strftime("%Y-%m").eq("2024-06")].copy()
        if not x.empty:
            x["Facility ID"]=facility.loc[x.index]
            parts.append(x)
    if not parts:raise ValueError("Missing June 2024 original EPA source")
    result=pd.concat(parts,ignore_index=True).rename(columns={
        "Facility ID":"facility_id","Unit ID":"unit_id",
        "Date":"local_date","Hour":"local_hour",
        "Operating Time":"operating_time","Gross Load (MW)":"gross_load_mw"})
    return result

def june_demand(h1):
    required={"Balancing Authority","UTC Time at End of Hour","Demand (MW)"}
    if not required.issubset(pd.read_csv(h1,nrows=0).columns):
        raise ValueError("Official H1 EIA930 schema missing")
    chunks=[]
    for part in pd.read_csv(h1,usecols=list(required),dtype="string",chunksize=180000):
        x=part.loc[part["Balancing Authority"].str.strip().eq("SRP")].copy()
        if x.empty:continue
        x["timestamp_utc"]=pd.to_datetime(x["UTC Time at End of Hour"],
            format="%m/%d/%Y %I:%M:%S %p",utc=True,errors="raise")-pd.Timedelta(hours=1)
        x=x.loc[x.timestamp_utc.between("2024-06-01T00:00:00Z",
                                         "2024-06-30T23:00:00Z")]
        if not x.empty:chunks.append(x)
    if not chunks:raise ValueError("No June SRP EIA930 original source rows")
    d=pd.concat(chunks,ignore_index=True)
    expected=pd.date_range("2024-06-01T00:00:00Z",periods=720,freq="h")
    if d.timestamp_utc.duplicated().any() or not pd.DatetimeIndex(
        d.timestamp_utc.sort_values()).equals(expected):
        raise ValueError("Incomplete official EIA930 June 720 UTC hours")
    d["srp_ba_demand_mw"]=pd.to_numeric(d["Demand (MW)"],errors="coerce")
    if not np.isfinite(d.srp_ba_demand_mw.to_numpy(float)).all() or d.srp_ba_demand_mw.lt(0).any():
        raise ValueError("Invalid official June SRP BA demand")
    return d[["timestamp_utc","srp_ba_demand_mw"]].sort_values("timestamp_utc")

def june_join(epa,weather,official_demand):
    a=epa.copy()
    a["facility_id"]=a.facility_id.astype("string").str.strip()
    a["unit_id"]=a.unit_id.astype("string").str.strip()
    identities={str(plant):set(units) for plant,units in
                a.groupby("facility_id").unit_id.unique().items()}
    if identities!=EXPECTED_UNITS:
        raise ValueError("June source EPA unit set inconsistent")
    dates=pd.to_datetime(a.local_date,errors="raise")
    hour=pd.to_numeric(a.local_hour,errors="raise")
    if not dates.dt.strftime("%Y-%m").eq("2024-06").all() or not hour.between(0,23).all():
        raise ValueError("Bad EPA June MST local date/hour")
    a["timestamp_utc"]=(dates+pd.to_timedelta(hour,unit="h")+
                        pd.Timedelta(hours=7)).dt.tz_localize("UTC")
    if a.duplicated(["facility_id","unit_id","timestamp_utc"]).any():
        raise ValueError("Duplicate source EPA local hour")
    for (_, _),g in a.groupby(["facility_id","unit_id"]):
        if not pd.DatetimeIndex(g.timestamp_utc.sort_values()).equals(JUNE_LOCAL_UTC):
            raise ValueError("EPA June source not exactly 720 local hours per unit")
    w=weather.copy()
    w["plant_id"]=w.plant_id.astype("string").str.strip()
    w=w.loc[w.plant_id.isin(EXPECTED_UNITS)&w.technology.eq("gas")].copy()
    w["timestamp_utc"]=pd.to_datetime(w.timestamp_utc,utc=True,errors="raise")
    w["temperature_2m_c"]=pd.to_numeric(w.temperature_2m_c,errors="coerce")
    if set(w.plant_id)!=set(EXPECTED_UNITS) or w.duplicated(["plant_id","timestamp_utc"]).any():
        raise ValueError("Missing/duplicate original ERA5 June site")
    expected=pd.date_range("2024-06-01T00:00:00Z",periods=720,freq="h")
    for site,group in w.groupby("plant_id"):
        if not pd.DatetimeIndex(group.timestamp_utc.sort_values()).equals(expected):
            raise ValueError("Incomplete observed June ERA5 calendar")
    if not np.isfinite(w.temperature_2m_c.to_numpy(float)).all():
        raise ValueError("Missing June ERA5 source temperature")
    a=a.merge(w[["plant_id","timestamp_utc","temperature_2m_c"]],
       left_on=["facility_id","timestamp_utc"],right_on=["plant_id","timestamp_utc"],
       how="left",indicator=True,validate="many_to_one")
    a["observed_june_weather_matched"]=a._merge.eq("both")
    a=a.drop(columns=["plant_id","_merge"])
    if len(a)!=7200 or a.observed_june_weather_matched.sum()!=7130:
        raise ValueError("Wrong June 713/720 UTC month weather gate")
    a=a.loc[a.observed_june_weather_matched].copy()
    for col in ("operating_time","gross_load_mw"):
        a[col]=pd.to_numeric(a[col],errors="coerce")
        if not np.isfinite(a[col].dropna().to_numpy(float)).all():
            raise ValueError("Invalid EPA gross/operating source data")
    if not a.operating_time.dropna().between(0,1).all():
        raise ValueError("Invalid source Operating Time")
    a=a.merge(official_demand,on="timestamp_utc",how="left",
              validate="many_to_one",indicator=True)
    if not a._merge.eq("both").all():
        raise ValueError("June weather hour missing actual EIA930 demand")
    a=a.drop(columns="_merge")
    for (_, _),g in a.groupby(["facility_id","unit_id"]):
        if not pd.DatetimeIndex(g.timestamp_utc.sort_values()).equals(JUNE_UTC):
            raise ValueError("Wrong original June overlap time calendar")
    return a

def july_join(epa,july_demand):
    a=epa.copy()
    needed={"facility_id","unit_id","timestamp_utc","temperature_2m_c",
           "operating_time","gross_load_mw","era5_full_local_july_matched"}
    if not needed.issubset(a) or not a.era5_full_local_july_matched.eq(True).all():
        raise ValueError("Missing genuine full July EPA ERA5 source")
    a["facility_id"]=a.facility_id.astype("string").str.strip()
    a["unit_id"]=a.unit_id.astype("string").str.strip()
    a["timestamp_utc"]=pd.to_datetime(a.timestamp_utc,utc=True)
    a=a.loc[a.timestamp_utc.dt.strftime("%Y-%m").eq("2024-07")].copy()
    if len(a)!=7370 or a.duplicated(["facility_id","unit_id","timestamp_utc"]).any():
        raise ValueError("Incomplete source July unit hours")
    e=july_demand.copy()
    columns={"UTC Time at End of Hour","Balancing Authority","Demand (MW)"}
    if not columns.issubset(e):raise ValueError("Missing official July EIA source")
    e=e.loc[e["Balancing Authority"].astype("string").str.strip().eq("SRP")].copy()
    e["timestamp_utc"]=pd.to_datetime(e["UTC Time at End of Hour"],
        format="%m/%d/%Y %I:%M:%S %p",utc=True)-pd.Timedelta(hours=1)
    e["srp_ba_demand_mw"]=pd.to_numeric(e["Demand (MW)"],errors="coerce")
    expected=pd.date_range("2024-07-01T00:00:00Z",periods=744,freq="h")
    if len(e)!=744 or e.timestamp_utc.duplicated().any() or not pd.DatetimeIndex(
        e.timestamp_utc.sort_values()).equals(expected):
        raise ValueError("July EIA demand 744 source UTC hours required")
    if not np.isfinite(e.srp_ba_demand_mw.to_numpy(float)).all():
        raise ValueError("July EIA demand missing")
    a=a.merge(e[["timestamp_utc","srp_ba_demand_mw"]],
              on="timestamp_utc",how="left",validate="many_to_one",indicator=True)
    if not a._merge.eq("both").all():raise ValueError("Missing actual July EIA demand")
    a=a.drop(columns="_merge")
    for (_, _),g in a.groupby(["facility_id","unit_id"]):
        if not pd.DatetimeIndex(g.timestamp_utc.sort_values()).equals(JULY_UTC):
            raise ValueError("July source UTC overlap source incomplete")
    for col in ("temperature_2m_c","operating_time","gross_load_mw"):
        a[col]=pd.to_numeric(a[col],errors="coerce")
    return a

def common_support(june,july):
    results=[]
    levels=["temp_bin","demand_bin","hour_bin"]
    for x in (june,july):
        local=x.timestamp_utc.dt.tz_convert("Etc/GMT+7")
        x["local_day"]=local.dt.strftime("%Y-%m-%d")
        x["temp_bin"]=np.floor(x.temperature_2m_c/2).astype(int)
        x["demand_bin"]=np.floor(x.srp_ba_demand_mw/500).astype(int)
        x["hour_bin"]=(local.dt.hour//4).astype(int)
    for site,units in EXPECTED_UNITS.items():
        for unit in sorted(units):
            a=june.loc[june.facility_id.eq(site)&june.unit_id.eq(unit)]
            b=july.loc[july.facility_id.eq(site)&july.unit_id.eq(unit)]
            if len(a)!=713 or len(b)!=737:
                raise ValueError("June/July EPA source hour conservation failure")
            shared=set(a[levels].itertuples(index=False,name=None)) & set(
                b[levels].itertuples(index=False,name=None))
            x=a[levels].apply(tuple,axis=1).isin(shared)
            y=b[levels].apply(tuple,axis=1).isin(shared)
            run_a=a.operating_time.gt(0)&a.gross_load_mw.notna()
            run_b=b.operating_time.gt(0)&b.gross_load_mw.notna()
            tlo=max(a.temperature_2m_c.min(),b.temperature_2m_c.min())
            thi=min(a.temperature_2m_c.max(),b.temperature_2m_c.max())
            dlo=max(a.srp_ba_demand_mw.min(),b.srp_ba_demand_mw.min())
            dhi=min(a.srp_ba_demand_mw.max(),b.srp_ba_demand_mw.max())
            screen=bool(
                len(shared)>0 and int(x.sum())>=80 and int(y.sum())>=80
                and a.loc[x,"local_day"].nunique()>=10
                and b.loc[y,"local_day"].nunique()>=10)
            results.append({
                "facility_id":site,"epa_unit_id":unit,
                "june_hours":len(a),"july_hours":len(b),
                "june_temp_min_c":float(a.temperature_2m_c.min()),
                "june_temp_max_c":float(a.temperature_2m_c.max()),
                "july_temp_min_c":float(b.temperature_2m_c.min()),
                "july_temp_max_c":float(b.temperature_2m_c.max()),
                "continuous_temperature_ranges_overlap":bool(tlo<=thi),
                "temperature_overlap_width_c":float(max(0,thi-tlo)),
                "demand_ranges_overlap":bool(dlo<=dhi),
                "shared_2c_500mw_4h_cells":len(shared),
                "june_joint_hours":int(x.sum()),
                "july_joint_hours":int(y.sum()),
                "june_joint_dates":int(a.loc[x,"local_day"].nunique()),
                "july_joint_dates":int(b.loc[y,"local_day"].nunique()),
                "june_joint_reported_operating_gross_hours":int((x&run_a).sum()),
                "july_joint_reported_operating_gross_hours":int((y&run_b).sum()),
                "covariate_screen_pass":screen,
                "operating_gross_screen_pass":bool(screen and
                    (x&run_a).sum()>=80 and (y&run_b).sum()>=80)})
    out=pd.DataFrame(results)
    if len(out)!=10:raise ValueError("Expected ten unit support diagnostics")
    manifest={
      "analysis":"2024 real June-versus-July EPA unit ERA5 EIA930 support",
      "june_local_source_hours_per_unit":720,
      "june_utc_month_matched_hours_per_unit":713,
      "july_utc_month_matched_hours_per_unit":737,
      "june_utc_july_boundary_hours_excluded_per_unit":7,
      "temperature_bin_c":2,"demand_bin_mw":500,"local_hour_bin_h":4,
      "minimum_source_joint_hours_each_month":80,
      "minimum_joint_dates_each_month":10,
      "screened_units_not_statistically_independent_weather":True,
      "bin_screen_not_proof_of_conditional_overlap":True,
      "temperature_effect_or_transfer_predictive_validity_identified":False,
      "generator_thermal_derating_or_eens_inferred":False,
      "unobserved_utc_boundary_demand_imputed":False,
    }
    return out,manifest

def main():
    p=argparse.ArgumentParser()
    for key in ("epa-original","june-era5","june-eia930-h1",
                "july-panel","july-demand","output"):
        p.add_argument("--"+key,required=True)
    args=p.parse_args()
    source=extract_june(args.epa_original)
    eia=june_demand(args.june_eia930_h1)
    june=june_join(source,pd.read_csv(args.june_era5,dtype={"plant_id":"string"}),eia)
    july=july_join(pd.read_csv(args.july_panel,dtype={"facility_id":"string","unit_id":"string"}),
                   pd.read_csv(args.july_demand,dtype="string"))
    result,meta=common_support(june,july)
    folder=Path(args.output);folder.mkdir(parents=True,exist_ok=True)
    # Retain the small, observed, joined source-hour panels for reproducible
    # holdout diagnostics without downloading the 183MB EPA archive again.
    keep=["facility_id","unit_id","timestamp_utc","temperature_2m_c",
          "operating_time","gross_load_mw","srp_ba_demand_mw"]
    assert len(june)==7130 and len(july)==7370
    june[keep].sort_values(["facility_id","unit_id","timestamp_utc"]).to_csv(
        folder/"june_2024_epa_era5_eia930_verified_unit_hours.csv",index=False)
    july[keep].sort_values(["facility_id","unit_id","timestamp_utc"]).to_csv(
        folder/"july_2024_epa_era5_eia930_verified_unit_hours.csv",index=False)
    result.to_csv(folder/"srp_epa_june_july_joint_common_support.csv",index=False)
    (folder/"srp_epa_june_july_common_support_manifest.json").write_text(
        json.dumps(meta,indent=2)+"\n")
    print(result.to_string(index=False))

if __name__=="__main__":
    main()
