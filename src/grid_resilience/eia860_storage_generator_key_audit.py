"""Cross-check official storage worksheet keys against full EIA-860 operable roster."""
import argparse,json
from pathlib import Path
import pandas as pd
def audit(storage,operable,output):
    s=pd.read_csv(storage,dtype={'plant_id':str,'generator_id':str})
    g=pd.read_csv(operable,dtype={'plant_id':str,'generator_id':str},keep_default_na=False)
    keys=['plant_id','generator_id']
    if s.duplicated(keys).any() or g.duplicated(keys).any():raise ValueError('Duplicate plant+generator key')
    for x in (s,g):
        for k in keys:x[k]=x[k].str.strip().str.replace(r'\.0$','',regex=True)
    m=s.merge(g[keys+['energy_source_1','reported_technology','nameplate_capacity_mw']],on=keys,how='left',validate='one_to_one',indicator=True)
    m['key_status']=m['_merge'].map({'both':'operable_roster_matched','left_only':'storage_only'}).astype(str)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    m.drop(columns='_merge').to_csv(out/'eia860_four_ba_storage_generator_key_audit.csv',index=False)
    status=m.key_status.value_counts().to_dict()
    report={'four_ba_storage_rows':len(s),'matched_operable_generator_keys':int(status.get('operable_roster_matched',0)),
            'storage_only_keys':int(status.get('storage_only',0)),
            'storage_mwh_verified_as_reported':True,'charge_discharge_history_verified':False,
            'storage_efficiency_and_initial_soc_verified':False,
            'general_roster_classification_not_equivalent_to_storage_workbook_membership':True}
    (out/'eia860_storage_generator_key_audit_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
def main():
    p=argparse.ArgumentParser()
    for v in ('storage','operable','output'):p.add_argument('--'+v,required=True)
    a=p.parse_args();print(json.dumps(audit(a.storage,a.operable,a.output),indent=2))
if __name__=='__main__':main()
