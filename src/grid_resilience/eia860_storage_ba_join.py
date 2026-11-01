"""Join official EIA-860 storage energy records to Plant balancing authority."""
import argparse,json,io,zipfile
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook

def run(archive,storage_csv,output):
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if n.endswith('2___Plant_Y2024.xlsx')]
        if len(names)!=1:raise ValueError('Missing official plant workbook')
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        try:
            rows=wb['Plant'].iter_rows(values_only=True);next(rows)
            h=list(next(rows));ix=[h.index('Plant Code'),h.index('Balancing Authority Code')]
            p=pd.DataFrame([(str(r[ix[0]]).strip().removesuffix('.0'),str(r[ix[1]]).strip())
                for r in rows if r[ix[0]] is not None],columns=['plant_id','ba'])
        finally:wb.close()
    if p.plant_id.duplicated().any():raise ValueError('Duplicate plant IDs')
    s=pd.read_csv(storage_csv,dtype={'plant_id':str,'generator_id':str})
    s.plant_id=s.plant_id.str.strip().str.removesuffix('.0')
    if s.duplicated(['plant_id','generator_id']).any():raise ValueError('Duplicate storage keys')
    matched=s.merge(p,on='plant_id',how='left',validate='many_to_one',indicator=True)
    target=matched.loc[matched.ba.isin(['AZPS','BPAT','CISO','SRP'])].copy()
    if target.empty:raise ValueError('No four-BA storage records matched')
    target['storage_input_complete']=target[['energy_mwh','charge_mw','discharge_mw']].gt(0).all(axis=1)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    target.to_csv(out/'eia860_four_ba_storage_matched.csv',index=False)
    report=target.groupby('ba').agg(
        storage_records=('generator_id','size'),
        complete_power_energy_records=('storage_input_complete','sum'),
        nameplate_energy_mwh=('energy_mwh',lambda x:float(x[x>0].sum())),
        reported_charge_mw=('charge_mw',lambda x:float(x[x>0].sum())),
        reported_discharge_mw=('discharge_mw',lambda x:float(x[x>0].sum()))
    ).reset_index()
    report.to_csv(out/'eia860_four_ba_storage_summary.csv',index=False)
    manifest={'source_storage_rows':int(len(s)),'national_unmatched_plant_rows':int(matched._merge.ne('both').sum()),
        'four_ba_storage_rows':int(len(target)),'four_ba_complete_rows':int(target.storage_input_complete.sum()),
        'true_energy_mwh_extracted':True,'ba_plant_code_matched':True,
        'generator_key_consistency_with_general_roster_checked':False,
        'initial_soc_observed':False,'efficiency_observed':False,
        'historic_storage_dispatch_calibrated':False}
    (out/'eia860_four_ba_storage_match_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return report
def main():
    p=argparse.ArgumentParser()
    for k in ('archive','storage','output'):p.add_argument('--'+k,required=True)
    a=p.parse_args();print(run(a.archive,a.storage,a.output).to_string(index=False))
if __name__=='__main__':main()
