"""Offline EIA-930 Balance archive -> complete UTC-month PyPSA screen.

Requires externally reviewed capacity CSV. A model result is NOT empirical calibration.
"""
import argparse,hashlib,json
from pathlib import Path
import pandas as pd
from grid_resilience.eia930_balance_archive_import import extract
from grid_resilience.monthly_pypsa_screen import run

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--archive',required=True);p.add_argument('--capacity',required=True)
    p.add_argument('--ba',required=True);p.add_argument('--year',type=int,required=True)
    p.add_argument('--month',type=int,required=True);p.add_argument('--output',required=True)
    a=p.parse_args()
    d=extract(a.archive,a.ba,a.year,a.month)
    c=pd.read_csv(a.capacity)
    if c.empty or set(c.ba)!={a.ba}:raise ValueError('Capacity must cover exactly requested BA')
    modeled,unserved=run(d,c,a.year,a.month)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    d.to_csv(out/'validated_hourly_demand.csv',index=False)
    modeled.to_csv(out/'modeled_monthly_generation.csv',index=False)
    sha=hashlib.sha256(Path(a.archive).read_bytes()).hexdigest()
    (out/'real_input_screen_manifest.json').write_text(json.dumps({
        'input_archive_sha256':sha,'ba':a.ba,'year':a.year,'month':a.month,
        'observed_hour_count':len(d),'observed_demand_mwh':float(d.demand_mw.sum()),
        'unserved_mwh_by_ba':unserved,'calibrated':False,
        'limits':'Isolated BA, no interchanges, flat generator availability, externally supplied capacities; no generation validation.'
    },indent=2)+'\n')
    print('Source-backed monthly PyPSA screening completed; NOT calibrated')
if __name__=='__main__':main()
