"""Hypothetical monthly hydro budget scenarios with actual EIA-860 nameplate.

EIA-930 mixed hydro/pumped net output serves as a scale reference only:
it is not a measured budget for the non-pumped EIA-860 fleet.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve

def run(demand,capacity,availability,full_capacity,observed_context,output):
    cap=pd.read_csv(capacity);avail=pd.read_csv(availability)
    fleet=pd.read_csv(full_capacity)
    obs=json.loads(Path(observed_context).read_text())
    hydro=fleet[(fleet.ba=="BPAT")&(fleet.technology=="hydro")]
    if len(hydro)!=1:raise ValueError("Missing unique BPAT hydro record")
    mw=float(hydro.iloc[0].nameplate_capacity_mw)
    proxy=float(obs["reported_mixed_hydro_pumped_net_mwh"])
    if not 0<mw<float("inf") or not 0<proxy<float("inf"):raise ValueError("Bad reference inputs")
    if ((cap.ba=="BPAT")&(cap.technology=="hydro")).any():raise ValueError("Hydro duplicate")
    times=avail.timestamp.drop_duplicates()
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    results=[]
    for budget_fraction in (0.05,0.1,0.25,0.5,1.0):
        case=out/("budget_"+str(int(budget_fraction*100))+"pct")
        case.mkdir(exist_ok=True)
        c=cap.copy();a=avail.copy()
        budget=proxy*budget_fraction
        c["energy_budget_mwh"]=float("nan")
        c=pd.concat([c,pd.DataFrame([{"ba":"BPAT","technology":"hydro",
            "capacity_mw":mw,"marginal_cost":0,"energy_budget_mwh":budget}])],ignore_index=True)
        a=pd.concat([a,pd.DataFrame({"timestamp":times,"ba":"BPAT",
            "technology":"hydro","availability_pu":1.0})],ignore_index=True)
        c.to_csv(case/"capacity.csv",index=False);a.to_csv(case/"availability.csv",index=False)
        short=solve(demand,case/"capacity.csv",case/"availability.csv",case/"dispatch")
        gen=pd.read_csv(case/"dispatch"/"generation_hourly.csv")
        hydro_gen=float(gen.loc[(gen.ba=="BPAT")&(gen.technology=="hydro"),"generation_mwh"].sum())
        if hydro_gen > budget+0.1:raise ValueError("Hydro budget violated")
        results.append({"assumed_budget_fraction_of_mixed_observed_energy":budget_fraction,
            "assumed_budget_mwh":budget,"optimized_hydro_generation_mwh":hydro_gen,
            "bpat_shortfall_mwh":float(short.loc[short.ba=="BPAT","unserved_energy_mwh"].iloc[0])})
    pd.DataFrame(results).to_csv(out/"hypothetical_monthly_hydro_budget_sweep.csv",index=False)
    m={"hydro_capacity_source":"EIA-860 2024 BPAT nonstorage nameplate",
       "budget_reference":"EIA-930 mixed hydro and pumped storage 2024-02 observed net generation",
       "budget_is_measured_nonstorage_hydro_water_availability":False,
       "hydro_hourly_availability_assumed":1.0,
       "monthly_hydro_e_sum_max_enforced":True,"historical_calibration_certified":False,
       "warning":"Sensitivity limits a hypothetical separate hydro generator, not historical observed hydro or pumped storage operation."}
    (out/"hypothetical_monthly_hydro_budget_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    return pd.DataFrame(results)
def main():
    p=argparse.ArgumentParser()
    for x in ("demand","capacity","availability","full-capacity","observed-context","output"):p.add_argument("--"+x,required=True)
    a=p.parse_args();print(run(a.demand,a.capacity,a.availability,a.full_capacity,a.observed_context,a.output).to_string(index=False))
if __name__=="__main__":main()
