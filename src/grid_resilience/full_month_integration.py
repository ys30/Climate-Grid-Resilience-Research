"""Full-calendar-month synthetic PyPSA solve and generation coverage gate.

Integration proof only: demand/capacities/availability are synthetic, not
observations or a 2024 historical calibration.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve
from .monthly_generation_gate import monthly_generation

def run(output, year=2024, month=2):
    from calendar import monthrange
    out=Path(output)
    out.mkdir(parents=True,exist_ok=True)
    hours=monthrange(year,month)[1]*24
    times=pd.date_range(f"{year}-{month:02d}-01",periods=hours,freq="h",tz="UTC")
    bas=("CISO","AZPS")
    techs=("gas","wind")
    demand=pd.DataFrame([{"timestamp":t.isoformat(),"ba":ba,"demand_mw":80.}
                         for t in times for ba in bas])
    capacity=pd.DataFrame([{"ba":ba,"technology":tech,"capacity_mw":100. if tech=="gas" else 20.,
                            "marginal_cost":50. if tech=="gas" else 0.}
                           for ba in bas for tech in techs])
    availability=pd.DataFrame([{"timestamp":t.isoformat(),"ba":ba,"technology":tech,
                                "availability_pu":1. if tech=="gas" else 0.5}
                               for t in times for ba in bas for tech in techs])
    input_dir=out/"synthetic_inputs"
    input_dir.mkdir(parents=True,exist_ok=True)
    for name,frame in (("demand",demand),("capacity",capacity),("availability",availability)):
        frame.to_csv(input_dir/f"{name}.csv",index=False)
    shortages=solve(input_dir/"demand.csv",input_dir/"capacity.csv",
                    input_dir/"availability.csv",out/"solve")
    cover=monthly_generation(out/"solve"/"generation_hourly.csv",out/"coverage")
    if cover["periods"] != [f"{year}-{month:02d}"]:
        raise ValueError("Unexpected calendar coverage")
    if shortages.unserved_energy_mwh.sum()>1e-5:
        raise AssertionError("Synthetic installed capacity should meet hourly demand")
    result={"status":"synthetic_full_month_integration_passed",
            "hours":hours,"bas":list(bas),"technologies":list(techs),
            "shortfall_mwh":float(shortages.unserved_energy_mwh.sum()),
            "historical_calibration_certified":False,
            "notice":"Synthetic integration smoke; NOT empirical model validation."}
    (out/"synthetic_full_month_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.output),indent=2))
if __name__=="__main__":main()
