import pandas as pd
import pytest
from grid_resilience.eia923_shared_plant_difference import differences


def inputs():
    page1=pd.DataFrame({
        "plant_id":["0001","1","2","3"],"reported_ba":["SRP"]*4,
        "period":["2024-01"]*4,"prime_mover":["ST","ST","PV","GT"],
        "reported_fuel":["NUC","NUC","SUN","NG"],
        "net_generation_mwh":[7.,9.,-2.,4.]
    })
    page4=pd.DataFrame({
        "plant_id":["1","0004"],"generator_id":["001","5"],
        "reported_ba":["SRP"]*2,"period":["2024-01"]*2,
        "generation_mwh":[15.,3.]
    })
    return page1,page4


def test_preserves_repeated_page1_rows_and_source_scopes():
    rows,fuel,m=differences(*inputs())
    assert m["shared_plant_count"]==1
    assert m["page1_only_plant_count"]==2
    assert m["page4_only_plant_count"]==1
    assert m["shared_net_difference_mwh"]==1.
    assert m["shared_absolute_difference_mwh"]==1.
    assert m["page1_total_mwh"]==18.
    assert m["page4_total_mwh"]==18.
    assert len(fuel)==2
    assert rows.loc[rows.plant_id.eq("1"),"page1_rows"].iloc[0]==2
    assert not m["add_source_totals_permitted"]
    assert not m["historical_calibration_certified"]


def test_duplicate_page4_is_rejected():
    a,b=inputs()
    b=pd.concat([b,b.iloc[[0]]],ignore_index=True)
    with pytest.raises(ValueError,match="Duplicate Page 4"):
        differences(a,b)


def test_invalid_reported_mwh_fails():
    a,b=inputs()
    a.loc[0,"net_generation_mwh"]=float("inf")
    with pytest.raises(ValueError,match="nonfinite"):
        differences(a,b)


def test_empty_selected_month_rejected():
    a,b=inputs()
    with pytest.raises(ValueError,match="No matching"):
        differences(a,b,period="2024-02")
