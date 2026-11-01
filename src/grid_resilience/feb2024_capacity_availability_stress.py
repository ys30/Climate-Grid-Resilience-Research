"""Run explicitly hypothetical constant-availability stress checks on EIA input screening.

All derating levels are scenario assumptions, not historical outage rates.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve

def run(demand_csv,capacity_csv,availability_csv,output,levels=(0.7,0.4)):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    base=pd.read_csv(availability_csv)
    if not {"timestamp","ba","technology","availability_pu"}.issubset(base):
        raise ValueError("Availability schema mismatch")
    if base.empty or not base.availability_pu.eq(1).all():
        raise ValueError("Screening reference must have 100% availability")
    if len(set(levels))!=len(levels) or any(not 0<x<1 for x in levels):
        raise ValueError("Derating levels must be unique and in (0,1)")
    rows=[]
    for fraction in levels:
        case=f"constant_available_{int(round(fraction*100))}pct"
        p=out/case;p.mkdir(parents=True,exist_ok=True)
        alt=base.copy()
        alt["availability_pu"]=fraction
        alt.to_csv(p/"assumed_availability.csv",index=False)
        result=solve(demand_csv,capacity_csv,p/"assumed_availability.csv",p/"solve")
        for row in result.itertuples(index=False):
            rows.append({"scenario":case,"ba":row.ba,
                         "availability_fraction_assumed":fraction,
                         "unserved_energy_mwh":float(row.unserved_energy_mwh)})
    pd.DataFrame(rows).sort_values(["scenario","ba"]).to_csv(
        out/"hypothetical_availability_shortfall.csv",index=False)
    report={"scenario_assumption":"Uniform 70% and 40% availability across all included technologies",
            "scenarios":len(levels),"ba_scenario_rows":len(rows),
            "historical_outage_rate_inferred":False,
            "historical_calibration_certified":False,
            "warning":"Counterfactual uniform derating is not an empirical weather model or verified reliability forecast."}
    (out/"hypothetical_availability_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    for k in ("demand","capacity","availability","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    print(json.dumps(run(a.demand,a.capacity,a.availability,a.output),indent=2))
if __name__=="__main__":main()
