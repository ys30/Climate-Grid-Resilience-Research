"""Describe limitations of BA-isolated nameplate-based dispatch without historical claims."""
import argparse,json
from pathlib import Path
import pandas as pd

def assess(demand_csv,capacity_csv,shortfall_csv,out):
    d=pd.read_csv(demand_csv);c=pd.read_csv(capacity_csv);s=pd.read_csv(shortfall_csv)
    if not {"ba","timestamp","demand_mw"}.issubset(d) or not {"ba","technology","capacity_mw"}.issubset(c) or not {"ba","unserved_energy_mwh"}.issubset(s):
        raise ValueError("Missing expected model schema")
    if d.duplicated(["ba","timestamp"]).any() or c.duplicated(["ba","technology"]).any() or s.ba.duplicated().any():
        raise ValueError("Duplicate input keys")
    metrics=d.groupby("ba").agg(peak_demand_mw=("demand_mw","max"),
                                observed_demand_mwh=("demand_mw","sum"),
                                modeled_hours=("timestamp","nunique")).reset_index()
    installed=c.groupby("ba",as_index=False).capacity_mw.sum().rename(columns={"capacity_mw":"included_nameplate_mw"})
    result=metrics.merge(installed,on="ba",validate="one_to_one").merge(s,on="ba",validate="one_to_one")
    if result.isna().any().any() or (result[["peak_demand_mw","included_nameplate_mw","unserved_energy_mwh"]]<0).any().any():
        raise ValueError("Invalid metrics")
    result["included_capacity_to_peak_ratio"]=result.included_nameplate_mw/result.peak_demand_mw
    result["included_nameplate_below_peak"]=result.included_nameplate_mw<result.peak_demand_mw
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    result.to_csv(output/"hybrid_model_capacity_diagnostics.csv",index=False)
    meta={"model_scope":"isolated BAs, selected single-fuel generators, nameplate capacity, assumed 100% availability",
          "missing_components":["hydropower_pumped_storage_category","other_generation_fuel_sources","cross_ba_transfers","storage_dispatch","empirically_verified_hourly_availability"],
          "shortfall_is_not_historical_outage":True,"historical_calibration_certified":False}
    (output/"hybrid_model_capacity_diagnostics_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    return meta
def main():
    p=argparse.ArgumentParser()
    for k in ("demand","capacity","shortfall","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args();print(json.dumps(assess(a.demand,a.capacity,a.shortfall,a.output),indent=2))
if __name__=="__main__":main()
