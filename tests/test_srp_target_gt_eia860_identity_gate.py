import pandas as pd
import pytest
from grid_resilience.srp_target_gt_eia860_identity_gate import gate

def inputs():
    annual=pd.DataFrame([
        {"plant_id":plant,"generator_id":gid,"prime_mover":pm,
         "energy_source_1":"NG","nameplate_capacity_mw":mw}
        for plant in ("141","55129","147")
        for gid,pm,mw in (("GT1","GT",20.),("ST1","ST",100.))])
    p1=pd.DataFrame([
        {"plant_id":plant,"period":period,"prime_mover":pm,"fuel":"NG",
         "reported_signed_net_mwh":mwh,"source_value_reported":True}
        for plant in ("141","55129","147") for period in ("2024-01","2024-07")
        for pm,mwh in (("GT",22.),("ST",110.))])
    p4=pd.DataFrame([
        {"plant_id":plant,"period":period,"generator_id":"ST1","prime_mover":"ST",
         "reported_signed_net_mwh":110.,"source_value_reported":True}
        for plant in ("141","55129","147") for period in ("2024-01","2024-07")])
    return annual,p1,p4

def test_annual_gt_candidate_is_not_a_measured_unit_allocation():
    table,joined,manifest=gate(*inputs())
    assert len(table)==6
    assert table.annual_gt_generator_count.eq(1).all()
    assert table.annual_gt_nameplate_mw.eq(20.).all()
    assert table.page4_exact_annual_id_matches.eq(1).all()
    assert table.page4_mover_matches_where_exact_id.eq(1).all()
    assert table.gt_reporting_grain_difference_mwh.eq(22.).all()
    assert table.non_gt_residual_mwh.eq(0.).all()
    assert table.page1_gt_to_unit_allocation_certified.eq(False).all()
    assert not manifest["heat_related_derating_calibrated"]

def test_no_gt_annual_identity_does_not_force_an_assignment():
    a,b,c=inputs()
    a=a.loc[a.prime_mover.ne("GT")]
    x,_,_=gate(a,b,c)
    assert x.annual_gt_generator_count.eq(0).all()
    assert x.possible_gt_population_present.eq(False).all()
    assert x.gt_reporting_grain_difference_mwh.eq(22.).all()

def test_missing_source_target_fails():
    a,b,c=inputs()
    a=a.loc[a.plant_id.ne("141")]
    with pytest.raises(ValueError,match="Missing annual"):
        gate(a,b,c)

def test_duplicate_annual_generator_id_fails():
    a,b,c=inputs()
    with pytest.raises(ValueError,match="Duplicate EIA860"):
        gate(pd.concat([a,a.iloc[[0]]]),b,c)

def test_unreported_nonnull_is_not_zero():
    a,b,c=inputs()
    c.loc[0,"source_value_reported"]=False
    with pytest.raises(ValueError,match="not zero"):
        gate(a,b,c)

def test_page4_wrong_unit_id_remains_unmatched():
    a,b,c=inputs()
    c.loc[0,"generator_id"]="NOT_ON_860"
    table,joined,_=gate(a,b,c)
    assert not joined.loc[joined.generator_id.eq("NOT_ON_860"),
                          "exact_annual_generator_id_match"].any()
    assert table.page4_exact_annual_id_matches.min()==0
