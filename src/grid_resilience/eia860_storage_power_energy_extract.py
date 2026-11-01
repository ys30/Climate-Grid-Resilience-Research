"""Extract independently reported EIA-860 2024 operating storage power and energy."""
import argparse,io,json,zipfile
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook

REQUIRED=['Plant Code','Generator ID','Nameplate Energy Capacity (MWh)',
          'Maximum Charge Rate (MW)','Maximum Discharge Rate (MW)',
          'Operating Month','Operating Year','Storage Technology 1']

def extract(archive,output):
    with zipfile.ZipFile(archive) as z:
        found=[n for n in z.namelist() if '3_4_Energy_Storage' in n and n.endswith('.xlsx')]
        if len(found)!=1:raise ValueError('Expected exactly one official storage workbook')
        wb=load_workbook(io.BytesIO(z.read(found[0])),read_only=True,data_only=True)
        try:
            rows=wb['Operable'].iter_rows(values_only=True)
            next(rows)
            hdr=[str(x).strip() if x is not None else '' for x in next(rows)]
            if any(hdr.count(k)!=1 for k in REQUIRED):raise ValueError('Missing/ambiguous storage column')
            indexes={k:hdr.index(k) for k in REQUIRED}
            data=[]
            for r in rows:
                if r[indexes['Plant Code']] is None:continue
                data.append({k:(r[i] if i<len(r) else None) for k,i in indexes.items()})
        finally:wb.close()
    df=pd.DataFrame(data).rename(columns={
        'Plant Code':'plant_id','Generator ID':'generator_id',
        'Nameplate Energy Capacity (MWh)':'energy_mwh',
        'Maximum Charge Rate (MW)':'charge_mw',
        'Maximum Discharge Rate (MW)':'discharge_mw',
        'Operating Month':'operating_month','Operating Year':'operating_year',
        'Storage Technology 1':'storage_technology'})
    if df.empty:raise ValueError('No operating storage rows')
    for k in ('plant_id','generator_id'):
        df[k]=df[k].astype(str).str.strip().str.replace(r'\\.0$','',regex=True)
    if df.duplicated(['plant_id','generator_id']).any():raise ValueError('Duplicate storage key')
    for field in ('energy_mwh','charge_mw','discharge_mw','operating_month','operating_year'):
        df[field]=pd.to_numeric(df[field],errors='coerce')
    power_fields=['energy_mwh','charge_mw','discharge_mw']
    positive=df[power_fields].gt(0).all(axis=1)&df[power_fields].notna().all(axis=1)
    df['all_three_positive_reported']=positive
    df['duration_hours_when_complete']=(df.energy_mwh/df.discharge_mw).where(positive)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/'eia860_2024_storage_operable_power_energy.csv',index=False)
    result={'storage_operable_rows':int(len(df)),
            'rows_with_positive_energy_charge_discharge':int(positive.sum()),
            'rows_incomplete':int((~positive).sum()),
            'all_rows_have_operating_date':bool(df[['operating_month','operating_year']].notna().all(axis=1).all()),
            'actual_storage_parameters_extracted':True,'ba_matched':False,
            'initial_soc_observed':False,'efficiency_observed':False,
            'historical_dispatch_calibrated':False,
            'source_workbook':found[0]}
    (out/'eia860_2024_storage_power_energy_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();print(json.dumps(extract(a.archive,a.output),indent=2))
if __name__=='__main__':main()
