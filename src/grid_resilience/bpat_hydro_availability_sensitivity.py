"""Sensitivity of BPAT reported hydro nameplate to assumed hourly availability.

All output is counterfactual; constant availability is NOT a measured
hydrological production profile, and no pumped storage is represented.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve

def run(demand,capacity,availability,full_capacity,output):
    base=pd.read_csv(capacity);av=pd.read_csv(availability);fleet=pd.read_csv(full_capacity)
    hydro=fleet.loc[(fleet.ba=="BPAT")&(fleet.technology=="hydro")]
    if len(hydro)!=1:raise ValueError("BPAT hydro inventory missing or duplicated")
    mw=float(hydro.iloc[0].nameplate_capacity_mw)
    if not 0<mw<float("inf"):raise ValueError("Invalid official nameplate")
    if ((base.ba=="BPAT")&(base.technology=="hydro")).any():raise ValueError("Hydro already present")
    times=av.timestamp.drop_duplicates()
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    results=[]
    for factor in (0,0.05,0.10,0.15,0.20,0.25,0.5,0.75,1.0):
        folder=out/f"hydro_availability_{int(factor*100)}";folder.mkdir(exist_ok=True)
        cap=base.copy();hourly=av.copy()
        if factor>0:
            cap=pd.concat([cap,pd.DataFrame([{"ba":"BPAT","technology":"hydro","capacity_mw":mw,"marginal_cost":0}])],ignore_index=True)
            hourly=pd.concat([hourly,pd.DataFrame({"timestamp":times,"ba":"BPAT",
                        "technology":"hydro","availability_pu":factor})],ignore_index=True)
        cap.to_csv(folder/"capacity.csv",index=False)
        hourly.to_csv(folder/"availability.csv",index=False)
        short=solve(demand,folder/"capacity.csv",folder/"availability.csv",folder/"dispatch")
        bpat=float(short.loc[short.ba=="BPAT","unserved_energy_mwh"].iloc[0])
        results.append({"assumed_hydro_availability_pu":factor,
                        "reported_bpat_hydro_nameplate_mw":mw,
                        "assumed_max_hydro_dispatch_mw":mw*factor,
                        "bpat_modeled_shortfall_mwh":bpat})
    pd.DataFrame(results).to_csv(out/"hydro_availability_sensitivity.csv",index=False)
    m={"capacity_source":"2024 EIA-860 reported BPAT non-storage single-fuel hydro nameplate",
       "availability_source":"hypothetical constant factors; NOT historical profiles",
       "tested_factors":[0,0.05,0.10,0.15,0.20,0.25,0.5,0.75,1.0],
       "storage_and_transmission_not_modeled":True,
       "hydrological_energy_budget_not_enforced":True,
       "historical_calibration_certified":False}
    (out/"hydro_availability_sensitivity_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    return pd.DataFrame(results)
def main():
    p=argparse.ArgumentParser()
    for x in ("demand","capacity","availability","full-capacity","output"):p.add_argument("--"+x,required=True)
    a=p.parse_args();print(run(a.demand,a.capacity,a.availability,a.full_capacity,a.output).to_string(index=False))
if __name__=="__main__":main()
