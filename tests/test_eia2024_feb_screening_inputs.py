import pandas as pd
import pytest
from grid_resilience.eia2024_feb_screening_inputs import build

def inputs(tmp_path):
    dates=pd.date_range("2024-02-01",periods=696,freq="h",tz="UTC")
    bas=["AZPS","BPAT","CISO","SRP"]
    d=tmp_path/"d.csv";c=tmp_path/"c.csv"
    pd.DataFrame([{"timestamp":t.isoformat(),"ba":ba,"demand_mw":100}
                  for t in dates for ba in bas]).to_csv(d,index=False)
    pd.DataFrame([{"ba":ba,"technology":"gas","nameplate_capacity_mw":150}
                  for ba in bas]).to_csv(c,index=False)
    return d,c

def test_observed_demand_assumed_supply_flag(tmp_path):
    d,c=inputs(tmp_path)
    r=build(d,c,tmp_path/"out")
    assert r["demand_hours_per_ba"]==696
    assert not r["historical_inputs_verified"]
    assert not r["historical_calibration_certified"]
    assert "100%" in r["availability_assumption"]
    assert len(pd.read_csv(tmp_path/"out"/"availability.csv"))==2784

def test_reject_incomplete_historical_demand(tmp_path):
    d,c=inputs(tmp_path)
    df=pd.read_csv(d).iloc[1:]
    df.to_csv(d,index=False)
    with pytest.raises(ValueError,match="Incomplete demand"):
        build(d,c,tmp_path/"out")
