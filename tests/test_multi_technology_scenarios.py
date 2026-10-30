import pandas as pd
import pytest
from grid_resilience.multi_technology_scenarios import prepare_scenarios

def inputs(tmp_path):
    d=tmp_path/"d.csv";w=tmp_path/"w.csv";a=tmp_path/"a.csv"
    hours=["2024-07-01T00:00Z","2024-07-01T01:00Z"]
    pd.DataFrame([{"timestamp":t,"ba":"CISO","demand_mw":100} for t in hours]).to_csv(d,index=False)
    pd.DataFrame([{"timestamp":t,"ba":"CISO","temperature_c":31} for t in hours]).to_csv(w,index=False)
    pd.DataFrame([{"timestamp":t,"ba":"CISO","technology":"wind","availability_pu":0.5} for t in hours]).to_csv(a,index=False)
    return d,w,a

def test_matched_scenarios(tmp_path):
    p=inputs(tmp_path)
    result=prepare_scenarios(*p,tmp_path/"out")
    assert len(result["scenarios"])==4
    b=pd.read_csv(tmp_path/"out"/"baseline"/"demand.csv")
    h=pd.read_csv(tmp_path/"out"/"heat_only"/"demand.csv")
    w=pd.read_csv(tmp_path/"out"/"wind_only"/"availability.csv")
    hw=pd.read_csv(tmp_path/"out"/"heat_wind"/"availability.csv")
    assert b.demand_mw.iloc[0]==pytest.approx(100)
    assert h.demand_mw.iloc[0]==pytest.approx(104.8)
    assert w.availability_pu.iloc[0]==pytest.approx(.35)
    assert hw.availability_pu.iloc[0]==pytest.approx(.35)

def test_reject_unmatched_weather(tmp_path):
    p=inputs(tmp_path)
    df=pd.read_csv(p[1]).iloc[:-1]
    df.to_csv(p[1],index=False)
    with pytest.raises(ValueError,match="coverage mismatch"):
        prepare_scenarios(*p,tmp_path/"out")
