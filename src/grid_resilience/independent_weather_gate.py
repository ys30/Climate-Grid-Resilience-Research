"""Gate externally sourced hourly wind weather before resilience experiments.

This module validates WEATHER INPUTS, not wind production observations.
An ERA5 or other independent meteorological provider must supply the file.
No weather-to-generation model is claimed by this validation.
"""
import argparse,json
from pathlib import Path
import pandas as pd

EXPECTED_BAS={"AZPS","BPAT","CISO","SRP"}
FORBIDDEN=("eia930","generation","eia923","dispatch","reported_wind")
def validate(source,output,start="2024-02-01T00:00:00Z",hours=696):
    src=Path(source)
    if any(token in src.name.lower() for token in FORBIDDEN):
        raise ValueError("Weather input path resembles electrical generation output")
    frame=pd.read_csv(src)
    required={"timestamp","ba","wind_speed_ms","weather_source","source_variable"}
    if not required.issubset(frame):raise ValueError("Missing weather provenance or wind speed columns")
    if frame.empty or frame[list(required)].isna().any().any():
        raise ValueError("Null weather input")
    if set(frame.ba)!=EXPECTED_BAS:raise ValueError("Incomplete or extra BA names")
    if frame.duplicated(["timestamp","ba"]).any():raise ValueError("Duplicate BA-hour")
    if frame.weather_source.astype(str).str.strip().eq("").any() or frame.source_variable.astype(str).str.strip().eq("").any():
        raise ValueError("Empty weather provenance")
    if frame.weather_source.astype(str).str.lower().str.contains("eia[-_]?930|electric|dispatch|generation",regex=True).any():
        raise ValueError("Electricity data cannot be relabeled meteorological data")
    ts=pd.to_datetime(frame.timestamp,utc=True,errors="raise")
    expected=pd.date_range(pd.Timestamp(start),periods=hours,freq="h")
    for ba in EXPECTED_BAS:
        actual=pd.DatetimeIndex(ts[frame.ba.eq(ba)]).sort_values()
        if len(actual)!=hours or not actual.equals(expected):
            raise ValueError(f"Missing/misaligned hourly weather records for {ba}")
    speed=pd.to_numeric(frame.wind_speed_ms,errors="raise")
    if not speed.map(lambda x:0<=float(x)<100).all():
        raise ValueError("Invalid wind speed or nonfinite values")
    clean=frame.copy()
    clean["timestamp"]=ts.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    clean["wind_speed_ms"]=speed
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    clean.sort_values(["timestamp","ba"]).to_csv(out/"independent_weather_validated.csv",index=False)
    manifest={"weather_rows":len(frame),"hours_per_ba":hours,"bas":sorted(EXPECTED_BAS),
      "unique_weather_sources":sorted(frame.weather_source.astype(str).unique().tolist()),
      "meteorological_independence_self_reported_not_verified":True,
      "weather_to_wind_capacity_factor_calibrated":False,
      "historical_reliability_calibrated":False,
      "notes":"Do not use EIA-930 net wind generation as weather; check weather provider metadata externally."}
    (out/"independent_weather_gate_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    p.add_argument("--start",default="2024-02-01T00:00:00Z");p.add_argument("--hours",type=int,default=696)
    a=p.parse_args();print(json.dumps(validate(a.input,a.output,a.start,a.hours),indent=2))
if __name__=="__main__":main()
