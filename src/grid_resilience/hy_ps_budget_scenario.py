"""Conservative resource budget inputs for HY and PS; no inferred hourly dispatch.

The official EIA-860 nameplate figures give maximum instantaneous capability,
not an energy budget, state of charge, inflow, or historical availability.
"""
import argparse,json
from pathlib import Path

HY_MW=91.1
PS_MW=154.1
def assumptions(hydro_monthly_mwh, storage_hours, roundtrip_efficiency):
    if hydro_monthly_mwh is None or hydro_monthly_mwh<0:
        raise ValueError("Hydro energy budget must be supplied from separately documented assumptions")
    if not (0<storage_hours<=48 and 0<roundtrip_efficiency<=1):
        raise ValueError("Storage duration or efficiency outside reviewable range")
    # Positive integer-like budgets are assumed counterfactual and not derived from January +1015 automatically.
    return {"hydro_nameplate_mw":HY_MW,"hydro_monthly_dispatch_budget_mwh":float(hydro_monthly_mwh),
      "ps_discharge_nameplate_mw":PS_MW,"ps_charge_nameplate_mw_assumed":PS_MW,
      "ps_energy_capacity_mwh_assumed":PS_MW*storage_hours,
      "ps_roundtrip_efficiency_assumed":roundtrip_efficiency,
      "ps_initial_state_of_charge_assumption":"zero","hydro_budget_source":"explicit counterfactual only",
      "storage_power_and_energy_source":"EIA-860 discharge nameplate; energy duration and charging rate are counterfactual",
      "historical_calibration_certified":False}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--hydro-budget-mwh",type=float,required=True)
    a.add_argument("--storage-hours",type=float,required=True)
    a.add_argument("--roundtrip-efficiency",type=float,required=True)
    a.add_argument("--output",required=True)
    x=a.parse_args()
    result=assumptions(x.hydro_budget_mwh,x.storage_hours,x.roundtrip_efficiency)
    path=Path(x.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
