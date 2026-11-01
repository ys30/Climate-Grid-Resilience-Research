"""Prepare observed EIA-860 storage capacity candidates, without invented SOC or efficiency."""
import argparse,json
from pathlib import Path
import pandas as pd

def build(source,output):
    d=pd.read_csv(source,dtype={'plant_id':str,'generator_id':str})
    keys=['plant_id','generator_id']
    if d.duplicated(keys).any():raise ValueError('Duplicate generator key')
    required={'ba','energy_mwh','charge_mw','discharge_mw','storage_input_complete'}
    if not required.issubset(d):raise ValueError('Missing storage matching fields')
    for k in ('energy_mwh','charge_mw','discharge_mw'):d[k]=pd.to_numeric(d[k],errors='coerce')
    good=d[list(('energy_mwh','charge_mw','discharge_mw'))].gt(0).all(axis=1)
    if good.sum()!=d.storage_input_complete.astype(str).str.lower().eq('true').sum():raise ValueError('Completeness marker inconsistent')
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    candidates=d.loc[good,keys+['ba','energy_mwh','charge_mw','discharge_mw','storage_technology']].copy()
    candidates['reported_duration_hours']=candidates.energy_mwh/candidates.discharge_mw
    candidates.to_csv(out/'four_ba_reported_storage_candidates.csv',index=False)
    excluded=d.loc[~good,keys+['ba','energy_mwh','charge_mw','discharge_mw']].copy()
    excluded.to_csv(out/'four_ba_storage_incomplete.csv',index=False)
    m={'matched_storage_records':int(len(d)),'complete_candidates':int(good.sum()),
       'incomplete_records':int((~good).sum()),'actual_energy_charge_discharge_reported':True,
       'efficiency_assumed':False,'initial_soc_assumed':False,'pypsa_dispatch_ready':False,
       'warning':'Reported capacity inputs only; no guessed efficiency, initial SOC or historical dispatch.'}
    (out/'four_ba_reported_storage_candidates_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    return m
def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();print(json.dumps(build(a.source,a.output),indent=2))
if __name__=='__main__':main()
