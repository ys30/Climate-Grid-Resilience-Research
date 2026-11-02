import pandas as pd
import pytest
from grid_resilience.eia923_full_observation_ledger import build

def fixtures():
    p=pd.DataFrame([
        {"plant_id":"0001","generator_id":"A","reported_ba":"SRP","period":"2024-01","generation_mwh":30},
        {"plant_id":"2","generator_id":"B","reported_ba":"CISO","period":"2024-01","generation_mwh":-5}])
    e=pd.DataFrame([{"plant_id":"1","generator_id":"A"}])
    return p,e

def test_retains_matched_and_unmatched_signed_generation():
    x,y=fixtures()
    r=build(x,y)
    assert r.generation_mwh.sum()==25
    assert set(r.identity_status)=={"in_2024_operable_identity_list","outside_2024_operable_identity_list"}
    assert not r.historical_capacity_certified.any()

def test_duplicate_month_fails():
    x,y=fixtures()
    with pytest.raises(ValueError,match="Duplicate reported"):
        build(pd.concat([x,x.iloc[[0]]]),y)

def test_nan_energy_fails():
    x,y=fixtures()
    x.loc[0,"generation_mwh"]=None
    with pytest.raises(ValueError,match="Missing/nonfinite"):
        build(x,y)
