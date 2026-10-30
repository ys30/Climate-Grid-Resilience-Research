import pandas as pd
import pytest
from grid_resilience.match_observed_inputs import match

def fixture(tmp_path):
    dates=pd.date_range("2024-07-01",periods=168,freq="h",tz="UTC")
    base=[dict(timestamp=dt.isoformat(),ba=ba) for dt in dates for ba in ("CISO","AZPS","BPAT","SRP")]
    d=pd.DataFrame(base);d["demand_mw"]=100.
    w=pd.DataFrame(base);w["temperature_c"]=35.;w["wind_availability"]=.5
    a=tmp_path/"d.csv";b=tmp_path/"w.csv"
    d.to_csv(a,index=False);w.to_csv(b,index=False)
    return a,b

def test_match_complete(tmp_path):
    a,b=fixture(tmp_path)
    result=match(a,b,tmp_path/"out")
    assert result["rows"]==672
    assert pd.read_csv(tmp_path/"out"/"matched_hourly.csv").shape[0]==672

def test_missing_weather_is_rejected(tmp_path):
    a,b=fixture(tmp_path)
    frame=pd.read_csv(b).iloc[:-1];frame.to_csv(b,index=False)
    with pytest.raises(ValueError,match="keys differ"):
        match(a,b,tmp_path/"out")
