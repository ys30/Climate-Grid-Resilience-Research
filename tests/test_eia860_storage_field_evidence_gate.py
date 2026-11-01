import json
import pandas as pd
import pytest
from grid_resilience.eia860_storage_field_evidence_gate import audit

def roster(path):
    pd.DataFrame([
      {'ba':'CISO','exclusion_reason':'unmapped_primary_energy_source','primary_fuel_code':'MWH','generator_rows':224,'positive_nameplate_mw':11675.1},
      {'ba':'BPAT','exclusion_reason':'unmapped_primary_energy_source','primary_fuel_code':'MWH','generator_rows':5,'positive_nameplate_mw':34},
      {'ba':'CISO','exclusion_reason':'storage_excluded','primary_fuel_code':'WAT','generator_rows':24,'positive_nameplate_mw':2077.6},
      {'ba':'BPAT','exclusion_reason':'unmapped_primary_energy_source','primary_fuel_code':'LFG','generator_rows':28,'positive_nameplate_mw':31.2},
    ]).to_csv(path,index=False)

def test_storage_evidence_never_converts_mw_to_mwh(tmp_path):
    p=tmp_path/'roster.csv';roster(p)
    m=audit(p,tmp_path/'out')
    assert m['storage_soc_dispatch_ready'] is False
    assert m['usable_energy_mwh_available'] is False
    assert m['storage_energy_inferred_from_power'] is False
    assert m['classifications']['unmapped_primary_energy_source']['generator_rows']==229
    assert m['classifications']['storage_excluded']['generator_rows']==24
    d=pd.read_csv(tmp_path/'out'/'storage_related_ba_roster.csv')
    assert d.generator_rows.sum()==253
    assert 'LFG' not in d.to_csv(index=False)

def test_duplicate_storage_key_rejected(tmp_path):
    p=tmp_path/'roster.csv';roster(p)
    d=pd.read_csv(p);pd.concat([d,d.iloc[[0]]]).to_csv(p,index=False)
    with pytest.raises(ValueError,match='Duplicate'):
        audit(p,tmp_path/'out')

def test_negative_nameplate_rejected(tmp_path):
    p=tmp_path/'roster.csv';roster(p)
    d=pd.read_csv(p);d.loc[0,'positive_nameplate_mw']=-100;d.to_csv(p,index=False)
    with pytest.raises(ValueError,match='Invalid'):
        audit(p,tmp_path/'out')
