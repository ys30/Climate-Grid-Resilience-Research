import pandas as pd
import pytest
from grid_resilience.srp_ng_plant_nameplate_envelope import audit


def data():
    c=pd.DataFrame({
        "plant_id":["001","1","2"],"period":["2024-01"]*3,
        "reported_fuel":["NG"]*3,"page1_signed_net_mwh":[100.,50.,50.],
        "fuel_candidate_units":[2,2,1],
        "fuel_candidate_generator_ids":["A;B","A;B","C"]
    })
    g=pd.DataFrame({
        "plant_id":["1","1","2"],"generator_id":["A","B","C"],
        "nameplate_capacity_mw":[1.,2.,1.],
        "plant_reported_ba":["SRP"]*3
    })
    return c,g


def test_de_dup_generator_ceiling_and_monthly_conservation():
    c,g=data()
    rows,m=audit(c,g)
    assert m["plants"]==2 and m["page1_ng_rows"]==3
    assert m["total_signed_ng_mwh"]==200.
    plant=rows.loc[rows.plant_id.eq("1")].iloc[0]
    assert plant.distinct_candidate_generators==2
    assert plant.candidate_nameplate_mw==3.
    assert plant.nameplate_24h_ceiling_mwh==2232.
    assert plant.page1_signed_ng_mwh==150.
    assert m["plants_exceeding_theoretical_ceiling"]==0
    assert not m["historical_calibration_certified"]


def test_exceeds_ceiling_is_diagnostic_not_silent_clipping():
    c,g=data()
    c.loc[0,"page1_signed_net_mwh"]=3000.
    rows,m=audit(c,g)
    assert m["plants_exceeding_theoretical_ceiling"]==1
    assert rows.loc[rows.plant_id.eq("1"),"exceeds_theoretical_nameplate_ceiling"].iloc[0]


def test_unknown_generator_id_is_rejected():
    c,g=data()
    c.loc[0,"fuel_candidate_generator_ids"]="A;Z"
    with pytest.raises(ValueError,match="absent"):
        audit(c,g)


def test_mismatching_candidate_count_is_rejected():
    c,g=data()
    c.loc[0,"fuel_candidate_units"]=1
    with pytest.raises(ValueError,match="IDs/count"):
        audit(c,g)


def test_duplicate_roster_generator_is_rejected():
    c,g=data()
    with pytest.raises(ValueError,match="Duplicate"):
        audit(c,pd.concat([g,g.iloc[[0]]],ignore_index=True))


def test_leap_february_hours_are_calculated():
    c,g=data()
    c["period"]="2024-02"
    rows,m=audit(c,g,month=2)
    assert m["hours"]==696
    assert rows.loc[rows.plant_id.eq("1"),"nameplate_24h_ceiling_mwh"].iloc[0]==2088.
