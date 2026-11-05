import numpy as np
import pandas as pd
import pytest
from grid_resilience.srp_epa_june_july_2024_common_support import (
    june_join, july_join, common_support, june_demand)
from grid_resilience.srp_epa_2024_january_july_observed_seasonal import EXPECTED_UNITS


def sample(month_june_temp=32., month_july_temp=32., july_demand=5000.):
    u=pd.date_range("2024-06-01T07:00:00Z",periods=720,freq="h")
    v=pd.date_range("2024-07-01T07:00:00Z",periods=744,freq="h")
    june=[];july=[]
    for site, units in EXPECTED_UNITS.items():
        for unit in units:
            june.append(pd.DataFrame({
                "facility_id":site,"unit_id":unit,
                "local_date":(u-pd.Timedelta(hours=7)).strftime("%Y-%m-%d"),
                "local_hour":(u-pd.Timedelta(hours=7)).hour,
                "operating_time":1.,"gross_load_mw":100.}))
            july.append(pd.DataFrame({
                "facility_id":site,"unit_id":unit,
                "timestamp_utc":v,"temperature_2m_c":month_july_temp,
                "operating_time":1.,"gross_load_mw":101.,
                "era5_full_local_july_matched":True}))
    weather=pd.concat([pd.DataFrame({
        "plant_id":site,"technology":"gas",
        "timestamp_utc":pd.date_range("2024-06-01T00:00:00Z",periods=720,freq="h"),
        "temperature_2m_c":month_june_temp}) for site in EXPECTED_UNITS])
    demand=pd.DataFrame({
        "timestamp_utc":pd.date_range("2024-06-01T00:00:00Z",periods=720,freq="h"),
        "srp_ba_demand_mw":5000.})
    july_eia=pd.DataFrame({
        "UTC Time at End of Hour":pd.date_range(
             "2024-07-01T01:00:00Z",periods=744,freq="h").strftime("%m/%d/%Y %I:%M:%S %p"),
        "Balancing Authority":"SRP","Demand (MW)":july_demand})
    return pd.concat(june,ignore_index=True),weather,demand,pd.concat(july,ignore_index=True),july_eia


def audit(**kw):
    j,w,d,summer,summer_d=sample(**kw)
    return common_support(june_join(j,w,d),july_join(summer,summer_d))

def test_original_june_713_and_july_737_joint_source_hours():
    out,meta=audit()
    assert len(out)==10
    assert out.june_hours.eq(713).all() and out.july_hours.eq(737).all()
    assert out.covariate_screen_pass.all()
    assert out.operating_gross_screen_pass.all()
    assert not meta["generator_thermal_derating_or_eens_inferred"]

def test_temperature_nonoverlap_not_smoothed():
    out,_=audit(month_june_temp=12.,month_july_temp=38.)
    assert not out.continuous_temperature_ranges_overlap.any()
    assert out.shared_2c_500mw_4h_cells.eq(0).all()
    assert not out.covariate_screen_pass.any()

def test_demand_overlap_needed_too():
    out,_=audit(july_demand=9000.)
    assert out.continuous_temperature_ranges_overlap.all()
    assert not out.demand_ranges_overlap.any()
    assert not out.operating_gross_screen_pass.any()

def test_missing_june_matched_hour_fails():
    j,w,d,_,_=sample()
    j=j.drop(index=0)
    with pytest.raises(ValueError,match="720 local hours"):
        june_join(j,w,d)

def test_bad_era5_site_hours_fail():
    j,w,d,_,_=sample()
    w=w.iloc[:-1]
    with pytest.raises(ValueError,match="Incomplete observed June ERA5"):
        june_join(j,w,d)

def test_zero_operating_not_treated_as_gross_availability():
    j,w,d,summer,summer_d=sample()
    j["operating_time"]=0.
    result,_=common_support(june_join(j,w,d),july_join(summer,summer_d))
    assert result.covariate_screen_pass.all()
    assert not result.operating_gross_screen_pass.any()

def test_monthly_utc_end_hour_no_source_shift():
    _,_,_,summer,summer_d=sample()
    checked=july_join(summer,summer_d)
    assert len(checked)==7370
    assert checked.srp_ba_demand_mw.eq(5000).all()
