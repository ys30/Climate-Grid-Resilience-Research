import pandas as pd
import pytest
from grid_resilience.srp_page1_eia860_fuel_crosswalk import audit


def data():
    p=pd.DataFrame({
        "plant_id":["0001","1","2","3"],"reported_ba":["SRP"]*4,
        "period":["2024-01"]*4,"prime_mover":["ST","ST","GT","PV"],
        "reported_fuel":["NUC","NUC","DFO","SUN"],
        "net_generation_mwh":[10.,20.,-1.,4.]
    })
    g=pd.DataFrame({
        "plant_id":["1","0002","2"],"generator_id":["001","A","B"],
        "prime_mover":["ST","GT","GT"],
        "energy_source_1":["NUC","NG","NG"],
        "energy_source_2":["","DFO",""],
        "plant_reported_ba":["SRP"]*3,
        "nameplate_capacity_mw":[50.,30.,5.]
    })
    return p,g


def test_preserve_source_rows_and_candidate_not_generator_assignment():
    rows,classes,m=audit(*data())
    assert len(rows)==4
    assert m["page1_source_rows"]==4
    assert m["page1_distinct_plants"]==3
    assert m["plant_mover_fuel_candidate_rows"]==3
    assert m["plant_absent_source_rows"]==1
    assert m["source_total_signed_net_mwh"]==33.
    assert not m["unique_generator_assignment_certified"]
    assert not m["historical_calibration_certified"]
    assert rows.loc[rows.plant_id.eq("2"),"fuel_candidate_generator_ids"].iloc[0]=="A"
    assert classes.source_rows.sum()==4


def test_unmatched_secondary_fuel_remains_visible():
    p,g=data()
    g.loc[g.generator_id.eq("A"),"energy_source_2"]=""
    rows,_,m=audit(p,g)
    assert m["fuel_code_unmatched_rows"]==1
    assert rows.loc[rows.plant_id.eq("2"),"candidate_status"].iloc[0]=="plant_mover_present_fuel_code_unmatched"


def test_duplicate_operable_generator_fails():
    p,g=data()
    with pytest.raises(ValueError,match="Duplicate EIA860"):
        audit(p,pd.concat([g,g.iloc[[0]]],ignore_index=True))


def test_nonfinite_page1_net_mwh_fails():
    p,g=data()
    p.loc[0,"net_generation_mwh"]=float("inf")
    with pytest.raises(ValueError,match="nonfinite"):
        audit(p,g)


def test_missing_plant_id_fails_closed():
    p,g=data()
    p.loc[0,"plant_id"]=""
    with pytest.raises(ValueError,match="Missing source"):
        audit(p,g)
