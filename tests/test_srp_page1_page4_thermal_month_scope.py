import pandas as pd
import pytest
from grid_resilience.srp_page1_page4_thermal_month_scope import reconcile


def sources():
    sites=pd.DataFrame({"plant_id":["001","2","3"],"technology":["gas","coal","gas"],
        "nameplate_mw":[100.,80.,40.]})
    a=pd.DataFrame({
        "plant_id":["1","1","1","2","1","2"],
        "reported_ba":["SRP"]*6,
        "period":["2024-01"]*4+["2024-07"]*2,
        "prime_mover":["GT","GT","ST","ST","GT","ST"],
        "reported_fuel":["NG","NG","SUB","SUB","NG","SUB"],
        "net_generation_mwh":[40.,-5.,999.,20.,80.,30.]})
    b=pd.DataFrame({
        "plant_id":["1","1","2","1","2"],"generator_id":["A","B","C","A","C"],
        "reported_ba":["SRP"]*5,
        "period":["2024-01"]*3+["2024-07"]*2,
        "generation_mwh":[15.,20.,30.,70.,25.]})
    return a,b,sites


def test_preserve_signed_values_and_different_fuel_rows_excluded():
    rows,stat,m=reconcile(*sources())
    jan=rows.loc[rows.period.eq("2024-01")&rows.plant_id.eq("1")].iloc[0]
    assert jan.page1_eligible_signed_net_mwh==35.
    assert jan.page4_signed_net_mwh==35.
    assert jan.source_difference_p1_minus_p4_mwh==0.
    assert m["page1_plus_page4_is_double_counted_generation"]
    assert not m["monthly_reconciliation_can_calibrate_hourly_heat_derating"]
    gas=stat.loc[stat.period.eq("2024-01")&stat.technology.eq("gas")].iloc[0]
    assert gas.annual_eia860_plant_count==2
    assert gas.neither_source_plants==1
    assert gas.both_sources_reported_plants==1
    assert gas.both_sources_nameplate_mw==100.


def test_page1_repeated_coarse_keys_legitimately_summed():
    a,b,s=sources()
    assert a.iloc[0].plant_id==a.iloc[1].plant_id
    rows,_,_=reconcile(a,b,s)
    assert rows.loc[rows.period.eq("2024-01")&rows.plant_id.eq("1"),
                    "page1_source_fuel_mover_rows"].iloc[0]==2


def test_missing_page4_does_not_mean_zero():
    a,b,s=sources()
    b=b.loc[~b.plant_id.eq("2")]
    rows,_,_=reconcile(a,b,s)
    v=rows.loc[rows.period.eq("2024-07")&rows.plant_id.eq("2")].iloc[0]
    assert pd.isna(v.page4_signed_net_mwh)
    assert pd.isna(v.source_difference_p1_minus_p4_mwh)
    assert not v.both_sources_report


def test_duplicate_page4_generator_month_rejected():
    a,b,s=sources()
    with pytest.raises(ValueError,match="Duplicate"):
        reconcile(a,pd.concat([b,b.iloc[[0]]],ignore_index=True),s)


def test_bad_source_values_rejected():
    a,b,s=sources()
    a.loc[0,"net_generation_mwh"]=float("nan")
    with pytest.raises(ValueError,match="nonfinite"):
        reconcile(a,b,s)
