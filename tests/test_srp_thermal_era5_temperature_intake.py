import json
import pandas as pd
import pytest
from grid_resilience.srp_thermal_era5_temperature_intake import sample,validate_response


def sites():
    return pd.DataFrame({
        "technology":["gas","coal"],"plant_id":["1","2"],
        "latitude":[33.,34.],"longitude":[-111.,-112.],
        "nameplate_mw":[100.,50.]})


def response():
    ts=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    return json.dumps({"utc_offset_seconds":0,
        "hourly_units":{"temperature_2m":"°C"},
        "hourly":{"time":ts.strftime("%Y-%m-%dT%H:%M").tolist(),
                  "temperature_2m":[12.]*744}}).encode()


def test_thermal_era5_complete_source_hour_coverage(tmp_path):
    m=sample(sites(),tmp_path,fetch=lambda _:response())
    assert m["selected_site_count"]==2
    assert m["selected_site_hours"]==1488
    assert not m["weather_to_generator_derating_calibrated"]
    x=pd.read_csv(tmp_path/"srp_thermal_era5_technology_hourly.csv")
    assert len(x)==1488
    assert x.capacity_weighted_temperature_c.eq(12.).all()


def test_misaligned_utc_rejected():
    x=json.loads(response())
    x["hourly"]["time"][0]="2024-02-01T00:00"
    with pytest.raises(ValueError,match="UTC"):
        validate_response(json.dumps(x).encode())


def test_null_temperature_rejected():
    x=json.loads(response())
    x["hourly"]["temperature_2m"][100]=None
    with pytest.raises((ValueError,TypeError)):
        validate_response(json.dumps(x).encode())


def test_duplicate_site_rejected(tmp_path):
    s=sites()
    with pytest.raises(ValueError,match="duplicate"):
        sample(pd.concat([s,s.iloc[[0]]],ignore_index=True),tmp_path,
               fetch=lambda _:response())


def test_bad_source_units_rejected():
    x=json.loads(response())
    x["hourly_units"]["temperature_2m"]="F"
    with pytest.raises(ValueError,match="units"):
        validate_response(json.dumps(x).encode())


def test_july_2024_hour_boundaries_and_weighted_output(tmp_path):
    times=pd.date_range("2024-07-01",periods=744,freq="h",tz="UTC")
    raw=json.dumps({"utc_offset_seconds":0,
        "hourly_units":{"temperature_2m":"°C"},
        "hourly":{"time":times.strftime("%Y-%m-%dT%H:%M").tolist(),
                  "temperature_2m":[35.]*744}}).encode()
    m=sample(sites(),tmp_path,year=2024,month=7,fetch=lambda _:raw)
    assert m["period"]=="2024-07"
    assert m["selected_site_hours"]==1488
    x=pd.read_csv(tmp_path/"srp_thermal_era5_technology_hourly.csv")
    assert x.capacity_weighted_temperature_c.eq(35).all()


def test_invalid_month_rejected_before_download(tmp_path):
    with pytest.raises(ValueError,match="month"):
        sample(sites(),tmp_path,year=2024,month=13,fetch=lambda _:response())


def test_transient_era5_transport_failure_retries_without_losing_hours(tmp_path):
    from urllib.error import URLError
    calls={"n":0}
    def unstable(_url):
        calls["n"]+=1
        if calls["n"]==1:
            raise URLError("temporary SSL handshake timeout")
        return response()
    m=sample(sites(),tmp_path,fetch=unstable)
    assert calls["n"]==3
    assert m["selected_site_hours"]==1488
