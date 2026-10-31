"""Counterfactual BPAT hydro capacity sensitivity, NOT observed hydro dispatch.

Adds hypothetical firm hydro nameplate to the existing isolated-BA model.
No inference about historic hydro availability or pumped-storage SOC is made.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve

def run(demand,capacity,availability,output,hydro_mw=(0,1000,2000)):
    d=Path(demand);c=pd.read_csv(capacity);a=pd.read_csv(availability)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    if "BPAT" not in set(c.ba):raise ValueError("BPAT missing")
    if ((c.ba=="BPAT")&(c.technology=="hydro")).any():
        raise ValueError("Existing BPAT hydro: refuse double counting")
    if not {"timestamp","ba","technology","availability_pu"}.issubset(a):
        raise ValueError("Missing availability fields")
    times=a.timestamp.drop_duplicates()
    results=[]
    for add_mw in hydro_mw:
        if add_mw<0:raise ValueError("Nonnegative hydro sensitivity only")
        case=out/f"hydro_plus_{add_mw}_mw";case.mkdir(exist_ok=True)
        cap=c.copy();avail=a.copy()
        if add_mw:
            cap=pd.concat([cap,pd.DataFrame([{"ba":"BPAT","technology":"hydro",
                "capacity_mw":add_mw,"marginal_cost":0}])],ignore_index=True)
            avail=pd.concat([avail,pd.DataFrame({"timestamp":times,
                "ba":"BPAT","technology":"hydro","availability_pu":1.0})],ignore_index=True)
        cap.to_csv(case/"capacity.csv",index=False)
        avail.to_csv(case/"availability.csv",index=False)
        shortages=solve(d,case/"capacity.csv",case/"availability.csv",case/"dispatch")
        for r in shortages.itertuples(index=False):
            results.append({"scenario_hydro_added_mw":add_mw,"ba":r.ba,
                            "modeled_shortfall_mwh":r.unserved_energy_mwh})
    pd.DataFrame(results).to_csv(out/"hypothetical_hydro_sensitivity.csv",index=False)
    meta={"historical_calibration_certified":False,
          "scenario_is_observed_hydropower":False,
          "hydro_availability_assumed":1.0,
          "bp_attribution":"Hypothetical BPAT hydro injection, not validated EIA-860 physical additional capacity",
          "model_transport_links":False,"hydro_additions_mw":list(hydro_mw),
          "pumped_storage_modeled":False,
          "warning":"Do not report sensitivity as real historical shortage or verified hydro capacity."}
    (out/"hypothetical_hydro_sensitivity_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    return pd.DataFrame(results)
def main():
    p=argparse.ArgumentParser()
    for x in ("demand","capacity","availability","output"):p.add_argument("--"+x,required=True)
    a=p.parse_args();print(run(a.demand,a.capacity,a.availability,a.output).to_string(index=False))
if __name__=="__main__":main()
