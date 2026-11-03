"""EIA fuel-scope tests with intentionally missing hourly fuel observations."""
import pandas as pd
import pytest

from grid_resilience.eia930_fuel_decomposition import FUELS
from grid_resilience.srp_eia923_eia930_fuel_scope import audit


def sources():
    p1=pd.DataFrame({"plant_id":["0001","1","2"],
                     "reported_ba":["SRP"]*3,"period":["2024-01"]*3,
                     "prime_mover":["ST","ST","GT"],
                     "reported_fuel":["NUC","NUC","NG"],
                     "net_generation_mwh":[30.,40.,-2.]})
    b=pd.DataFrame({"Balancing Authority":["SRP"]*2,
                    "UTC Time at End of Hour":["01/01/2024 01:00:00 AM","01/01/2024 02:00:00 AM"],
                    "Net Generation (MW)":[30.,40.]})
    for fuel in FUELS:
        b["Net Generation (MW) from "+fuel]=["",""]
    b["Net Generation (MW) from Nuclear"]=[30.,40.]
    return p1,b


def test_blank_is_not_zero_and_coarse_page1_keys_are_preserved():
    p1,b=sources()
    d,f,m=audit(p1,b,expected_hours=2)
    assert m["eia923_page1_reported_generation_mwh"]==68.
    assert m["eia930_total_reported_generation_mwh"]==70.
    assert m["page1_minus_eia930_source_scope_difference_mwh"]==-2.
    assert not m["eia930_all_fuels_hourly_complete"]
    assert m["eia930_complete_fuel_sum_mwh"] is None
    assert not m["historical_calibration_certified"]
    nuclear=d.loc[d.eia930_fuel.eq("Nuclear")].iloc[0]
    coal=d.loc[d.eia930_fuel.eq("Coal")].iloc[0]
    assert nuclear.reported_hours==2 and nuclear.signed_reported_mwh==70.
    assert coal.blank_hours==2 and pd.isna(coal.signed_reported_mwh)
    assert f.loc[f.reported_fuel.eq("NUC"),"source_rows"].iloc[0]==2


def test_complete_fuel_total_comparable_within_eia930_only():
    p1,b=sources()
    for fuel in FUELS:
        b["Net Generation (MW) from "+fuel]=[0.,0.]
    b["Net Generation (MW) from Nuclear"]=[30.,40.]
    d,_,m=audit(p1,b,expected_hours=2)
    assert m["eia930_all_fuels_hourly_complete"]
    assert m["eia930_complete_fuel_sum_mwh"]==70.
    assert m["eia930_total_minus_complete_fuel_sum_mwh"]==0.
    assert not m["category_crosswalk_certified"]


def test_missing_or_duplicate_ba_hours_fail():
    p1,b=sources()
    with pytest.raises(ValueError,match="Incomplete"):
        audit(p1,b.iloc[:1],expected_hours=2)
    with pytest.raises(ValueError,match="duplicate"):
        audit(p1,pd.concat([b.iloc[:1],b.iloc[:1]],ignore_index=True),expected_hours=2)


def test_nonfinite_page1_and_eia930_fail():
    p1,b=sources()
    p1.loc[0,"net_generation_mwh"]=float("inf")
    with pytest.raises(ValueError,match="Nonfinite"):
        audit(p1,b,expected_hours=2)
    p1,b=sources()
    b.loc[0,"Net Generation (MW) from Nuclear"]=float("inf")
    with pytest.raises(ValueError,match="Invalid"):
        audit(p1,b,expected_hours=2)


def test_no_fuel_imputation_on_partially_missing_group():
    p1,b=sources()
    b["Net Generation (MW) from Nuclear"]=[30.,""]
    d,_,m=audit(p1,b,expected_hours=2)
    nuclear=d.loc[d.eia930_fuel.eq("Nuclear")].iloc[0]
    assert nuclear.reported_hours==1
    assert nuclear.blank_hours==1
    assert nuclear.signed_reported_mwh==30.
    assert not m["eia930_all_fuels_hourly_complete"]
