"""Controlled storage depletion proof: initial SOC must matter when replenishment is impossible."""
import json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve

def run(output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    ts=pd.date_range("2024-07-01T00:00:00Z",periods=4,freq="h")
    pd.DataFrame({"timestamp":ts,"ba":["AZPS"]*4,"demand_mw":[10.]*4}).to_csv(out/"demand.csv",index=False)
    pd.DataFrame([{"ba":"AZPS","technology":"gas","capacity_mw":0.,
                   "marginal_cost":100.}]).to_csv(out/"capacity.csv",index=False)
    pd.DataFrame({"timestamp":ts,"ba":["AZPS"]*4,"technology":["gas"]*4,
                  "availability_pu":[1.]*4}).to_csv(out/"availability.csv",index=False)
    results={}
    for fraction in (0.0,0.5,1.0):
        name=f"soc{int(fraction*100)}"
        pd.DataFrame([{"ba":"AZPS","power_mw":10.,"energy_mwh":10.,
                      "efficiency_store":1.,"efficiency_dispatch":1.,
                      "initial_soc_fraction":fraction}]).to_csv(out/(name+"_storage.csv"),index=False)
        r=solve(out/"demand.csv",out/"capacity.csv",out/"availability.csv",
                out/name,storage_csv=out/(name+"_storage.csv"))
        results[name]=float(r.unserved_energy_mwh.sum())
    if not abs(results["soc0"]-40)<1e-5:raise AssertionError(results)
    if not abs(results["soc50"]-35)<1e-5:raise AssertionError(results)
    if not abs(results["soc100"]-30)<1e-5:raise AssertionError(results)
    report={"case":"synthetic_finite_energy_no_recharge",
            "shortfall_mwh_by_initial_soc":results,
            "initial_soc_effect_verified":True,
            "historical_grid_validation":False,
            "does_not_explain_large_fleet_zero_soc_sensitivity":True}
    (out/"soc_initial_state_stress_test.json").write_text(json.dumps(report,indent=2)+"\n")
    return report
def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--output",required=True);a=p.parse_args()
    print(json.dumps(run(a.output),indent=2))
if __name__=="__main__":main()
