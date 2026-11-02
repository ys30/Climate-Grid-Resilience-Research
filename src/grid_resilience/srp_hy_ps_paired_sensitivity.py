"""Run paired observed-boundary SRP screens, baseline vs explicit HY/PS assumptions."""
import argparse,json
from pathlib import Path
import pandas as pd
from grid_resilience.bidirectional_interchange_screen import solve
from grid_resilience.hy_ps_budget_scenario import assumptions

def main():
    p=argparse.ArgumentParser()
    for k in ("balance","capacity","output"):p.add_argument("--"+k,required=True)
    p.add_argument("--year",type=int,default=2024);p.add_argument("--month",type=int,default=1)
    p.add_argument("--ba",default="SRP");p.add_argument("--hydro-budget-mwh",type=float,default=1015.)
    p.add_argument("--storage-hours",type=float,default=4.)
    p.add_argument("--roundtrip-efficiency",type=float,default=.81)
    a=p.parse_args()
    balance=pd.read_csv(a.balance);capacity=pd.read_csv(a.capacity)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    prior=solve(balance,capacity,a.year,a.month,a.ba,hourly_output=out/"baseline_hourly_diagnostics.csv")
    settings=assumptions(a.hydro_budget_mwh,a.storage_hours,a.roundtrip_efficiency)
    scenario=solve(balance,capacity,a.year,a.month,a.ba,resource_settings=settings,hourly_output=out/"hy_ps_hourly_diagnostics.csv")
    delta=prior["modeled_unserved_mwh"]-scenario["modeled_unserved_mwh"]
    report={"baseline":prior,"scenario":scenario,"delta_unserved_mwh":delta,
        "hydro_budget_is_explicit_scenario_not_verified_availability":True,
        "storage_duration_and_efficiency_are_assumed":True,
        "historical_calibration_certified":False}
    (out/"hy_ps_paired_sensitivity.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
