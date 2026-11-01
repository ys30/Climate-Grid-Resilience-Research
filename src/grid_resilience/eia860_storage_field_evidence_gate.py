"""Audit whether EIA-860 BA storage roster can support SOC-constrained dispatch.

This intentionally refuses to infer MWh from generator MW.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(roster_csv,output):
    d=pd.read_csv(roster_csv)
    req={'ba','exclusion_reason','primary_fuel_code','generator_rows','positive_nameplate_mw'}
    if not req.issubset(d):raise ValueError('Missing BA fuel roster fields')
    if d.duplicated(['ba','exclusion_reason','primary_fuel_code']).any():raise ValueError('Duplicate roster category')
    for field in ['generator_rows','positive_nameplate_mw']:
        d[field]=pd.to_numeric(d[field],errors='raise')
        if not d[field].ge(0).all() or not d[field].map(lambda x:float('-inf')<float(x)<float('inf')).all():raise ValueError('Invalid roster totals')
    related=d[(d.exclusion_reason.eq('storage_excluded'))|
              ((d.exclusion_reason.eq('unmapped_primary_energy_source')) & d.primary_fuel_code.eq('MWH'))]
    grouped=related.groupby(['ba','exclusion_reason'],as_index=False)[['generator_rows','positive_nameplate_mw']].sum()
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    grouped.to_csv(out/'storage_related_ba_roster.csv',index=False)
    totals=grouped.groupby('exclusion_reason')[['generator_rows','positive_nameplate_mw']].sum()
    report={'audit_type':'storage_related_records_not_unique_verified_battery_fleet',
            'classifications':{k:{'generator_rows':int(v.generator_rows),'nameplate_mw':float(v.positive_nameplate_mw)}
                for k,v in totals.iterrows()},
            'power_nameplate_proxy_available':True,
            'usable_energy_mwh_available':False,
            'charging_power_mw_verified':False,
            'discharging_power_mw_verified':False,
            'round_trip_efficiency_verified':False,
            'initial_soc_verified':False,
            'storage_soc_dispatch_ready':False,
            'storage_energy_inferred_from_power':False,
            'full_storage_census_certified':False,
            'notes':'Primary MWH and technology-labelled excluded categories are disjoint in this hierarchical audit. Nameplate alone cannot imply discharge power or usable energy.'}
    (out/'storage_field_evidence_gate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
def main():
    p=argparse.ArgumentParser();p.add_argument('--roster',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();print(json.dumps(audit(a.roster,a.output),indent=2))
if __name__=='__main__':main()
