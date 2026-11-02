"""Capacity derating screen using genuine hourly load and explicitly hypothetical supply availability.

Not historical capacity calibration. Every scenario reruns full-month PyPSA.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from grid_resilience.monthly_pypsa_screen import run

def scenarios(demand, capacities, year, month, factors=(1.0,0.75,0.5,0.35)):
    if not factors or any(not 0 < float(f)<=1 for f in factors):raise ValueError("Invalid derating factor")
    if len(set(factors))!=len(factors):raise ValueError("Duplicate derating factors")
    rows=[];dispatch=[]
    for factor in factors:
        supply=capacities.copy()
        supply["capacity_mw"]=pd.to_numeric(supply.capacity_mw,errors="raise")*float(factor)
        generation,shortage=run(demand,supply,year,month)
        for ba,unserved in shortage.items():
            load=float(pd.to_numeric(demand.loc[demand.ba==ba,"demand_mw"]).sum())
            modeled=float(generation.loc[generation.ba==ba,"modeled_generation_mwh"].sum())
            if abs(modeled+unserved-load)>max(1e-4,load*1e-9):
                raise ValueError("Energy balance failure")
            rows.append({"availability_factor_assumed":factor,"ba":ba,
                "demand_mwh":load,"modeled_supply_mwh":modeled,
                "modeled_unserved_mwh":unserved,
                "unserved_share":unserved/load if load>0 else 0.0,
                "hypothetical_assumption":True,"historical_calibration_certified":False})
        generation.insert(0,"availability_factor_assumed",factor)
        dispatch.append(generation)
    return pd.DataFrame(rows),pd.concat(dispatch,ignore_index=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand",required=True);p.add_argument("--capacity",required=True)
    p.add_argument("--year",type=int,required=True);p.add_argument("--month",type=int,required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    summary,detail=scenarios(pd.read_csv(a.demand),pd.read_csv(a.capacity),a.year,a.month)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    summary.to_csv(out/"availability_sensitivity_summary.csv",index=False)
    detail.to_csv(out/"availability_sensitivity_generation.csv",index=False)
    (out/"availability_sensitivity_manifest.json").write_text(json.dumps({
      "capacity_scale_factors":[1.0,0.75,0.5,0.35],
      "scenario_scope":"All candidate generator nameplate uniformly reduced, no source-derived hourly availability.",
      "historical_calibration_certified":False,"BA_fleet_complete":False},indent=2)+"\n")
    print(summary.to_string(index=False))
if __name__=="__main__":main()
