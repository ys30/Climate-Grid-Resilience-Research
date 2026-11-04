import pandas as pd
import pytest
from grid_resilience.srp_thermal_coincident_site_heat import analyze


def source():
    t=pd.date_range("2024-07-01",periods=744,freq="h",tz="UTC")
    rows=[]
    for tech,plant,mw in (("gas","1",75.),("gas","2",25.),("coal","3",50.)):
        temps=[20.]*744
        if plant=="1":temps[10:19]=[41.]*9
        if plant=="2":temps[10:13]=[42.]*3
        if tech=="coal":temps[10:14]=[36.]*4
        rows.append(pd.DataFrame({"timestamp_utc":t,"technology":tech,
            "plant_id":plant,"selected_nameplate_mw":mw,
            "temperature_2m_c":temps}))
    return pd.concat(rows,ignore_index=True)


def test_concurrent_capacity_exposure_and_episode_durations():
    h,e,s,m=analyze(source())
    gas=s[(s.technology=="gas") & (s.temperature_threshold_c==40.)]
    half=gas.loc[gas.coincident_source_capacity_share_threshold==.5].iloc[0]
    three_quarters=gas.loc[gas.coincident_source_capacity_share_threshold==.75].iloc[0]
    assert half.hours==9 and half.longest_episode_hours==9
    assert three_quarters.hours==9
    assert half.site_temperature_exposed_nameplate_mwh==75*9+25*3
    assert m["technology_source_nameplate_mw"]["gas"]==100.
    assert not m["actual_outage_or_eens_inferred"]
    assert len(h)==744*2*2
    assert e.duration_hours.sum()>0


def test_missing_or_duplicate_site_hour_fails():
    x=source()
    with pytest.raises(ValueError,match="Missing hours"):
        analyze(x.iloc[:-1])
    with pytest.raises(ValueError,match="Duplicate"):
        analyze(pd.concat([x,x.iloc[[0]]],ignore_index=True))


def test_bad_site_weather_or_month_fails():
    x=source()
    x.loc[0,"temperature_2m_c"]=float("nan")
    with pytest.raises(ValueError,match="Invalid source numeric"):
        analyze(x)
    x=source()
    x.loc[0,"timestamp_utc"]="2024-08-01T00:00:00Z"
    with pytest.raises(ValueError,match="one complete source month"):
        analyze(x)


def test_only_zero_weather_exposure_returns_empty_episode_table():
    x=source()
    x["temperature_2m_c"]=5.
    h,e,s,m=analyze(x)
    assert e.empty and s.hours.eq(0).all()
