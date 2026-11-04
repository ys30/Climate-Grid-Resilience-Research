import pandas as pd
import pytest
from grid_resilience.srp_thermal_weather_monthly_generation_scope import analyze


def inputs():
    sites=pd.DataFrame({"plant_id":["1","2","3"],"technology":["gas","gas","coal"],
        "nameplate_mw":[100.,50.,40.]})
    page4=pd.DataFrame({
        "plant_id":["1","1","3","1","1","3"],
        "generator_id":["A","B","C","A","B","C"],
        "reported_ba":["SRP"]*6,
        "period":["2024-01"]*3+["2024-07"]*3,
        "generation_mwh":[120.,-5.,10.,300.,-7.,20.]})
    t=pd.date_range("2024-07-01",periods=744,freq="h",tz="UTC")
    weather=pd.concat([pd.DataFrame({
        "timestamp_utc":t,"plant_id":pid,"technology":tech,"temperature_2m_c":temp})
        for pid,tech,temp in (("1","gas",42.),("2","gas",40.),("3","coal",25.))],
        ignore_index=True)
    return sites,page4,weather


def test_monthly_reporting_gap_preserved_not_outage():
    rows,s,m=analyze(*inputs())
    assert len(rows)==6
    assert rows.page4_month_reported.sum()==4
    missing=rows.loc[rows.plant_id.eq("2")]
    assert missing.page4_month_signed_net_mwh.isna().all()
    assert missing.descriptive_net_output_over_nameplate_hours.isna().all()
    jan=s[(s.period=="2024-01")&(s.technology=="gas")].iloc[0]
    assert jan.page4_reported_plant_count==1
    assert jan.page4_absent_plant_count==1
    assert jan.page4_reported_signed_net_mwh==115.
    assert jan.page4_nameplate_coverage_fraction==2/3
    assert not m["monthly_reporting_completeness_certified"]
    assert not m["monthly_data_can_estimate_hourly_temperature_derating"]


def test_duplicate_generator_month_fails():
    s,p,w=inputs()
    with pytest.raises(ValueError,match="Duplicate"):
        analyze(s,pd.concat([p,p.iloc[[0]]],ignore_index=True),w)


def test_bad_or_missing_site_hour_fails():
    s,p,w=inputs()
    with pytest.raises(ValueError,match="Missing/shifted"):
        analyze(s,p,w.iloc[:-1])


def test_signed_net_generation_is_not_clipped():
    s,p,w=inputs()
    p.loc[(p.generator_id=="B")&(p.period=="2024-01"),"generation_mwh"]=-1000.
    rows,_,_=analyze(s,p,w)
    value=rows[(rows.plant_id=="1")&(rows.period=="2024-01")].iloc[0]
    assert value.page4_month_signed_net_mwh==-880.


def test_all_plant_months_reported_can_pass_completeness_gate():
    s,p,w=inputs()
    more=pd.DataFrame({"plant_id":["2","2"],"generator_id":["D","D"],
        "reported_ba":["SRP","SRP"],"period":["2024-01","2024-07"],
        "generation_mwh":[0.,10.]})
    _,summary,m=analyze(s,pd.concat([p,more],ignore_index=True),w)
    assert summary.month_is_complete_for_annual_plant_cohort.all()
    assert m["monthly_reporting_completeness_certified"]
    assert not m["historical_reliability_calibrated"]
