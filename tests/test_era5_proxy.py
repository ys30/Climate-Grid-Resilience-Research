import pytest
from grid_resilience.era5_proxy import convert

def hour_values():
    return {"time":["2024-07-01T00:00","2024-07-01T01:00"],
            "temperature_2m":[35,36],"wind_speed_100m":[3,12]}

def test_valid_hourly_conversion():
    d=convert(hour_values(),"AZPS","2024-07-01T00:00:00Z","2024-07-01T02:00:00Z")
    assert len(d)==2
    assert d.wind_availability.tolist()==[0,1]

def test_missing_hour_fails():
    x=hour_values()
    for k in x:x[k]=x[k][:1]
    with pytest.raises(ValueError,match="incomplete"):
        convert(x,"AZPS","2024-07-01T00:00:00Z","2024-07-01T02:00:00Z")

def test_unsafe_wind_values_fail():
    x=hour_values();x["wind_speed_100m"][0]=-1
    with pytest.raises(ValueError,match="invalid"):
        convert(x,"AZPS","2024-07-01T00:00:00Z","2024-07-01T02:00:00Z")
