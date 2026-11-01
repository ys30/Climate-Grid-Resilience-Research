"""Inspect official EIA-860 2024 energy-storage worksheet; do not infer MWh from MW."""
import argparse,io,json,zipfile
from pathlib import Path
from openpyxl import load_workbook

def inspect(archive,output):
    with zipfile.ZipFile(archive) as z:
        matches=[n for n in z.namelist() if '3_4_Energy_Storage' in n and n.lower().endswith('.xlsx')]
        if len(matches)!=1:raise ValueError('Expected exactly one EIA-860 energy storage workbook')
        wb=load_workbook(io.BytesIO(z.read(matches[0])),read_only=True,data_only=True)
        sheets={}
        try:
            for ws in wb.worksheets:
                rows=ws.iter_rows(values_only=True)
                preview=list(__import__('itertools').islice(rows,5))
                # Official workbook generally has a title row followed by exact column headers.
                headers=max(preview,key=lambda r:sum(v is not None for v in r))
                normalized=[str(v).strip() if v is not None else '' for v in headers]
                sheets[ws.title]={'columns':normalized,
                    'energy_mwh_candidates':[x for x in normalized if ('mwh' in x.lower() or ('energy' in x.lower() and 'capacity' in x.lower()))],
                    'power_mw_candidates':[x for x in normalized if ('mw' in x.lower() and 'mwh' not in x.lower()) or 'discharge rate' in x.lower()],
                    'plant_key_columns':[x for x in normalized if x.lower() in ('plant code','generator id')]}
        finally:wb.close()
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    result={'source_workbook':matches[0],'sheets':sheets,
            'schema_discovery_only':True,'actual_energy_mwh_matched_to_ba':False,
            'storage_dispatch_calibrated':False}
    (out/'eia860_2024_storage_schema.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();print(json.dumps(inspect(a.archive,a.output),indent=2))
if __name__=='__main__':main()
