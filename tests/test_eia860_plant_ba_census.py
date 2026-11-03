"""Plant-based BA assignment must reveal units absent from Page4 monthly scope."""
import pandas as pd
import pytest
from grid_resilience.eia860_plant_ba_census import census

def samples():
    plants=pd.DataFrame({"plant_id":["001","2","3"],"plant_reported_ba":["SRP","SRP","OTHER"]})
    operable=pd.DataFrame({"plant_id":["1","2","3"],"generator_id":["A","B","C"],
        "nameplate_capacity_mw":[100.,30.,50.]})
    page4=pd.DataFrame({"plant_id":["1"],"generator_id":["A"],
        "reported_ba":["SRP"],"period":["2024-01"]})
    return plants,operable,page4

def test_missing_monthly_page4_units_visible_without_zero_imputation():
    d,m=census(*samples())
    assert len(d)==2
    assert m["eia860_plant_assigned_operable_generators"]==2
    assert m["eia860_plant_assigned_nameplate_mw"]==130
    assert m["of_those_appearing_in_eia923_page4_ba_month"]==1
    assert m["plant_assigned_operable_not_in_page4_month"]==1
    assert m["plant_assigned_nameplate_not_in_page4_month_mw"]==30
    assert m["historical_calibration_certified"] is False

def test_duplicate_plants_fail():
    a,b,c=samples()
    with pytest.raises(ValueError,match="Duplicate EIA-860 plant"):
        census(pd.concat([a,a.iloc[:1]]),b,c)

def test_unrelated_missing_plant_is_reported_but_does_not_block_target_ba():
    a,b,c=samples()
    rows,manifest=census(a.iloc[:2],b,c)
    assert len(rows)==2
    assert manifest["nationwide_operable_records_without_plant_join"]==1

def test_invalid_unrelated_capacity_is_not_used_for_target_ba():
    a,b,c=samples()
    b.loc[2,"nameplate_capacity_mw"]="not-reported"
    rows,manifest=census(a,b,c)
    assert manifest["eia860_plant_assigned_nameplate_mw"]==130.

def test_invalid_target_ba_capacity_fails_closed():
    a,b,c=samples()
    b.loc[1,"nameplate_capacity_mw"]="not-reported"
    with pytest.raises(ValueError,match="target BA generator nameplate"):
        census(a,b,c)

def test_no_target_ba_plant_is_rejected():
    a,b,c=samples()
    a["plant_reported_ba"]="OTHER"
    with pytest.raises(ValueError,match="No EIA-860 operable"):
        census(a,b,c)

def test_duplicate_page4_id_fails():
    a,b,c=samples()
    with pytest.raises(ValueError,match="Duplicate EIA-923"):
        census(a,b,pd.concat([c,c]))
