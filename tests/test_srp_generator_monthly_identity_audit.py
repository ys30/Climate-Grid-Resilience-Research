import pandas as pd
import pytest
from grid_resilience.srp_generator_monthly_identity_audit import audit

def inputs():
    review=pd.DataFrame({"plant_id":[1,1,2],"generator_id":["A","B","C"],
      "nameplate_capacity_mw":[100.,40.,20.],
      "energy_source_1":["NG","NG","NG"],
      "screening_candidate":[True,True,False]})
    rows=pd.DataFrame({"plant_id":[1,1,2],"generator_id":["A","B","C"],
      "generation_mwh":[500.,0.,0.],
      "identity_scope":["exact_screened_generator","exact_screened_generator","reviewed_but_excluded"]})
    return review,rows

def test_monthly_identity_audit():
    a,b=inputs()
    r=audit(a,b)
    assert r["matched_generator_identities"]==3
    assert r["screened_zero_observed_monthly_net_generation"]==1
    assert r["excluded_zero_observed_monthly_net_generation"]==1
    assert r["screened_observed_page4_monthly_net_mwh"]==500
    assert r["excluded_nameplate_mw"]==20
    assert r["observed_zero_screened_nameplate_mw"]==40
    assert r["observed_zero_screened_plant_count"]==1
    assert len(r["source_scope_by_fuel"])==2
    assert r["historical_calibration_certified"] is False

@pytest.mark.parametrize("mode",["missing","duplicate","scope","nonfinite"])
def test_fail_closed(mode):
    a,b=inputs()
    if mode=="missing":b=b.iloc[:-1]
    elif mode=="duplicate":b.loc[1,"generator_id"]="A"
    elif mode=="scope":b.loc[2,"identity_scope"]="exact_screened_generator"
    elif mode=="nonfinite":b.loc[0,"generation_mwh"]=float("inf")
    with pytest.raises(ValueError):audit(a,b)
