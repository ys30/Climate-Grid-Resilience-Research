"""Monthly EIA923 Page4 reporting coverage versus matched ERA5 site temperatures.

EIA-923 Page4 source-reported BA and EIA-860 Plant-BA are different grains;
a month-reported net output/nameplate-hour ratio is NOT availability,
temperature derating, generator operating efficiency, hourly performance
or causal effect. Keep missing plants in the coverage denominator.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

MONTHS={"2024-01":"January","2024-07":"July"}
SOURCE_KEYS=("plant_id","generator_id","reported_ba","period")


def analyze(sites,monthly_generation,plant_weather):
    required_sites={"technology","plant_id","nameplate_mw"}
    required_g={"plant_id","generator_id","reported_ba","period","generation_mwh"}
    required_w={"timestamp_utc","technology","plant_id","temperature_2m_c"}
    if not required_sites.issubset(sites) or not required_g.issubset(monthly_generation) or not required_w.issubset(plant_weather):
        raise ValueError("Missing required source fields")
    s=sites[list(required_sites)].copy()
    g=monthly_generation.copy()
    w=plant_weather.copy()
    for frame in (s,g,w):
        frame["plant_id"]=frame.plant_id.astype("string").str.strip().str.replace(
            r"^0+(?=[0-9])","",regex=True)
        if frame.plant_id.isna().any() or frame.plant_id.eq("").any():
            raise ValueError("Missing source plant ID")
    if s.duplicated(["technology","plant_id"]).any() or s.plant_id.duplicated().any():
        raise ValueError("Duplicated EIA860 plant identity")
    if set(s.technology)!={"gas","coal"}:
        raise ValueError("Expected gas and coal source plant categories")
    s["nameplate_mw"]=pd.to_numeric(s.nameplate_mw,errors="coerce")
    if not np.isfinite(s.nameplate_mw.to_numpy(float)).all() or s.nameplate_mw.le(0).any():
        raise ValueError("Invalid EIA860 source capacity")
    g["generator_id"]=g.generator_id.astype("string").str.strip()
    g["period"]=g.period.astype("string").str.strip()
    g["reported_ba"]=g.reported_ba.astype("string").str.strip()
    if g.generator_id.isna().any() or g.generator_id.eq("").any():
        raise ValueError("Missing generator ID")
    g=g.loc[g.reported_ba.eq("SRP") & g.period.isin(MONTHS)].copy()
    if g.duplicated(list(SOURCE_KEYS)).any():
        raise ValueError("Duplicate EIA923 reported BA generator-month")
    g["generation_mwh"]=pd.to_numeric(g.generation_mwh,errors="coerce")
    if not np.isfinite(g.generation_mwh.to_numpy(float)).all():
        raise ValueError("Nonfinite reported Page4 generation")
    w["timestamp_utc"]=pd.to_datetime(w.timestamp_utc,utc=True,errors="raise")
    w["temperature_2m_c"]=pd.to_numeric(w.temperature_2m_c,errors="coerce")
    if not np.isfinite(w.temperature_2m_c.to_numpy(float)).all():
        raise ValueError("Missing ERA5 temperatures")
    if w.duplicated(["technology","plant_id","timestamp_utc"]).any():
        raise ValueError("Duplicate ERA5 source site-hour")
    for (tech,plant),frame in w.groupby(["technology","plant_id"]):
        if (tech,str(plant)) not in set(zip(s.technology,s.plant_id)):
            raise ValueError("Weather site not in annual EIA860 source scope")
        expected=pd.date_range("2024-07-01",periods=744,freq="h",tz="UTC")
        if not pd.DatetimeIndex(frame.timestamp_utc.sort_values()).equals(expected):
            raise ValueError("Missing/shifted July ERA5 site hours")
    if len(w)!=744*len(s):
        raise ValueError("Incomplete weather site population")
    weather=w.groupby(["technology","plant_id"],as_index=False).agg(
        july_avg_era5_temperature_c=("temperature_2m_c","mean"),
        july_hours_ge_35_c=("temperature_2m_c",lambda x:int(x.ge(35).sum())),
        july_hours_ge_40_c=("temperature_2m_c",lambda x:int(x.ge(40).sum())))
    perplant=g.groupby(["period","plant_id"],as_index=False).agg(
        page4_month_signed_net_mwh=("generation_mwh","sum"),
        page4_reported_generator_count=("generator_id","nunique"))
    # Cross the annual plant cohort with two target months to keep unreported
    # plants as explicit missing values, NEVER as zero generation.
    universe=pd.MultiIndex.from_product([list(MONTHS),s.plant_id],
        names=["period","plant_id"]).to_frame(index=False)
    rows=universe.merge(s,on="plant_id",validate="many_to_one").merge(
        perplant,on=["period","plant_id"],how="left",validate="one_to_one").merge(
        weather,on=["technology","plant_id"],validate="many_to_one")
    rows["page4_month_reported"]=rows.page4_reported_generator_count.notna()
    rows["descriptive_net_output_over_nameplate_hours"]=(
        rows.page4_month_signed_net_mwh/(rows.nameplate_mw*744))
    summary=[]
    for (month,tech),frame in rows.groupby(["period","technology"]):
        matched=frame.loc[frame.page4_month_reported]
        summary.append({
            "period":month,"technology":tech,
            "annual_source_plants":int(len(frame)),
            "page4_reported_plant_count":int(len(matched)),
            "page4_absent_plant_count":int(len(frame)-len(matched)),
            "annual_source_nameplate_mw":float(frame.nameplate_mw.sum()),
            "page4_matched_annual_nameplate_mw":float(matched.nameplate_mw.sum()),
            "page4_nameplate_coverage_fraction":float(
                matched.nameplate_mw.sum()/frame.nameplate_mw.sum()),
            "page4_reported_signed_net_mwh":float(matched.page4_month_signed_net_mwh.sum()),
            "month_is_complete_for_annual_plant_cohort":bool(len(matched)==len(frame)),
        })
    summaries=pd.DataFrame(summary)
    manifest={
        "periods":list(MONTHS),
        "era5_weather_month":"2024-07",
        "page4_reporting_scope":"EIA923 Page4 generator month, reported BA=SRP",
        "eia860_source_scope":"EIA860 2024 annual Plant BA SRP eligible gas/coal plant sites",
        "page4_generator_reported_net_mwh_preserve_signed_values":True,
        "unreported_monthly_generation_is_missing_not_zero":True,
        "monthly_net_output_over_nameplate_hours_is_equipment_availability":False,
        "monthly_data_can_estimate_hourly_temperature_derating":False,
        "seasonal_weather_comparison_is_causal_heat_effect":False,
        "monthly_reporting_completeness_certified":bool(
            summaries.month_is_complete_for_annual_plant_cohort.all()),
        "historical_reliability_calibrated":False}
    return rows,summaries,manifest


def main():
    p=argparse.ArgumentParser()
    for key in ("sites","page4","weather","output"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    rows,summary,m=analyze(
        pd.read_csv(a.sites,dtype={"plant_id":"string"}),
        pd.read_csv(a.page4,dtype={"plant_id":"string","generator_id":"string"}),
        pd.read_csv(a.weather,dtype={"plant_id":"string"}))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    rows.to_csv(out/"page4_era5_matched_plant_month_rows.csv",index=False)
    summary.to_csv(out/"page4_era5_reporting_coverage.csv",index=False)
    (out/"page4_era5_scope_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print(summary.to_string(index=False))


if __name__=="__main__":
    main()
