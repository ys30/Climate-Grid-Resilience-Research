import pandas as pd
import pytest
from grid_resilience.monthly_generation_gate import monthly_generation

def test_rejects_partial_event(tmp_path):
    p=tmp_path/"hourly.csv"
    pd.DataFrame([{"timestamp":"2024-07-01T00:00:00Z","ba":"CISO",
                   "technology":"wind","generation_mwh":10}]).to_csv(p,index=False)
    with pytest.raises(ValueError,match="Incomplete calendar month"):
        monthly_generation(p,tmp_path/"out")

def test_accepts_complete_leap_february(tmp_path):
    p=tmp_path/"hourly.csv"
    ts=pd.date_range("2024-02-01",periods=29*24,freq="h",tz="UTC")
    pd.DataFrame([{"timestamp":str(t),"ba":"CISO","technology":"wind",
                   "generation_mwh":2} for t in ts]).to_csv(p,index=False)
    result=monthly_generation(p,tmp_path/"out")
    assert result["periods"]==["2024-02"]
    df=pd.read_csv(tmp_path/"out"/"modeled_generation_full_months.csv")
    assert df.generation_mwh.iloc[0]==pytest.approx(29*24*2)
