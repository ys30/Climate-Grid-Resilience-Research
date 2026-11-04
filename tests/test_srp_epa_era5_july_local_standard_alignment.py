import pandas as pd
import pytest
from grid_resilience.srp_epa_era5_july_local_standard_alignment import align


def inputs():
    local=pd.date_range("2024-07-01",periods=744,freq="h")
    epa=pd.concat([pd.DataFrame({
        "facility_id":site,"unit_id":unit,
        "date_local_standard":local.strftime("%Y-%m-%d"),
        "hour_local_standard":local.hour,
        "operating_time":1.,
        "gross_load_mw":75.,
        "heat_input_mmbtu":90.
    }) for site,unit in (("141","1"),("55129","DBG1"),("147","K-7"))],ignore_index=True)
    utc=pd.date_range("2024-07-01",periods=744,freq="h",tz="UTC")
    weather=pd.concat([pd.DataFrame({
        "plant_id":site,"technology":"gas",
        "timestamp_utc":utc,
        "temperature_2m_c":35.
    }) for site in ("141","55129","147")],ignore_index=True)
    return epa,weather


def test_az_mst_fixed_offset_and_737_hour_match():
    hourly,summary,m=align(*inputs())
    assert len(hourly)==3*744
    assert summary.epa_local_july_rows.eq(744).all()
    assert summary.matched_utc_july_weather_rows.eq(737).all()
    assert summary.matched_hours_with_positive_operating_fraction.eq(737).all()
    assert m["epa_hour_to_utc_hours_added"]==7
    assert not m["dst_applied"]
    a=hourly.loc[hourly.facility_id.eq("141")].sort_values("timestamp_utc")
    assert a.iloc[0].timestamp_utc==pd.Timestamp("2024-07-01T07:00Z")
    assert a.iloc[-1].timestamp_utc==pd.Timestamp("2024-08-01T06:00Z")
    assert a.era5_july_hour_matched.sum()==737


def test_no_silent_extra_august_era5_temperature():
    hourly,_,_=align(*inputs())
    miss=hourly.loc[~hourly.era5_july_hour_matched]
    assert len(miss)==3*7 and miss.temperature_2m_c.isna().all()


def test_reject_duplicate_epa_hour():
    a,b=inputs()
    with pytest.raises(ValueError,match="Duplicate EPA"):
        align(pd.concat([a,a.iloc[[0]]],ignore_index=True),b)


def test_reject_truncated_era5_weather():
    a,b=inputs()
    with pytest.raises(ValueError,match="Incomplete source UTC July"):
        align(a,b.iloc[:-1])


def test_reject_invalid_ambient_operating_fraction():
    a,b=inputs()
    a.loc[0,"operating_time"]=1.4
    with pytest.raises(ValueError,match="operating fraction"):
        align(a,b)


def test_fail_closed_when_epa_calendar_incomplete():
    a,b=inputs()
    with pytest.raises(ValueError,match="Incomplete EPA local July"):
        align(a.iloc[:-1],b)
