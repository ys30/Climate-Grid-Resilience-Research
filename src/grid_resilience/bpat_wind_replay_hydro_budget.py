"""Audit wind-replay shortage sensitivity to hypothetical hydro monthly budgets.

Reuses the observed-wind-ceiling scenario inputs exactly; only the hydro
energy budget changes. This is NOT an independent historical calibration.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve

def sweep(wind_replay_dir,demand,observed_context,output):
    root=Path(wind_replay_dir)/"reported_wind_ceiling"
    c=pd.read_csv(root/"capacity.csv")
    a=root/"availability.csv";d=Path(demand)
    if not d.exists():raise ValueError(f"Expected historical demand file at {d}")
    hydro=(c.ba=="BPAT")&(c.technology=="hydro")
    if hydro.sum()!=1 or "energy_budget_mwh" not in c:raise ValueError("No unique hydro budget row")
    ref=float(json.loads(Path(observed_context).read_text())["reported_mixed_hydro_pumped_net_mwh"])
    if ref<=0:raise ValueError("Nonpositive reference")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    data=[]
    for fraction in (0.05,0.10,0.25,0.50,1.00):
        case=out/f"budget_{int(fraction*100)}";case.mkdir(exist_ok=True)
        cc=c.copy();cc.loc[hydro,"energy_budget_mwh"]=ref*fraction
        cc.to_csv(case/"capacity.csv",index=False)
        result=solve(d,case/"capacity.csv",a,case/"dispatch")
        generation=pd.read_csv(case/"dispatch"/"generation_hourly.csv")
        hydro_mwh=float(generation.loc[(generation.ba=="BPAT")&(generation.technology=="hydro"),"generation_mwh"].sum())
        if hydro_mwh>ref*fraction+0.1:raise AssertionError("Hydro energy limit violated")
        hourly=gen[(gen.ba=="BPAT")&(gen.technology=="hydro")]
        hydro_peak=float(hourly.generation_mwh.max())
        hydro_power_cap=float(cc.loc[hydro,"capacity_mw"].iloc[0])*0.1
        if hydro_peak>hydro_power_cap+0.1:raise AssertionError("Hydro hourly power limit violated")
        data.append({"hydro_budget_fraction":fraction,"hypothetical_hydro_budget_mwh":ref*fraction,
                     "optimized_hydro_mwh":hydro_mwh,
                     "hydro_energy_budget_binding":abs(hydro_mwh-ref*fraction)<0.1,
                     "max_hourly_hydro_generation_mw":hydro_peak,
                     "hydro_power_cap_mw":hydro_power_cap,
                     "bpat_shortfall_mwh":float(result.loc[result.ba=="BPAT","unserved_energy_mwh"].iloc[0])})
    frame=pd.DataFrame(data)
    if (frame.bpat_shortfall_mwh.diff().dropna()>0.1).any():raise AssertionError("Shortfall increased with more hydro energy")
    frame.to_csv(out/"wind_replay_hydro_budget_sweep.csv",index=False)
    (out/"wind_replay_hydro_budget_manifest.json").write_text(json.dumps({
      "wind_input":"EIA-930 observed net wind as hourly upper bound, not weather potential",
      "hydro_energy_scale":"EIA-930 mixed hydro plus pumped 2024-02 reported net generation",
      "hydro_power_assumed":"10% of EIA-860 nameplate","independent_validation":False,
      "historical_calibration_certified":False,
      "warning":"Mixed EIA-930 hydro+pumped net output is not a validated hydro energy resource budget."},indent=2)+"\n")
    return frame
def main():
    p=argparse.ArgumentParser()
    for key in ("wind-replay-dir","demand","observed-context","output"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    print(sweep(a.wind_replay_dir,a.demand,a.observed_context,a.output).to_string(index=False))
if __name__=="__main__":main()
