"""Generate labeled SOC/efficiency sensitivity inputs from verified EIA-860 storage candidates."""
import argparse,json
from pathlib import Path
import pandas as pd
from .eia860_storageunit_scenario_bridge import build

def generate(source,output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    records=[]
    reference=None
    for efficiency in (0.85,0.90,0.95):
        for soc in (0.25,0.50,0.75):
            name=f'eff{int(efficiency*100)}_soc{int(soc*100)}'
            folder=out/name
            d=build(source,folder,efficiency=efficiency,initial_soc_fraction=soc)
            fingerprint=d[['ba','power_mw','energy_mwh','generator_count']].sort_values('ba').reset_index(drop=True)
            if reference is None:reference=fingerprint
            elif not reference.equals(fingerprint):raise ValueError('Capacity changed between assumptions')
            records.append({'scenario':name,'assumed_efficiency_store':efficiency,
                'assumed_efficiency_dispatch':efficiency,'assumed_round_trip_efficiency':efficiency**2,
                'assumed_initial_soc_fraction':soc,'storage_input_csv':str(folder/'four_ba_storageunit_scenario.csv'),
                'reported_total_mwh':float(d.energy_mwh.sum()),
                'symmetric_power_mw':float(d.power_mw.sum())})
    summary=pd.DataFrame(records)
    if len(summary)!=9 or summary.scenario.duplicated().any():raise ValueError('Scenario coverage invalid')
    summary.to_csv(out/'storage_assumption_matrix.csv',index=False)
    (out/'storage_assumption_matrix_manifest.json').write_text(json.dumps({
        'scenarios':9,'official_reported_energy_and_power_held_constant':True,
        'initial_soc_and_efficiency_are_assumptions':True,
        'historical_dispatch_calibrated':False,
        'pypsa_solve_performed':False},indent=2)+'\n')
    return summary

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();print(generate(a.source,a.output).to_string(index=False))
if __name__=='__main__':main()
