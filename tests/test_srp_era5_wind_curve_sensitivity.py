import pandas as pd
import pytest
from grid_resilience.srp_era5_wind_curve_sensitivity import analyze


def weather():
    times=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    return pd.concat([
        pd.DataFrame({
            "timestamp_utc":times.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "plant_id":plant,"wind_speed_100m_ms":speed,
            "site_nameplate_mw":nameplate,"capacity_weight":weight,
        })
        for plant,speed,nameplate,weight in
        (("A",4.,100.,.25),("B",13.,300.,.75))
    ],ignore_index=True)


def test_reanalysis_site_curve_before_spatial_weighting():
    _,hourly,stats,m=analyze(weather())
    ref=hourly.loc[hourly.curve_scenario.eq("reference")]
    # Reference curve: B rated, A fractional, not power_curve(weighted avg wind).
    value=(4**3-3**3)/(12**3-3**3)*.25+.75
    assert abs(ref.fleet_uncalibrated_proxy_pu.mean()-value)<1e-10
    assert len(ref)==744
    assert len(stats)==3
    assert m["source_eligible_wind_nameplate_mw"]==400.
    assert not m["wind_fleet_production_calibrated"]


def test_missing_hour_rejected():
    with pytest.raises(ValueError,match="grid"):
        analyze(weather().iloc[:-1])


def test_duplicate_plant_hour_rejected():
    x=weather()
    with pytest.raises(ValueError,match="grid"):
        analyze(pd.concat([x,x.iloc[[0]]],ignore_index=True))


def test_inconsistent_weights_rejected():
    x=weather()
    x.loc[x.plant_id.eq("A"),"capacity_weight"]=.3
    with pytest.raises(ValueError,match="weights"):
        analyze(x)


def test_misaligned_hour_rejected():
    x=weather()
    x.loc[0,"timestamp_utc"]="2024-02-01T00:00:00Z"
    with pytest.raises(ValueError,match="coverage"):
        analyze(x)


def test_bad_curve_rejected():
    with pytest.raises(ValueError,match="curve"):
        analyze(weather(),curves={"bad":(12,3,25)})
