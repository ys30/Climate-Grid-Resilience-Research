"""Convert official storage candidates into an explicitly assumed PyPSA StorageUnit scenario.

StorageUnit has symmetric nominal charging/discharging power. Use the smaller
of summed reported charge and discharge ratings per BA, conservatively.
This scenario is NOT observed historical storage dispatch.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def build(source,output,efficiency=0.9,initial_soc_fraction=0.5):
    if not (0<efficiency<=1 and 0<=initial_soc_fraction<=1):
        raise ValueError('Invalid scenario assumptions')
    d=pd.read_csv(source,dtype={'plant_id':str,'generator_id':str})
    required={'plant_id','generator_id','ba','energy_mwh','charge_mw','discharge_mw'}
    if not required.issubset(d) or d.empty or d.duplicated(['plant_id','generator_id']).any():
        raise ValueError('Invalid storage candidate roster')
    for k in ('energy_mwh','charge_mw','discharge_mw'):
        d[k]=pd.to_numeric(d[k],errors='raise')
        if not d[k].map(lambda x: 0<float(x)<float('inf')).all():
            raise ValueError('Missing or nonpositive official capacity')
    if not set(d.ba).issubset({'AZPS','BPAT','CISO','SRP'}):
        raise ValueError('Unexpected BA')
    g=d.groupby('ba',as_index=False).agg(energy_mwh=('energy_mwh','sum'),
        reported_charge_mw=('charge_mw','sum'),reported_discharge_mw=('discharge_mw','sum'),
        generator_count=('generator_id','size'))
    g['power_mw']=g[['reported_charge_mw','reported_discharge_mw']].min(axis=1)
    g['efficiency_store']=efficiency
    g['efficiency_dispatch']=efficiency
    g['initial_soc_fraction']=initial_soc_fraction
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    g[['ba','power_mw','energy_mwh','efficiency_store','efficiency_dispatch','initial_soc_fraction']].to_csv(out/'four_ba_storageunit_scenario.csv',index=False)
    g.to_csv(out/'four_ba_storageunit_capacity_bridge_audit.csv',index=False)
    meta={'reported_storage_energy_and_power':True,
          'power_derivation':'min(sum_charge_MW,sum_discharge_MW) per BA, symmetric StorageUnit approximation',
          'round_trip_efficiency_assumed':efficiency**2,
          'per_direction_efficiency_assumed':efficiency,
          'initial_soc_fraction_assumed':initial_soc_fraction,
          'historical_storage_dispatch_validated':False,
          'empirical_reliability_calibrated':False}
    (out/'four_ba_storageunit_scenario_manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
    return g
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',required=True);p.add_argument('--output',required=True)
    p.add_argument('--efficiency',type=float,default=0.9)
    p.add_argument('--initial-soc-fraction',type=float,default=0.5)
    a=p.parse_args();print(build(a.source,a.output,a.efficiency,a.initial_soc_fraction).to_string(index=False))
if __name__=='__main__':main()
