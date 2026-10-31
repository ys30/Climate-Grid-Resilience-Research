"""Plan auditable BPAT wind-plant ERA5 spatial sampling (no invented weather).

Writes deterministic capacity-ranked coordinate batches for later weather
downloads. Plant coordinates are proxies for turbine locations.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def plan(locations,output,ba="BPAT",max_points=30):
    df=pd.read_csv(locations,dtype={"plant_id":str})
    required={"ba","plant_id","latitude","longitude","nameplate_mw"}
    if not required.issubset(df):raise ValueError("Missing EIA wind plant fields")
    part=df[df.ba==ba].copy()
    if part.empty or part.plant_id.duplicated().any():raise ValueError("No unique plant locations")
    if part[list(required-{"ba","plant_id"})].isna().any().any() or not part.nameplate_mw.gt(0).all():
        raise ValueError("Invalid plant coordinates or capacities")
    part=part.sort_values(["nameplate_mw","plant_id"],ascending=[False,True])
    selected=part.head(max_points).copy()
    if selected.empty:raise ValueError("No selected plants")
    coverage=float(selected.nameplate_mw.sum()/part.nameplate_mw.sum())
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    selected["capacity_weight_within_sample"]=selected.nameplate_mw/selected.nameplate_mw.sum()
    selected.to_csv(out/"bpat_era5_sampling_plan.csv",index=False)
    manifest={"ba":ba,"total_eligible_wind_plants":len(part),
      "selected_plant_points":len(selected),"selected_wind_capacity_mw":float(selected.nameplate_mw.sum()),
      "eligible_wind_capacity_mw":float(part.nameplate_mw.sum()),
      "sampled_share_of_eligible_nameplate":coverage,
      "selection":"top installed nameplate by EIA-860 plant coordinates",
      "weather_download_completed":False,"capacity_weighted_weather_completed":False,
      "plant_coordinate_not_turbine_location":True,
      "uncertainty":"Selection excludes lower-capacity wind plants; point weather is not BA-level validation."}
    (out/"bpat_era5_sampling_plan_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--locations",required=True);p.add_argument("--output",required=True)
    p.add_argument("--max-points",type=int,default=30)
    a=p.parse_args();print(json.dumps(plan(a.locations,a.output,max_points=a.max_points),indent=2))
if __name__=="__main__":main()
