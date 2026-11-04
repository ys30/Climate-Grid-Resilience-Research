import pandas as pd
import pytest
from grid_resilience.srp_era5_wind_pypsa_matched import (
    validate_curve_hours,construct_cases,run
)


def inputs():
    t=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    b=pd.DataFrame({"timestamp":t,"demand_mw":8.,
                    "generation_mw":8.,"interchange_mw":0.})
    roster=pd.DataFrame({
        "plant_id":["1","2","3","4"],"generator_id":["G","C","N","W"],
        "plant_reported_ba":["SRP"]*4,
        "energy_source_1":["NG","SUB","NUC","WND"],
        "prime_mover":["GT","ST","ST","WT"],
        "nameplate_capacity_mw":[8.,2.,2.,1.]
    })
    c=pd.concat([
        pd.DataFrame({"timestamp_utc":t.strftime("%Y-%m-%dT%H:%M:%SZ"),
                      "curve_scenario":name,"fleet_uncalibrated_proxy_pu":value})
        for name,value in (("low_cut_in",.8),("reference",.5),("high_cut_in",.1))
    ],ignore_index=True)
    return b,roster,c


def test_only_wind_is_replaced_by_weather_proxy():
    b,r,c=inputs()
    _,_,cases,_=construct_cases(b,r,c)
    fixed=cases["fixed_wind_0p35"]
    for key,x in cases.items():
        nonwind=fixed.loc[fixed.technology.ne("wind"),"availability_pu"].reset_index(drop=True)
        other=x.loc[x.technology.ne("wind"),"availability_pu"].reset_index(drop=True)
        pd.testing.assert_series_equal(nonwind,other)
        assert len(x)==4*744
    assert cases["era5_reference"].loc[
        cases["era5_reference"].technology.eq("wind"),"availability_pu"].eq(.5).all()


def test_lost_weather_hour_is_rejected():
    b,r,c=inputs()
    with pytest.raises(ValueError,match="Missing or misaligned"):
        construct_cases(b,r,c.iloc[:-1])


def test_out_of_bounds_weather_proxy_rejected():
    _,_,c=inputs()
    c.loc[0,"fleet_uncalibrated_proxy_pu"]=1.2
    with pytest.raises(ValueError,match="range"):
        validate_curve_hours(c)


def test_bad_stress_factor_rejected():
    b,r,c=inputs()
    with pytest.raises(ValueError,match="multiplier"):
        construct_cases(b,r,c,gas=1.1)


def test_four_actual_solver_scenarios_are_matched(tmp_path):
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    b,r,c=inputs()
    x,m=run(b,r,c,tmp_path)
    assert len(x)==4
    assert set(x.scenario)=={"fixed_wind_0p35","era5_low_cut_in",
                             "era5_reference","era5_high_cut_in"}
    assert x.positive_gap_hours.between(0,744).all()
    assert not m["weather_climate_causal_effect_identified"]
    assert not m["historical_reliability_calibrated"]
