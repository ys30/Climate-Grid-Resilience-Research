import pandas as pd
import pytest
from grid_resilience.srp_epa_camd_eia_2024_operation_bridge import join_units

def inputs():
    ops=pd.DataFrame([
        {"oris":site,"epa_unit_id":unit,"source_calendar_hour_rows":8784,
         "positive_operating_time_rows":100,"reported_operating_hours_sum":90.,
         "positive_gross_load_rows":80}
        for site,unit in (("141","1"),("141","8"),("55129","DBG1"),("147","K-7"))])
    static=pd.DataFrame([
        {"CAMD_PLANT_ID":site,"CAMD_UNIT_ID":unit,"EIA_PLANT_ID":site,
         "EIA_GENERATOR_ID":eid,"EIA_UNIT_TYPE":pm,"MATCH_TYPE_GEN":"Exact"}
        for site,unit,eid,pm in (
            ("141","1","AF1","ST"),("55129","DBG1","CTG1","CT"),
            ("147","K-7","KY7","CT"),("147","K-7","KY7A","CA"))])
    return ops,static

def test_preserves_unmatched_and_one_to_many_source_unit_relationships():
    result,coverage,raw,meta=join_units(*inputs())
    assert len(result)==4
    assert len(raw)==5
    assert int(coverage.units_with_static_crosswalk.sum())==3
    assert int(coverage.units_without_static_crosswalk.sum())==1
    assert not coverage.units_with_direct_gt_class_link.any()
    assert result.loc[result.epa_unit_id.eq("K-7"),
                      "direct_static_crosswalk_relationship_count"].iloc[0]==2
    assert result.loc[result.epa_unit_id.eq("8"),
                      "linked_eia_generator_ids"].iloc[0]==""
    assert not meta["actual_temperature_derating_calibrated"]

def test_wrong_eia_plant_identity_fails_closed():
    a,b=inputs()
    b.loc[0,"EIA_PLANT_ID"]="999"
    with pytest.raises(ValueError,match="plant IDs differ"):
        join_units(a,b)

def test_duplicate_observed_unit_fails():
    a,b=inputs()
    with pytest.raises(ValueError,match="Duplicate observed"):
        join_units(pd.concat([a,a.iloc[[0]]],ignore_index=True),b)

def test_incomplete_2024_calendar_source_fails():
    a,b=inputs()
    a.loc[0,"source_calendar_hour_rows"]=8783
    with pytest.raises(ValueError,match="Incomplete source-calendar"):
        join_units(a,b)

def test_no_automated_unit_power_allocation():
    a,b=inputs()
    b.loc[0,"EIA_UNIT_TYPE"]="GT"
    result,summary,_,meta=join_units(a,b)
    assert result.loc[result.epa_unit_id.eq("1"),
                      "eia860_gt_generator_directly_linked"].iloc[0]
    assert not meta["eia_gt_generator_net_mw_inferred"]
