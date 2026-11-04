import pandas as pd
import pytest
from grid_resilience.srp_gt_epa_camd_crosswalk_gate import analyze


def examples():
    inventory=pd.DataFrame([
        {"plant_id":pid,"generator_id":"GT1","prime_mover":"GT",
         "energy_source_1":"NG","nameplate_capacity_mw":50.}
        for pid in ("141","55129","147")])
    cw=pd.DataFrame([
        {"CAMD_PLANT_ID":pid,"CAMD_UNIT_ID":"U1","CAMD_GENERATOR_ID":"GT1",
         "EIA_PLANT_ID":pid,"EIA_GENERATOR_ID":"GT1","MATCH_TYPE_GEN":"Exact",
         "MATCH_TYPE_BOILER":"","EIA_UNIT_TYPE":"GT"}
        for pid in ("141","55129","147")])
    return inventory,cw


def test_camd_mapping_is_not_operational_output_certification():
    inventory,cw=examples()
    t,s,rel,m=analyze(inventory,cw)
    assert len(t)==3 and s.candidates_with_epa_unit_relationship.eq(1).all()
    assert t.epa_mapping_one_to_one_proven.eq(False).all()
    assert not m["hourly_operational_data_downloaded"]
    assert not m["temperature_derating_calibrated"]


def test_many_to_many_relationships_preserved():
    inventory,cw=examples()
    extra=cw.iloc[[0]].copy()
    extra["CAMD_UNIT_ID"]="U2"
    t,s,_,_=analyze(inventory,pd.concat([cw,extra],ignore_index=True))
    one=t.loc[t.plant_id.eq("141")].iloc[0]
    assert one.epa_camd_unit_relationship_count==2
    assert one.epa_camd_unit_ids=="141/U1;141/U2"
    assert s.loc[s.plant_id.eq("141"),"annual_gt_ids_with_multiple_camd_units"].iloc[0]==1


def test_missing_crosswalk_row_is_not_an_outage():
    inv,cw=examples()
    cw=cw.loc[cw.EIA_PLANT_ID.ne("147")]
    t,s,_,m=analyze(inv,cw)
    assert not t.loc[t.plant_id.eq("147"),"epa_mapping_exists"].iloc[0]
    assert m["unmapped_eia_gt_generator_is_not_outage_or_nonreporting_evidence"]


def test_duplicate_annual_generator_ids_rejected():
    a,b=examples()
    with pytest.raises(ValueError,match="Duplicate"):
        analyze(pd.concat([a,a.iloc[[0]]],ignore_index=True),b)


def test_missing_required_crosswalk_identity_rejected():
    a,b=examples()
    with pytest.raises(ValueError,match="Missing EPA-EIA"):
        analyze(a,b.drop(columns=["MATCH_TYPE_BOILER"]))
