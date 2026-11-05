"""Cross-season EPA source-unit observational validation (Jan/Jul 2024).

Only EPA-source operating indicators and gross electrical reporting compared;
neither month identifies equipment availability, generator net MW or derating.
January EPA Local Standard Time UTC-7 and genuine UTC-January ERA5 intersect
for 737 hours; July also uses only its 737 UTC-July overlapping source hours.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from grid_resilience.srp_epa_2024_az_hourly_admission import EXPECTED_MD5
from grid_resilience.srp_epa_era5_july_local_standard_alignment import PLANTS

EXPECTED_UNITS = {"141":{"1","2","3","7","8"},
                  "55129":{"DBG1","DBG2","DBG4","DBG5"},
                  "147":{"K-7"}}


def extract_epa_january(original):
    cols=["Facility ID","Unit ID","Date","Hour","Operating Time",
          "Gross Load (MW)","Heat Input (mmBtu)"]
    if not set(cols).issubset(pd.read_csv(original,nrows=0).columns):
        raise ValueError("Original EPA schema changed")
    parts=[]
    for chunk in pd.read_csv(original,usecols=cols,dtype="string",chunksize=150000):
        fac=chunk["Facility ID"].str.strip().str.replace(r"^0+(?=[0-9])","",regex=True)
        take=chunk.loc[fac.isin(PLANTS)&chunk.Date.str.contains("2024",na=False)].copy()
        if take.empty:continue
        dates=pd.to_datetime(take.Date,errors="raise")
        take=take.loc[dates.dt.strftime("%Y-%m").eq("2024-01")].copy()
        if not take.empty:
            take["Facility ID"]=fac.loc[take.index]
            parts.append(take)
    if not parts:raise ValueError("No original January EPA source")
    x=pd.concat(parts,ignore_index=True).rename(columns={
        "Facility ID":"facility_id","Unit ID":"unit_id","Date":"date_local_standard",
        "Hour":"hour_local_standard","Operating Time":"operating_time",
        "Gross Load (MW)":"gross_load_mw","Heat Input (mmBtu)":"heat_input_mmbtu"})
    return x


def january_join(epa, weather):
    needed={"facility_id","unit_id","date_local_standard","hour_local_standard",
            "operating_time","gross_load_mw","heat_input_mmbtu"}
    if not needed.issubset(epa) or not {"plant_id","technology","timestamp_utc",
            "temperature_2m_c"}.issubset(weather):
        raise ValueError("Missing original EPA/ERA5 columns")
    e=epa.copy()
    e["facility_id"]=e.facility_id.astype("string").str.strip()
    e["unit_id"]=e.unit_id.astype("string").str.strip()
    if e[["facility_id","unit_id"]].isna().any().any():
        raise ValueError("Missing EPA source IDs")
    observed={str(k):set(v) for k,v in e.groupby("facility_id").unit_id.unique().items()}
    if observed!=EXPECTED_UNITS:
        raise ValueError("January EPA source unit population differs from July")
    dates=pd.to_datetime(e.date_local_standard,errors="raise")
    h=pd.to_numeric(e.hour_local_standard,errors="raise")
    if not dates.dt.strftime("%Y-%m").eq("2024-01").all() or not h.between(0,23).all() or not h.mod(1).eq(0).all():
        raise ValueError("Invalid January EPA local clock")
    e["timestamp_utc"]=(dates+pd.to_timedelta(h,unit="h")+pd.Timedelta(hours=7)).dt.tz_localize("UTC")
    for col in ("operating_time","gross_load_mw","heat_input_mmbtu"):
        e[col]=pd.to_numeric(e[col],errors="coerce")
        if not np.isfinite(e[col].dropna().to_numpy(float)).all():
            raise ValueError("Nonfinite EPA source reading")
    if not e.operating_time.dropna().between(0,1).all():
        raise ValueError("Invalid EPA source operating fraction")
    if e.duplicated(["facility_id","unit_id","timestamp_utc"]).any():
        raise ValueError("Duplicate source unit hour")
    jan_local=pd.date_range("2024-01-01T07:00:00Z",periods=744,freq="h")
    for (plant,unit),g in e.groupby(["facility_id","unit_id"]):
        if not pd.DatetimeIndex(g.timestamp_utc.sort_values()).equals(jan_local):
            raise ValueError("Incomplete original EPA January local calendar")
    w=weather.copy()
    w["plant_id"]=w.plant_id.astype("string").str.strip()
    w=w.loc[w.technology.eq("gas")&w.plant_id.isin(EXPECTED_UNITS)].copy()
    w["timestamp_utc"]=pd.to_datetime(w.timestamp_utc,utc=True)
    w["temperature_2m_c"]=pd.to_numeric(w.temperature_2m_c,errors="coerce")
    if set(w.plant_id)!=set(EXPECTED_UNITS) or w.duplicated(["plant_id","timestamp_utc"]).any():
        raise ValueError("January 3-site ERA5 plant identity missing or duplicated")
    jan_utc=pd.date_range("2024-01-01T00:00:00Z",periods=744,freq="h")
    for site,g in w.groupby("plant_id"):
        if not pd.DatetimeIndex(g.timestamp_utc.sort_values()).equals(jan_utc):
            raise ValueError("Incomplete January weather source UTC calendar")
    if not np.isfinite(w.temperature_2m_c.to_numpy(float)).all():
        raise ValueError("Unreported January weather temperatures")
    j=e.merge(w[["plant_id","timestamp_utc","temperature_2m_c"]],
              left_on=["facility_id","timestamp_utc"],right_on=["plant_id","timestamp_utc"],
              how="left",validate="many_to_one",indicator=True)
    j["observed_utc_month_weather_matched"]=j._merge.eq("both")
    j=j.drop(columns=["plant_id","_merge"])
    counts=j.groupby(["facility_id","unit_id"]).observed_utc_month_weather_matched.sum()
    if len(counts)!=10 or not counts.eq(737).all():
        raise ValueError("January source overlap not 737/744 per unit")
    missing=j.loc[~j.observed_utc_month_weather_matched]
    if not missing.timestamp_utc.dt.strftime("%Y-%m-%d").eq("2024-02-01").all() or not missing.timestamp_utc.dt.hour.lt(7).all():
        raise ValueError("January UTC-February boundary mismatch")
    return j


def compare(january,july):
    j=january.loc[january.observed_utc_month_weather_matched].copy()
    u=july.copy()
    needed={"facility_id","unit_id","timestamp_utc","temperature_2m_c",
            "operating_time","gross_load_mw","era5_full_local_july_matched"}
    if not needed.issubset(u) or not u.era5_full_local_july_matched.eq(True).all():
        raise ValueError("July source panel not certified")
    u["timestamp_utc"]=pd.to_datetime(u.timestamp_utc,utc=True)
    u=u.loc[u.timestamp_utc.lt(pd.Timestamp("2024-08-01T00:00:00Z"))]
    if len(j)!=7370 or len(u)!=7370:
        raise ValueError("Unequal or incomplete UTC-month matched source populations")
    rows=[]
    for label,data in [("January",j),("July",u)]:
        data=data.copy()
        data["facility_id"]=data.facility_id.astype("string").str.strip()
        data["unit_id"]=data.unit_id.astype("string").str.strip()
        for col in ("temperature_2m_c","operating_time","gross_load_mw"):
            data[col]=pd.to_numeric(data[col],errors="coerce")
        for (plant,unit),g in data.groupby(["facility_id","unit_id"]):
            if len(g)!=737 or unit not in EXPECTED_UNITS.get(str(plant),set()):
                raise ValueError("Source EPA cohort mismatch")
            running=g.operating_time.gt(0)
            gross=g.loc[running,"gross_load_mw"].dropna()
            rows.append({"source_month":label,"facility_id":str(plant),"epa_unit_id":str(unit),
                "matched_utc_month_source_hours":len(g),
                "mean_site_temperature_c":float(g.temperature_2m_c.mean()),
                "positive_operation_source_rows":int(running.sum()),
                "positive_operation_share":float(running.mean()),
                "gross_reported_when_running_rows":int(len(gross)),
                "mean_gross_load_mw_given_running":float(gross.mean()) if len(gross) else np.nan})
    frame=pd.DataFrame(rows)
    if len(frame)!=20 or frame.groupby("source_month").size().ne(10).any():
        raise ValueError("January-July comparison source conservation failed")
    pivot=frame.pivot(index=["facility_id","epa_unit_id"],columns="source_month",
        values=["mean_site_temperature_c","positive_operation_share","mean_gross_load_mw_given_running"])
    delta=pd.DataFrame({
        "facility_id":pivot.index.get_level_values(0),
        "epa_unit_id":pivot.index.get_level_values(1),
        "july_minus_january_temperature_c":(pivot[("mean_site_temperature_c","July")]-
                                            pivot[("mean_site_temperature_c","January")]).to_numpy(),
        "july_minus_january_operation_share":(pivot[("positive_operation_share","July")]-
                                             pivot[("positive_operation_share","January")]).to_numpy(),
        "july_minus_january_conditional_gross_load_mw":(
            pivot[("mean_gross_load_mw_given_running","July")]-
            pivot[("mean_gross_load_mw_given_running","January")]).to_numpy()
    })
    meta={"source_periods":["2024-01","2024-07"],
          "epa_local_standard_utc_offset_hours":7,
          "source_units_in_each_period":10,
          "matched_utc_month_hours_per_unit_each_period":737,
          "boundary_unmatched_hours_per_unit_each_period":7,
          "january_missing_weather_requires_real_february_utc_source":True,
          "july_full_local_weather_still_available_upstream":True,
          "same_epa_source_unit_cohort":True,
          "independent_season_weather_exposure_contrast":True,
          "transfer_validation_of_july_temperature_slope":False,
          "separate_january_eia930_demand_control_included":False,
          "physical_eia_generator_mapping_admitted":False,
          "conditional_gross_is_not_generator_available_net_power":True,
          "causal_heat_derating_or_eens_estimated":False}
    return frame,delta,meta


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-epa",required=True)
    p.add_argument("--january-era5",required=True)
    p.add_argument("--july-panel",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--expected-original-md5",default=EXPECTED_MD5)
    a=p.parse_args()
    source=Path(a.original_epa)
    if hashlib.md5(source.read_bytes()).hexdigest()!=a.expected_original_md5:
        raise ValueError("2024 EPA AZ original source MD5 differs from published archive")
    jan=january_join(extract_epa_january(source),
        pd.read_csv(a.january_era5,dtype={"plant_id":"string"}))
    july=pd.read_csv(a.july_panel,dtype={"facility_id":"string","unit_id":"string"})
    result,delta,manifest=compare(jan,july)
    root=Path(a.output);root.mkdir(parents=True,exist_ok=True)
    jan.to_csv(root/"epa_january_2024_744_local_hours_era5_utc_weather_gate.csv",index=False)
    result.to_csv(root/"epa_source_january_july_matched_operating_comparison.csv",index=False)
    delta.to_csv(root/"epa_source_january_july_matched_differences.csv",index=False)
    (root/"epa_source_january_july_comparison_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print(result.to_string(index=False))
    print(delta.to_string(index=False))


if __name__=="__main__":
    main()
