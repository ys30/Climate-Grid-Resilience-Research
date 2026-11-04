"""Reproducible January/July source-identity-matched ERA5 thermal-plant exposure.

Only the site intersection is comparable. Source EIA860 generator nameplate
must agree across months. A temperature threshold describes WEATHER, never
generator derating, outages, or causal climate-change effects.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

THRESHOLDS_C=(35.,40.)


def _validate(data, *, month, year=2024):
    required={"timestamp_utc","technology","plant_id","temperature_2m_c","selected_nameplate_mw"}
    if not required.issubset(data):
        raise ValueError("Missing source ERA5 plant-hour columns")
    x=data.copy()
    x["plant_id"]=x.plant_id.astype("string").str.strip().str.replace(
        r"^0+(?=[0-9])","",regex=True)
    x["technology"]=x.technology.astype("string").str.strip()
    if x.plant_id.isna().any() or x.plant_id.eq("").any():
        raise ValueError("Invalid source plant ID")
    if not set(x.technology.unique()).issubset({"gas","coal"}):
        raise ValueError("Unrecognized thermal source class")
    x["timestamp_utc"]=pd.to_datetime(x.timestamp_utc,errors="raise",utc=True)
    for field in ("temperature_2m_c","selected_nameplate_mw"):
        x[field]=pd.to_numeric(x[field],errors="coerce")
    if x.duplicated(["technology","plant_id","timestamp_utc"]).any():
        raise ValueError("Duplicate source plant-hour")
    if not np.isfinite(x[["temperature_2m_c","selected_nameplate_mw"]].to_numpy(float)).all():
        raise ValueError("Missing or nonfinite source weather/nameplate")
    if (x.selected_nameplate_mw<=0).any() or not x.temperature_2m_c.between(-100,70).all():
        raise ValueError("Invalid physical source range")
    expected=pd.date_range(f"{year}-{month:02d}-01",
                           periods=pd.Period(f"{year}-{month:02d}").days_in_month*24,
                           freq="h",tz="UTC")
    for key,frame in x.groupby(["technology","plant_id"]):
        if not pd.DatetimeIndex(frame.timestamp_utc.sort_values()).equals(expected):
            raise ValueError(f"Incomplete UTC source weather for {key}")
        if frame.selected_nameplate_mw.nunique()!=1:
            raise ValueError("Changing capacity within source month")
    return x


def compare(january,july):
    jan=_validate(january,month=1)
    jul=_validate(july,month=7)
    keys=["technology","plant_id"]
    ja=jan.groupby(keys,as_index=False).selected_nameplate_mw.first()
    ju=jul.groupby(keys,as_index=False).selected_nameplate_mw.first()
    match=ja.merge(ju,on=keys,how="inner",validate="one_to_one",suffixes=("_jan","_jul"))
    if match.empty or set(match.technology)!={"gas","coal"}:
        raise ValueError("Matched January/July gas and coal sites required")
    if not np.allclose(match.selected_nameplate_mw_jan,match.selected_nameplate_mw_jul,atol=1e-5,rtol=0):
        raise ValueError("Source annual nameplate differs for matched plant")
    both=[]
    plant_rows=[]
    for month,x in (("January",jan),("July",jul)):
        d=x.merge(match[keys],on=keys,how="inner",validate="many_to_one")
        for (tech,plant),f in d.groupby(keys):
            plant_rows.append({"month":month,"technology":tech,"plant_id":plant,
                               "nameplate_mw":float(f.selected_nameplate_mw.iloc[0]),
                               "mean_temperature_c":float(f.temperature_2m_c.mean()),
                               "hours_ge_35_c":int((f.temperature_2m_c>=35).sum()),
                               "hours_ge_40_c":int((f.temperature_2m_c>=40).sum())})
        weighted=d.assign(weighted_c=d.temperature_2m_c*d.selected_nameplate_mw)
        agg=weighted.groupby(["technology","timestamp_utc"],as_index=False).agg(
            weighted_c=("weighted_c","sum"),nameplate_mw=("selected_nameplate_mw","sum"))
        agg["capacity_weighted_temperature_c"]=agg.weighted_c/agg.nameplate_mw
        agg["month"]=month
        both.append(agg.drop(columns="weighted_c"))
    hourly=pd.concat(both,ignore_index=True)
    summary=[]
    for (month,tech),group in hourly.groupby(["month","technology"]):
        temps=group.capacity_weighted_temperature_c
        summary.append({"month":month,"technology":tech,"matched_plant_count":int(
            match.technology.eq(tech).sum()),"matched_nameplate_mw":float(
            match.loc[match.technology.eq(tech),"selected_nameplate_mw_jan"].sum()),
            "hours":len(group),"capacity_weighted_mean_temp_c":float(temps.mean()),
            "capacity_weighted_max_hourly_temp_c":float(temps.max()),
            "capacity_weighted_min_hourly_temp_c":float(temps.min()),
            "weighted_fleet_hours_ge_35_c":int((temps>=35).sum()),
            "weighted_fleet_hours_ge_40_c":int((temps>=40).sum())})
    table=pd.DataFrame(summary).sort_values(["technology","month"])
    pairs=table.pivot(index="technology",columns="month",values="capacity_weighted_mean_temp_c")
    differences=(pairs.July-pairs.January).rename("july_minus_january_mean_temp_c").reset_index()
    manifest={"year":2024,"source_months":["2024-01","2024-07"],
        "matched_gas_plants":int(match.technology.eq("gas").sum()),
        "matched_coal_plants":int(match.technology.eq("coal").sum()),
        "matched_gas_nameplate_mw":float(match.loc[match.technology.eq("gas"),"selected_nameplate_mw_jan"].sum()),
        "july_only_gas_plants":int(len(ju.loc[ju.technology.eq("gas")])-match.technology.eq("gas").sum()),
        "hours_per_source_month":744,
        "source_population_identical_for_month_comparison":True,
        "source_is_era5_reanalysis_at_eia860_plant_point":True,
        "thermal_derating_calibrated":False,
        "historical_reliability_calibrated":False,
        "climate_change_trend_estimated":False}
    return table,hourly,pd.DataFrame(plant_rows),differences,manifest


def main():
    p=argparse.ArgumentParser()
    for key in ("january","july","output"):p.add_argument("--"+key,required=True)
    args=p.parse_args()
    t,h,plants,delta,m=compare(pd.read_csv(args.january,dtype={"plant_id":"string"}),
                                pd.read_csv(args.july,dtype={"plant_id":"string"}))
    root=Path(args.output);root.mkdir(parents=True,exist_ok=True)
    t.to_csv(root/"matched_seasonal_technology_summary.csv",index=False)
    h.to_csv(root/"matched_seasonal_technology_hourly.csv",index=False)
    plants.to_csv(root/"matched_seasonal_plant_summary.csv",index=False)
    delta.to_csv(root/"matched_seasonal_mean_differences.csv",index=False)
    (root/"matched_seasonal_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print(t.to_string(index=False))
    print(delta.to_string(index=False))


if __name__=="__main__":
    main()
