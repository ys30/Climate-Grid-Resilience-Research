import pandas as pd
import pytest
from grid_resilience.srp_fuel_gap_plant_attribution import attribute


def sources():
    p=pd.DataFrame({"plant_id":["0001","1","2","3","3"],
                    "reported_ba":["SRP"]*5,
                    "period":["2024-01"]*5,
                    "prime_mover":["CT","GT","ST","ST","ST"],
                    "reported_fuel":["NG","NG","NG","SUB","DFO"],
                    "net_generation_mwh":[10.,20.,0.,40.,2.]})
    f=pd.DataFrame({"eia930_fuel":["Natural Gas","Coal"],
                    "reported_hours":[744,744],"blank_hours":[0,0],
                    "signed_reported_mwh":[25.,45.]})
    return p,f


def test_plant_counts_and_signed_differences():
    p,f=sources()
    plants,d,summary=attribute(p,f)
    assert summary["ng_distinct_plants"]==2
    assert summary["sub_distinct_plants"]==1
    assert d.loc[d.eia923_original_fuel_code.eq("NG"),"numeric_source_difference_mwh"].iloc[0]==5.
    assert d.loc[d.eia923_original_fuel_code.eq("SUB"),"numeric_source_difference_mwh"].iloc[0]==-5.
    assert plants.loc[plants.plant_id.eq("1")&plants.reported_fuel.eq("NG"),"page1_source_rows"].iloc[0]==2
    assert not summary["eia930_plant_allocation_certified"]


def test_missing_fuel_category_is_not_zero_or_a_comparison():
    p,f=sources()
    f.loc[0,"reported_hours"]=0
    f.loc[0,"blank_hours"]=744
    f.loc[0,"signed_reported_mwh"]=float("nan")
    _,d,_=attribute(p,f)
    row=d.loc[d.eia923_original_fuel_code.eq("NG")].iloc[0]
    assert pd.isna(row.numeric_source_difference_mwh)
    assert not row.numerically_comparable_coverage


def test_duplicate_eia930_heading_rejected():
    p,f=sources()
    with pytest.raises(ValueError,match="Duplicate"):
        attribute(p,pd.concat([f,f.iloc[[0]]],ignore_index=True))


def test_bad_monthly_source_values_rejected():
    p,f=sources()
    p.loc[0,"net_generation_mwh"]=float("inf")
    with pytest.raises(ValueError,match="nonfinite"):
        attribute(p,f)
