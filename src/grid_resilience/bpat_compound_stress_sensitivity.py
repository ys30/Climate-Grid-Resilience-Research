"""Paired hypothetical demand/renewables stress on a fixed BPAT hydro configuration.

All shocks are transparent scenario assumptions, not reconstructed weather.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve
def run(demand,capacity,availability,full_capacity,observed_context,output):
    base=pd.read_csv(capacity);av=pd.read_csv(availability);fleet=pd.read_csv(full_capacity)
    context=json.loads(Path(observed_context).read_text())
    row=fleet[(fleet.ba=="BPAT")&(fleet.technology=="hydro")]
    if len(row)!=1:raise ValueError("Missing BPAT hydro category")
    hydro_mw=float(row.iloc[0].nameplate_capacity_mw)
    budget=0.05*float(context["reported_mixed_hydro_pumped_net_mwh"])
    cap=base.copy();cap["energy_budget_mwh"]=float("nan")
    cap=pd.concat([cap,pd.DataFrame([{"ba":"BPAT","technology":"hydro",
        "capacity_mw":hydro_mw,"marginal_cost":0,"energy_budget_mwh":budget}])],ignore_index=True)
    avail=pd.concat([av,pd.DataFrame({"timestamp":av.timestamp.drop_duplicates(),
        "ba":"BPAT","technology":"hydro","availability_pu":0.10})],ignore_index=True)
    demand_df=pd.read_csv(demand)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    records=[]
    for name,demand_factor,wind_factor in [("baseline",1.,1.),("demand_plus_5pct",1.05,1.),
                                            ("wind_half",1.,0.5),("compound",1.05,0.5)]:
        case=out/name;case.mkdir(exist_ok=True)
        dd=demand_df.copy();aa=avail.copy()
        dd.loc[dd.ba=="BPAT","demand_mw"]*=demand_factor
        aa.loc[(aa.ba=="BPAT")&(aa.technology=="wind"),"availability_pu"]*=wind_factor
        dd.to_csv(case/"demand.csv",index=False);aa.to_csv(case/"availability.csv",index=False)
        cap.to_csv(case/"capacity.csv",index=False)
        s=solve(case/"demand.csv",case/"capacity.csv",case/"availability.csv",case/"dispatch")
        records.append({"scenario":name,"bpat_demand_multiplier":demand_factor,
          "bpat_wind_availability_multiplier":wind_factor,
          "bpat_model_shortfall_mwh":float(s.loc[s.ba=="BPAT","unserved_energy_mwh"].iloc[0])})
    df=pd.DataFrame(records);ref=float(df.loc[df.scenario=="baseline","bpat_model_shortfall_mwh"].iloc[0])
    df["additional_shortfall_vs_baseline_mwh"]=df.bpat_model_shortfall_mwh-ref
    df.to_csv(out/"bpat_hypothetical_compound_stress.csv",index=False)
    (out/"bpat_hypothetical_compound_stress_manifest.json").write_text(json.dumps({
       "demand_data":"EIA-930 February 2024 demand",
       "generator_capacity":"EIA-860 2024 BA-attributed single fuel candidate nameplate",
       "hydro_availability_assumed":0.10,"hydro_energy_budget_assumed_mwh":budget,
       "wind_base_availability_assumed":1.0,"weather_shocks_empirically_estimated":False,
       "historical_calibration_certified":False,
       "warning":"Demand +5% and wind halved are artificial diagnostic shocks, not observed compound heat/low-wind event."},indent=2)+"\n")
    return df
def main():
    p=argparse.ArgumentParser()
    for x in ("demand","capacity","availability","full-capacity","observed-context","output"):p.add_argument("--"+x,required=True)
    a=p.parse_args();print(run(a.demand,a.capacity,a.availability,a.full_capacity,a.observed_context,a.output).to_string(index=False))
if __name__=="__main__":main()
