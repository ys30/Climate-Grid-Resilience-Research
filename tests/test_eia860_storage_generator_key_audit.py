import pandas as pd
import pytest
from grid_resilience.eia860_storage_generator_key_audit import audit

def test_prior_merge_indicator_does_not_collide(tmp_path):
    s=tmp_path/"storage.csv";g=tmp_path/"operable.csv"
    pd.DataFrame([{"plant_id":"123","generator_id":"A","ba":"CISO","_merge":"both","energy_mwh":12}]).to_csv(s,index=False)
    pd.DataFrame([{"plant_id":"123","generator_id":"A","energy_source_1":"MWH","reported_technology":"Batteries","nameplate_capacity_mw":3}]).to_csv(g,index=False)
    report=audit(s,g,tmp_path/"out")
    assert report["matched_operable_generator_keys"]==1
    assert report["storage_only_keys"]==0

def test_normalized_duplicate_keys_rejected(tmp_path):
    s=tmp_path/"storage.csv";g=tmp_path/"operable.csv"
    pd.DataFrame([{"plant_id":"123","generator_id":"A"},{"plant_id":"123.0","generator_id":"A"}]).to_csv(s,index=False)
    pd.DataFrame([{"plant_id":"123","generator_id":"A","energy_source_1":"MWH","reported_technology":"Batteries","nameplate_capacity_mw":3}]).to_csv(g,index=False)
    with pytest.raises(ValueError,match="Duplicate normalized"):
        audit(s,g,tmp_path/"out")
