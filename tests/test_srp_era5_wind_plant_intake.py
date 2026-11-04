import json
import pandas as pd
import pytest

from grid_resilience.srp_era5_wind_plant_intake import (
    parse_response, validate_sites, run
)


def sites():
    return pd.DataFrame({
        "ba":["SRP","SRP","BPAT"],
        "plant_id":["100","200","300"],
        "latitude":[34.,35.,45.],
        "longitude":[-112.,-111.,-120.],
        "nameplate_mw":[100.,50.,300.],
    })


def response(year=2024,month=1):
    n=pd.Period(f"{year}-{month:02d}").days_in_month*24
    ts=pd.date_range(f"{year}-{month:02d}-01",periods=n,freq="h",tz="UTC")
    return json.dumps({
        "latitude":34.,"longitude":-112.,"elevation":1000.,
        "utc_offset_seconds":0,
        "hourly_units":{"wind_speed_100m":"m/s","temperature_2m":"°C"},
        "hourly":{"time":ts.strftime("%Y-%m-%dT%H:%M").tolist(),
                  "wind_speed_100m":[6.]*n,
                  "temperature_2m":[15.]*n},
    }).encode()


def test_site_capacity_weights_and_ba_selection():
    s=validate_sites(sites())
    assert len(s)==2
    assert s.plant_id.tolist()==["100","200"]
    assert abs(s.capacity_weight.sum()-1)<1e-12
    assert s.nameplate_mw.sum()==150


def test_actual_utc_hours_and_sources_are_preserved(tmp_path):
    m=run(sites(),tmp_path,fetch=lambda _:response())
    assert m["plant_count"]==2
    assert m["hours"]==744 and m["site_hours"]==1488
    assert all(len(x["source_response_sha256"])==64 for x in m["plant_provenance"])
    assert not m["historical_reliability_calibrated"]
    data=pd.read_csv(tmp_path/"srp_era5_wind_fleet_hourly_exposure.csv")
    assert len(data)==744
    assert data.fleet_capacity_weighted_wind_speed_100m_ms.eq(6.).all()


def test_misaligned_hour_fails():
    s=validate_sites(sites()).iloc[0]
    raw=json.loads(response())
    raw["hourly"]["time"][0]="2024-01-02T00:00"
    with pytest.raises(ValueError,match="UTC hour mismatch"):
        parse_response(json.dumps(raw).encode(),s)


def test_null_weather_fails():
    s=validate_sites(sites()).iloc[0]
    raw=json.loads(response())
    raw["hourly"]["wind_speed_100m"][12]=None
    with pytest.raises((ValueError,TypeError),match=""):
        parse_response(json.dumps(raw).encode(),s)


def test_wrong_units_rejected():
    s=validate_sites(sites()).iloc[0]
    raw=json.loads(response())
    raw["hourly_units"]["wind_speed_100m"]="km/h"
    with pytest.raises(ValueError,match="units"):
        parse_response(json.dumps(raw).encode(),s)


def test_bad_coordinates_and_duplicate_plant_fail():
    a=sites()
    a.loc[1,"latitude"]=100.
    with pytest.raises(ValueError,match="coordinate"):
        validate_sites(a)
    with pytest.raises(ValueError,match="duplicate"):
        validate_sites(pd.concat([sites(),sites().iloc[[0]]],ignore_index=True))


def test_february_leap_year_coverage(tmp_path):
    m=run(sites(),tmp_path,year=2024,month=2,
          fetch=lambda _:response(month=2))
    assert m["hours"]==696
