"""BPAT verified 2024 EIA860 pumped storage nameplate anchored scenario.

The EIA860 Operable PS prime movers sum to 314 MW but no source-matched
storage-sheet MWh/charge/discharge records exist. Use this ONLY as an
upper scenario power point, not observed charging/discharging capability.
A 2h/4h duration, symmetric power and efficiency remain hypothetical.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from grid_resilience.bpat_july2024_hy_ps_soc_pypsa import run

def settings_from_admission(source_manifest):
    m=json.loads(Path(source_manifest).read_text())
    if (m.get("target_ba")!="BPAT" or
        m.get("bpat_ps_prime_mover_records")!=6 or
        m.get("bpat_ps_positive_nameplate_records")!=6 or
        abs(m.get("bpat_ps_positive_nameplate_mw",float("nan"))-314)>1e-6 or
        m.get("bpat_ps_exact_generator_storage_sheet_matches")!=0 or
        m.get("physical_ps_672h_dispatch_parameters_admitted") is not False):
        raise ValueError("Expected source-observed six BPAT PS units/314 MW with unverified power-energy sheet")
    p=314.
    scenarios=((0.,0.,1.),(p,p*2,.80),(p,p*4,.80),(p,p*4,.90))
    return scenarios,m

def main():
    parser=argparse.ArgumentParser()
    for x in ("source-admission","demand","weather","capacity","source-scope","output"):
        parser.add_argument("--"+x,required=True)
    args=parser.parse_args()
    specs,admission=settings_from_admission(args.source_admission)
    scope=pd.read_csv(args.source_scope)
    if len(scope)!=1 or float(scope.iloc[0].eia923_observed_hy_mwh)!=5989476:
        raise ValueError("Missing independent EIA923 July conventional hydro reference")
    f,s,m=run(pd.read_csv(args.demand),pd.read_csv(args.weather),
        pd.read_csv(args.capacity),5989476.,args.output,settings=specs)
    record={"source_eia860_ps_2024_nameplate_mw":314.,
        "source_ps_prime_mover_generators":6,
        "source_ps_charge_mw_verified":False,
        "source_ps_discharge_mw_verified":False,
        "source_ps_usable_mwh_verified":False,
        "charge_discharge_power_314_mw_are_scenario_assumptions":True,
        "ps_duration_hours_are_assumptions":[2,4],
        "ps_roundtrip_efficiencies_are_assumptions":[.8,.9],
        "baseline_same_HY_2000MW_598947MWh":True,
        "historical_ps_dispatch_or_eens_inferred":False}
    (Path(args.output)/"bpat_314mw_ps_source_anchored_assumption_manifest.json").write_text(
        json.dumps(record,indent=2)+"\n")
    print("BPAT 314 MW NAMEPLATE ANCHORED BUT UNCALIBRATED PS SOC SENSITIVITY")
    print(s.to_string(index=False))
if __name__=="__main__":
    main()
