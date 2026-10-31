"""Sensitivity to hourly hydro power under an ample hypothetical monthly budget.

Reported wind is an observational dispatch ceiling, NOT weather availability.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve

def run(wind_replay_dir,demand,observed_context,output):
    base=Path(wind_replay_dir)/"reported_wind_ceiling"
    c=pd.read_csv(base/"capacity.csv");a=pd.read_csv(base/"availability.csv")
    hydro=(c.ba=="BPAT")&(c.technology=="hydro")
    profile=(a.ba=="BPAT")&(a.technology=="hydro")
    if hydro.sum()!=1 or profile.sum()!=696:raise ValueError("Unexpected hydro inputs")
    ref=float(json.loads(Path(observed_context).read_text())["reported_mixed_hydro_pumped_net_mwh"])
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for factor in (0.05,0.1,0.15,0.2,0.3,0.5):
        path=out/f"hydro_power_{int(factor*100)}";path.mkdir(exist_ok=True)
        cc=c.copy();aa=a.copy()
        cc.loc[hydro,"energy_budget_mwh"]=ref
        aa.loc[profile,"availability_pu"]=factor
        cc.to_csv(path/"capacity.csv",index=False);aa.to_csv(path/"availability.csv",index=False)
        shortage=solve(demand,path/"capacity.csv",path/"availability.csv",path/"dispatch")
        generation=pd.read_csv(path/"dispatch"/"generation_hourly.csv")
        hydro_generation=float(generation.loc[(generation.ba=="BPAT")&(generation.technology=="hydro"),"generation_mwh"].sum())
        rows.append({"assumed_hydro_hourly_availability":factor,
                     "monthly_energy_budget_mwh":ref,
                     "hydro_dispatched_mwh":hydro_generation,
                     "bpat_shortfall_mwh":float(shortage.loc[shortage.ba=="BPAT","unserved_energy_mwh"].iloc[0])})
    df=pd.DataFrame(rows)
    if (df.bpat_shortfall_mwh.diff().dropna()>0.1).any():raise AssertionError("Nonmonotone power stress")
    df.to_csv(out/"hydro_power_ceiling_sensitivity.csv",index=False)
    (out/"hydro_power_ceiling_manifest.json").write_text(json.dumps({
      "wind":"EIA-930 reported hourly wind used as dispatch ceiling, not weather potential",
      "hydro_energy_budget":"100% of reported EIA-930 combined hydro+pumped net generation, hypothetical proxy only",
      "hydro_power":"5% to 50% of EIA-860 BPAT nonstorage hydro nameplate",
      "historical_calibration_certified":False},indent=2)+"\n")
    return df
def main():
    p=argparse.ArgumentParser()
    for k in ("wind-replay-dir","demand","observed-context","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args();print(run(a.wind_replay_dir,a.demand,a.observed_context,a.output).to_string(index=False))
if __name__=="__main__":main()
