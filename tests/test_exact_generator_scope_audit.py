import pandas as pd
import pytest
from grid_resilience.exact_generator_scope_audit import validate

def test_identity_does_not_substitute_same_fuel():
    observed=pd.DataFrame([
        {"plant_id":"001","generator_id":"A","reported_ba":"SRP","period":"2024-01","generation_mwh":100},
        {"plant_id":"1","generator_id":"B","reported_ba":"SRP","period":"2024-01","generation_mwh":-5}])
    review=pd.DataFrame([{"plant_id":"1","generator_id":"A","screening_candidate":True}])
    rows,summary,manifest=validate(observed,review)
    assert manifest["exact_generator_screened_rows"]==1
    assert manifest["excluded_or_unmatched_rows"]==1
    assert summary.observed_net_mwh.sum()==95
    assert not manifest["complete_ba_fleet_certified"]

def test_duplicate_inventory_fails():
    observed=pd.DataFrame([{"plant_id":"1","generator_id":"A","reported_ba":"SRP","period":"2024-01","generation_mwh":2}])
    review=pd.DataFrame([{"plant_id":"1","generator_id":"A","screening_candidate":True}]*2)
    with pytest.raises(ValueError,match="Duplicate"):
        validate(observed,review)


def test_excluded_observation_preserves_negative_mwh():
    observed=pd.DataFrame([
        {"plant_id":"1","generator_id":"A","reported_ba":"SRP","period":"2024-01","generation_mwh":120},
        {"plant_id":"1","generator_id":"B","reported_ba":"SRP","period":"2024-01","generation_mwh":-20}])
    review=pd.DataFrame([
        {"plant_id":"1","generator_id":"A","screening_candidate":True},
        {"plant_id":"1","generator_id":"B","screening_candidate":False}])
    rows,summary,manifest=validate(observed,review)
    assert manifest["exact_generator_screened_rows"]==1
    assert manifest["excluded_or_unmatched_rows"]==1
    assert summary.observed_net_mwh.sum()==100
    assert rows.loc[rows.generator_id.eq("B"),"identity_scope"].iloc[0]=="reviewed_but_excluded"

def test_null_generation_fails_closed():
    observed=pd.DataFrame([{"plant_id":"1","generator_id":"A","reported_ba":"SRP",
        "period":"2024-01","generation_mwh":None}])
    review=pd.DataFrame([{"plant_id":"1","generator_id":"A","screening_candidate":True}])
    with pytest.raises(ValueError,match="Invalid observed"):
        validate(observed,review)
