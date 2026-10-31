"""Joint power and monthly energy limits for BPAT hydro: hypothetical scenarios."""
import argparse,json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve

def run(demand,capacity,availability,full_capacity,observed_context,output):
    cap=pd.read_csv(capacity);av=pd.read_csv(availability);fleet=pd.read_csv(full_capacity)
    context=json.loads(Path(observed_context).read_text())
    h=fleet[(fleet.ba=="BPAT")&(fleet.technology=="hydro")]
    if len(h)!=1 or ((cap.ba=="BPAT")&(cap.technology=="hydro")).any():
        raise ValueError("Missing or duplicated BPAT hydro")
    mw=float(h.iloc[0].nameplate_capacity_mw)
    reference=float(context["reported_mixed_hydro_pumped_net_mwh"])
    if mw<=0 or reference<=0:raise ValueError("Bad hydro input")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    times=av.timestamp.drop_duplicates()
    results=[]
    for power_fraction in (0.05,0.10):
        for budget_fraction in (0.01,0.05):
            label=f"power_{int(power_fraction*100)}_budget_{int(budget_fraction*100)}"
            path=out/label;path.mkdir(exist_ok=True)
            budget=reference*budget_fraction
            cc=cap.copy();cc["energy_budget_mwh"]=float("nan")
            cc=pd.concat([cc,pd.DataFrame([{"ba":"BPAT","technology":"hydro","capacity_mw":mw,
                                            "marginal_cost":0,"energy_budget_mwh":budget}])],ignore_index=True)
            aa=pd.concat([av,pd.DataFrame({"timestamp":times,"ba":"BPAT","technology":"hydro",
                                           "availability_pu":power_fraction})],ignore_index=True)
            cc.to_csv(path/"capacity.csv",index=False);aa.to_csv(path/"availability.csv",index=False)
            result=solve(demand,path/"capacity.csv",path/"availability.csv",path/"dispatch")
            gen=pd.read_csv(path/"dispatch"/"generation_hourly.csv")
            hydro_gen=float(gen.loc[(gen.ba=="BPAT")&(gen.technology=="hydro"),"generation_mwh"].sum())
            if hydro_gen>budget+0.1:raise AssertionError("Monthly energy budget exceeded")
            results.append({"assumed_power_fraction":power_fraction,"assumed_energy_fraction":budget_fraction,
                            "hydro_hourly_cap_mw":mw*power_fraction,"hydro_monthly_budget_mwh":budget,
                            "hydro_dispatched_mwh":hydro_gen,
                            "bpat_model_shortfall_mwh":float(result.loc[result.ba=="BPAT","unserved_energy_mwh"].iloc[0])})
    df=pd.DataFrame(results);df.to_csv(out/"bpat_hydro_joint_constraints.csv",index=False)
    (out/"bpat_hydro_joint_constraints_manifest.json").write_text(json.dumps({
        "observed_monthly_energy_is_scale_reference_only":True,
        "tested_hours":len(times),"historical_calibration_certified":False,
        "model_has_both_hourly_power_and_monthly_energy_constraints":True,
        "limitations":"Hydro/pumped observed mix is not physically attributable to nonstorage hydro; constant power and monthly budget are hypothetical."},indent=2)+"\n")
    return df
def main():
    p=argparse.ArgumentParser()
    for x in ("demand","capacity","availability","full-capacity","observed-context","output"):p.add_argument("--"+x,required=True)
    a=p.parse_args();print(run(a.demand,a.capacity,a.availability,a.full_capacity,a.observed_context,a.output).to_string(index=False))
if __name__=="__main__":main()
