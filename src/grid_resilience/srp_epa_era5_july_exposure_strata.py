"""Descriptive EPA source-unit operating indicators by co-located ERA5 heat bins.

Not generator net output, not causal thermal derating. Only source-matched
UTC hours admitted. Conditioning on positive operation is dispatch-selective.
Do not treat multiple EPA units sharing a weather plant as independent
replications of an atmospheric event.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
import numpy as np

BINS=(-np.inf,35.0,40.0,np.inf)
LABELS=("below_35_c","35_to_below_40_c","at_least_40_c")


def summarize(hourly):
    required={"facility_id","unit_id","timestamp_utc",
              "era5_july_hour_matched","temperature_2m_c",
              "operating_time","gross_load_mw"}
    if not required.issubset(hourly):
        raise ValueError("Missing verified hourly source fields")
    x=hourly.copy()
    x["facility_id"]=x.facility_id.astype("string").str.strip()
    x["unit_id"]=x.unit_id.astype("string").str.strip()
    x["timestamp_utc"]=pd.to_datetime(x.timestamp_utc,utc=True,errors="raise")
    for k in ("temperature_2m_c","operating_time","gross_load_mw"):
        x[k]=pd.to_numeric(x[k],errors="coerce")
    match=x.era5_july_hour_matched
    if match.dtype!=bool or match.isna().any():
        raise ValueError("Invalid source weather match indicator")
    if x.duplicated(["facility_id","unit_id","timestamp_utc"]).any():
        raise ValueError("Duplicate source unit UTC hours")
    if x.loc[match,"temperature_2m_c"].isna().any() or x.loc[
        ~match,"temperature_2m_c"].notna().any():
        raise ValueError("Source weather presence contradicts match flag")
    if not x.operating_time.dropna().between(0,1).all():
        raise ValueError("Operating time outside [0,1]")
    if not np.isfinite(x.gross_load_mw.dropna().to_numpy(float)).all():
        raise ValueError("Nonfinite source gross load")
    total=x.groupby(["facility_id","unit_id"],as_index=False).agg(
        calendar_rows=("timestamp_utc","size"),
        matched_weather_rows=("era5_july_hour_matched","sum"))
    if not total.calendar_rows.eq(744).all() or not total.matched_weather_rows.eq(737).all():
        raise ValueError("Expected 744 source hours, 737 UTC weather source matches per unit")
    x=x.loc[match].copy()
    x["temperature_bin"]=pd.cut(x.temperature_2m_c,bins=BINS,
                                 labels=LABELS,right=False)
    if x.temperature_bin.isna().any():
        raise ValueError("Unclassified matched temperature")
    x["reported_positive_operating_time"]=x.operating_time.gt(0)
    x["reported_positive_gross_load"]=x.gross_load_mw.gt(0)
    rows=[]
    for (plant,unit,tempbin),g in x.groupby(
        ["facility_id","unit_id","temperature_bin"],observed=True):
        running=g.loc[g.reported_positive_operating_time]
        gross=running.loc[running.gross_load_mw.notna()]
        rows.append({
            "facility_id":str(plant),"epa_unit_id":str(unit),
            "temperature_bin":str(tempbin),
            "source_weather_hour_count":len(g),
            "reported_positive_operating_hours":int(g.reported_positive_operating_time.sum()),
            "source_reported_operating_fraction_hours":float(g.operating_time.sum()),
            "positive_operating_hour_share":float(g.reported_positive_operating_time.mean()),
            "operating_rows_with_gross_load":len(gross),
            "operating_rows_with_positive_gross_load":int(
                running.reported_positive_gross_load.sum()),
            "mean_reported_gross_load_mw_given_positive_operation":(
                float(gross.gross_load_mw.mean()) if len(gross) else float("nan")),
            "source_weather_hour_count_is_independent_weather_sample":False,
            "source_gross_load_is_net_electrical_generator_mw":False
        })
    result=pd.DataFrame(rows).sort_values(
        ["facility_id","epa_unit_id","temperature_bin"])
    check=result.groupby(["facility_id","epa_unit_id"],as_index=False).agg(
        classified_source_hours=("source_weather_hour_count","sum"))
    if not check.classified_source_hours.eq(737).all() or len(check)!=len(total):
        raise AssertionError("Temperature bin source hours do not sum to matched UTC hours")
    # Count plant weather once, not once for each EPA unit at the same plant.
    weather=x[["facility_id","timestamp_utc","temperature_2m_c","temperature_bin"]].drop_duplicates()
    if weather.duplicated(["facility_id","timestamp_utc"]).any():
        raise ValueError("Co-located EPA units disagree on common plant ERA5 temperature")
    plant=weather.groupby(["facility_id","temperature_bin"],observed=True).agg(
        unique_site_weather_hours=("timestamp_utc","size")).reset_index()
    if not plant.groupby("facility_id").unique_site_weather_hours.sum().eq(737).all():
        raise AssertionError("Duplicate or incomplete plant-weather source hours")
    manifest={
        "EPA_source_time":"Part75 local standard time, fixed Arizona MST UTC-07",
        "weather_source_time":"ERA5 July 2024 UTC",
        "temperature_bin_edges_c":[35,40],
        "observed_source_utc_hour_intersection_per_unit":737,
        "reused_weather_across_colocated_epa_units":True,
        "gross_load_conditioned_on_positive_operation_only":True,
        "dispatch_commitment_selection_adjusted":False,
        "unit_hour_observation_is_independent_climate_sample":False,
        "epa_unit_is_verified_eia_generator":False,
        "measured_eia_generator_net_output":False,
        "causal_thermal_derating_or_outage_identified":False
    }
    return result,plant,manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    x,weather,m=summarize(pd.read_csv(a.hourly))
    root=Path(a.output);root.mkdir(parents=True,exist_ok=True)
    x.to_csv(root/"epa_unit_source_heat_strata_descriptive.csv",index=False)
    weather.to_csv(root/"unique_plant_era5_heat_strata_hours.csv",index=False)
    (root/"epa_2024_july_source_heat_strata_manifest.json").write_text(
        json.dumps(m,indent=2)+"\n")
    print(x.to_string(index=False))
    print(weather.to_string(index=False))


if __name__=="__main__":
    main()
