"""Read official EIA-930 six-month Balance CSV/ZIP supplied as a file.

No download assumptions; strict UTC-hour completeness. EIA Balance columns
commonly include 'Balancing Authority', 'UTC Time at End of Hour', 'Demand (MW)'.
"""
import argparse,io,zipfile
from pathlib import Path
import pandas as pd

def extract(path,ba,year,month):
    path=Path(path)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            matches=[n for n in z.namelist() if 'balance' in n.lower() and n.lower().endswith('.csv')]
            if len(matches)!=1:raise ValueError(f'Expected exactly one Balance CSV: {matches}')
            data=pd.read_csv(io.BytesIO(z.read(matches[0])),low_memory=False)
    else:data=pd.read_csv(path,low_memory=False)
    required=['Balancing Authority','UTC Time at End of Hour','Demand (MW)']
    missing=[x for x in required if x not in data]
    if missing:raise ValueError(f'Missing Balance columns: {missing}; found {list(data.columns)[:25]}')
    d=data.loc[data['Balancing Authority'].astype(str).str.strip().eq(ba),required].copy()
    if d.empty:raise ValueError(f'No records for {ba}')
    # EIA-930 Balance timestamps are END of hour; normalize to START-hour
    d['timestamp']=pd.to_datetime(d['UTC Time at End of Hour'],utc=True,errors='raise')-pd.Timedelta(hours=1)
    start=pd.Timestamp(f'{year}-{month:02d}-01',tz='UTC')
    end=start+pd.offsets.MonthBegin(1)
    d=d[(d.timestamp>=start)&(d.timestamp<end)].copy()
    d['demand_mw']=pd.to_numeric(d['Demand (MW)'],errors='coerce')
    if d.demand_mw.isna().any() or (d.demand_mw<0).any():raise ValueError('Missing or negative demand')
    if d.timestamp.duplicated().any():raise ValueError('Duplicate UTC hour')
    expected=pd.date_range(start,end,freq='h',inclusive='left')
    if not pd.DatetimeIndex(d.timestamp.sort_values()).equals(expected):
        raise ValueError(f'Incomplete UTC hours: {len(d)} vs {len(expected)}')
    return d.sort_values('timestamp')[['timestamp','demand_mw']].assign(ba=ba)[['timestamp','ba','demand_mw']]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--archive',required=True);p.add_argument('--ba',required=True)
    p.add_argument('--year',type=int,required=True);p.add_argument('--month',type=int,required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    r=extract(a.archive,a.ba,a.year,a.month)
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);r.to_csv(out,index=False)
    print(f'Validated {len(r)} observed UTC demand hours; source {a.archive}')
if __name__=='__main__':main()
