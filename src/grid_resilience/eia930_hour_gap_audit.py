"""Diagnose UTC-hour gaps in EIA-930 semiannual Balance CSV before modeling."""
import argparse,json
from pathlib import Path
import pandas as pd
def audit(path,ba,year,month,out):
    frame=pd.read_csv(path,low_memory=False)
    needed=['Balancing Authority','UTC Time at End of Hour','Demand (MW)']
    if not set(needed).issubset(frame.columns):raise ValueError('Unexpected Balance CSV schema')
    g=frame[frame['Balancing Authority'].astype(str).str.strip()==ba].copy()
    g['hour_start_utc']=pd.to_datetime(g['UTC Time at End of Hour'],utc=True,errors='raise')-pd.Timedelta(hours=1)
    start=pd.Timestamp(f'{year}-{month:02d}-01',tz='UTC');end=start+pd.offsets.MonthBegin(1)
    g=g[(g.hour_start_utc>=start)&(g.hour_start_utc<end)]
    expected=pd.date_range(start,end,freq='h',inclusive='left')
    present=pd.DatetimeIndex(g.hour_start_utc)
    missing=expected.difference(present)
    duplicated=g[g.hour_start_utc.duplicated(keep=False)]
    g['demand_numeric']=pd.to_numeric(g['Demand (MW)'],errors='coerce')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame({'missing_hour_start_utc':missing.astype(str)}).to_csv(out/'missing_hours.csv',index=False)
    duplicated[['hour_start_utc','Demand (MW)']].to_csv(out/'duplicate_hours.csv',index=False)
    summary={'ba':ba,'year':year,'month':month,'expected_hours':len(expected),
             'source_rows_in_month':len(g),'distinct_source_hours':present.nunique(),
             'missing_hour_count':len(missing),'duplicate_row_count':len(duplicated),
             'invalid_demand_count':int(g.demand_numeric.isna().sum()),
             'valid_for_full_month_model':bool(len(missing)==0 and duplicated.empty and g.demand_numeric.notna().all())}
    (out/'hour_coverage_audit.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    return summary
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--csv',required=True);p.add_argument('--ba',required=True)
    p.add_argument('--year',type=int,required=True);p.add_argument('--month',type=int,required=True);p.add_argument('--output',required=True)
    a=p.parse_args();audit(a.csv,a.ba,a.year,a.month,a.output)
if __name__=='__main__':main()
