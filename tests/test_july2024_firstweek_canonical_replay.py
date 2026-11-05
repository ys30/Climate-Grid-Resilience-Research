import numpy as np
import pandas as pd
import pytest
from grid_resilience.july2024_firstweek_canonical_replay import source_parity

def source():
    hours=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    weather=pd.DataFrame([{"timestamp":t,"ba":b,"temperature_c":32.,
                           "wind_availability":.4}
                           for t in hours for b in ("AZPS","BPAT","CISO","SRP")])
    demand=weather[["timestamp","ba"]].assign(demand_mw=5000.)
    return weather,demand

def test_canonical_168_hours_per_four_bas():
    w,d=source()
    m=source_parity(w,w.copy(),d)
    assert m["source_weather_exact_match"]
    assert m["weather_source_hour_exact_pairs"]==672
    assert not m["missing_source_interpolation"]

def test_weather_difference_is_rejected():
    w,d=source()
    v=w.copy();v.loc[0,"temperature_c"]+=.5
    with pytest.raises(ValueError,match="Original weather does not match"):
        source_parity(w,v,d)

def test_absent_canonical_demand_hour_is_rejected():
    w,d=source()
    with pytest.raises(ValueError,match="Invalid canonical_demand"):
        source_parity(w,w,d.iloc[:-1])

def test_duplicated_weather_hour_is_rejected():
    w,d=source()
    with pytest.raises(ValueError,match="Invalid legacy_weather"):
        source_parity(pd.concat([w,w.iloc[[0]]]),w,d)
