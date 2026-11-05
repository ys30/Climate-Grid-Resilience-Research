"""BPAT Grand Coulee PS irrigation-competition availability sensitivity.

A USBR-source-grounded *reason to test restricted availability*, NOT
observed 2024 pumping/irrigation rights. The available fraction of the
314MW six-unit nameplate (0/.25/.5/1) and proportional 4h usable energy
are explicitly hypothetical, separate from historical reservoir levels.
Same 672-hour July original input, partial gas/wind and assumed HY.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from grid_resilience.bpat_july2024_hy_ps_soc_pypsa import run

FRACTIONS=(0.,0.25,0.50,1.00)
ASSUMED_DURATION_H=4.
ASSUMED_ROUNDTRIP=0.80

def derive_scenarios(usbr_path,ps_admission_path):
    u=json.loads(Path(usbr_path).read_text())
    p=json.loads(Path(ps_admission_path).read_text())
    if (u.get("eia860_2024_plant_id")!="6163" or
        u.get("physical_reversible_PS_generating_units")!=6 or
        u.get("Banks_Lake_upper_reservoir_and_irrigation_water_storage") is not True or
        u.get("PS_usable_MWh_verified") is not False or
        p.get("bpat_ps_prime_mover_records")!=6 or
        abs(float(p.get("bpat_ps_positive_nameplate_mw",-1))-314.)>.001 or
        p.get("physical_ps_672h_dispatch_parameters_admitted") is not False):
        raise ValueError("Original USBR/EIA860 PS identity or missing-MWh protection gate failed")
    scenarios=tuple((314.*f,314.*f*ASSUMED_DURATION_H,
                     1. if f==0 else ASSUMED_ROUNDTRIP) for f in FRACTIONS)
    return scenarios

def main():
    a=argparse.ArgumentParser()
    for k in ("usbr-gate","ps-admission","demand","weather","capacity","hy-source-scope","output"):
        a.add_argument("--"+k,required=True)
    x=a.parse_args()
    specs=derive_scenarios(x.usbr_gate,x.ps_admission)
    scope=pd.read_csv(x.hy_source_scope)
    if len(scope)!=1 or float(scope.iloc[0].eia923_observed_hy_mwh)!=5989476.:
        raise ValueError("Original EIA923 actual July BPAT HY source scale not verified")
    f,s,m=run(pd.read_csv(x.demand),pd.read_csv(x.weather),
        pd.read_csv(x.capacity),5989476.,x.output,settings=specs)
    root=Path(x.output)
    evidence={
        "original_usbr_Grand_Coulee_irrigation_role_checked":True,
        "original_eia860_six_ps_2024_nameplate_mw":314.,
        "source_rated_ps_discharge_MW_is_not_2024_hourly_available":True,
        "water_allocation_fraction_observed":False,
        "hypothetical_available_PS_fraction_of_nameplate":list(FRACTIONS),
        "hypothetical_duration_hours":ASSUMED_DURATION_H,
        "hypothetical_roundtrip_efficiency":ASSUMED_ROUNDTRIP,
        "historical_Banks_Lake_level_irrigation_flow_or_PS_SOC_observed":False,
        "source_energy_capacity_MWh_observed":False,
        "counterfactual_model_is_four_isolated_BA_incomplete_fleet":True,
        "historical_real_blackouts_or_avoided_EENS":False
    }
    (root/"grand_coulee_irrigation_competition_assumptions.json").write_text(json.dumps(evidence,indent=2)+"\n")
    print("GRAND COULEE IRRIGATION-DRIVEN UNCERTAINTY STRESS ASSUMPTIONS, NOT OBSERVED PS ACCESS")
    print(s.to_string(index=False))
if __name__=="__main__":main()
