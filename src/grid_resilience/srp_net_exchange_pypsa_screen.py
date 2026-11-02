"""EIA-930 hourly demand plus *signed* interchange as an exogenous dispatch screen.

Positive interchange is an export sink, negative interchange an import source.
Imports are held fixed as observed; this does NOT simulate transfer capability.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from grid_resilience.monthly_pypsa_screen import run

def screened_load(balance,ba):
    required={"timestamp","demand_mw","generation_mw","interchange_mw"}
    if not required.issubset(balance):raise ValueError("Missing EIA-930 balance columns")
    d=balance.copy()
    d["timestamp"]=pd.to_datetime(d.timestamp,utc=True,errors="raise")
    for key in ["demand_mw","generation_mw","interchange_mw"]:
        d[key]=pd.to_numeric(d[key],errors="raise")
    if d[list(required)].isna().any().any() or d.timestamp.duplicated().any():
        raise ValueError("Missing or duplicate EIA-930 hours")
    if (d.demand_mw<0).any() or (d.generation_mw<0).any():
        raise ValueError("Unexpected negative demand or generation")
    d["net_supply_required_mw"]=d.demand_mw+d.interchange_mw
    if (d.net_supply_required_mw<0).any():
        raise ValueError("Observed import larger than demand; explicit import treatment required")
    return pd.DataFrame({"timestamp":d.timestamp,"ba":ba,"demand_mw":d.net_supply_required_mw})

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--balance",required=True);a.add_argument("--capacity",required=True)
    a.add_argument("--ba",default="SRP");a.add_argument("--year",type=int,default=2024)
    a.add_argument("--month",type=int,default=1);a.add_argument("--output",required=True)
    x=a.parse_args()
    balance=pd.read_csv(x.balance)
    load=screened_load(balance,x.ba)
    generations,shortages=run(load,pd.read_csv(x.capacity),x.year,x.month)
    output=Path(x.output);output.mkdir(parents=True,exist_ok=True)
    load.to_csv(output/"eia930_demand_plus_net_exports.csv",index=False)
    generations.to_csv(output/"modeled_generation_with_net_exchange.csv",index=False)
    (output/"interchange_screen_manifest.json").write_text(json.dumps({
       "ba":x.ba,"period":f"{x.year}-{x.month:02d}",
       "observed_local_demand_mwh":float(balance.demand_mw.sum()),
       "observed_net_interchange_mwh":float(balance.interchange_mw.sum()),
       "exogenous_supply_requirement_mwh":float(load.demand_mw.sum()),
       "modeled_supply_mwh":float(generations.modeled_generation_mwh.sum()),
       "modeled_unserved_mwh":float(shortages[x.ba]),
       "real_network_interchange_simulated":False,"historical_calibration_certified":False,
       "limitations":"Observed net interchange fixed exogenously; all candidate generators assumed always available, incomplete BA fleet, no transmission topology."
       },indent=2)+"\n")
    print((output/"interchange_screen_manifest.json").read_text())
if __name__=="__main__":main()
