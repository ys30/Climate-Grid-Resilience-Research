"""Paired BPAT weather/replay PyPSA dispatch with shared hypothetical hydro.

Hydro plant nameplate from EIA-860 is not an observed available capacity;
the EIA-930 hydro+pumped energy total is not a certified hydro budget.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve

def run(root,hydro_capacity,hydro_context,output):
    root=Path(root);out=Path(output);out.mkdir(parents=True,exist_ok=True)
    cap=pd.read_csv(root.parent/"model_inputs/capacity.csv")
    demand=root.parent/"model_inputs/hourly_ba_demand.csv"
    h=pd.read_csv(hydro_capacity)
    h=h[(h.ba=="BPAT")&(h.technology=="hydro")]
    if len(h)!=1 or (cap.ba.eq("BPAT")&cap.technology.eq("hydro")).any():raise ValueError("Duplicate/missing hydro")
    hydro_mw=float(h.nameplate_capacity_mw.iloc[0])
    reference=float(json.loads(Path(hydro_context).read_text())["reported_mixed_hydro_pumped_net_mwh"])
    records=[]
    for fraction,power in [(0.05,0.10),(0.25,0.10),(0.50,0.10),(1.0,0.20),(1.0,0.30)]:
        cc=cap.copy();cc["energy_budget_mwh"]=float("nan")
        cc=pd.concat([cc,pd.DataFrame([{"ba":"BPAT","technology":"hydro","capacity_mw":hydro_mw,"marginal_cost":0,
                                       "energy_budget_mwh":reference*fraction}])],ignore_index=True)
        for label,filename in [("era5","era5_29site_wind_availability.csv"),
                               ("replay","observed_wind_replay_availability.csv")]:
            aa=pd.read_csv(root/filename)
            times=aa.loc[(aa.ba=="BPAT")&(aa.technology=="wind"),"timestamp"]
            if len(times)!=696:raise ValueError("Missing wind hours")
            aa=pd.concat([aa,pd.DataFrame({"timestamp":times,"ba":"BPAT","technology":"hydro",
                                           "availability_pu":power})],ignore_index=True)
            case=out/f"hydro_energy_{int(fraction*100)}_power_{int(power*100)}"/label
            case.mkdir(parents=True,exist_ok=True)
            cc.to_csv(case/"capacity.csv",index=False)
            aa.to_csv(case/"availability.csv",index=False)
            result=solve(demand,case/"capacity.csv",case/"availability.csv",case/"dispatch")
            short=float(result.loc[result.ba=="BPAT","unserved_energy_mwh"].iloc[0])
            records.append({"hydro_budget_fraction":fraction,"hydro_power_fraction":power,
                            "scenario":label,"bpat_shortfall_mwh":short})
    frame=pd.DataFrame(records)
    pivot=frame.pivot(index=["hydro_budget_fraction","hydro_power_fraction"],columns="scenario",values="bpat_shortfall_mwh").reset_index()
    pivot["era5_minus_replay_shortfall_mwh"]=pivot.era5-pivot.replay
    pivot.to_csv(out/"bpat_matched_hydro_weather_comparison.csv",index=False)
    (out/"bpat_matched_hydro_weather_manifest.json").write_text(json.dumps({
      "scenario_pairs":len(pivot),"constant_hydro_within_each_pair":True,
      "hydro_capacity":"2024 EIA-860 BPAT single-fuel nonstorage hydro nameplate",
      "hydro_energy_reference":"EIA-930 hydro+pumped mixed reported output; used as hypothetical scaling only",
      "observed_historical_shortfall":False,"hydro_water_availability_calibrated":False,
      "interties_modeled":False},indent=2)+"\n")
    return pivot
def main():
    p=argparse.ArgumentParser()
    for k in ("root","hydro-capacity","hydro-context","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args();print(run(a.root,a.hydro_capacity,a.hydro_context,a.output).to_string(index=False))
if __name__=="__main__":main()
