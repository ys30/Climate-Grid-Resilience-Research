import pandas as pd
import pytest
from grid_resilience.multi_technology_dispatch import solve

def inputs(tmp_path):
    d=tmp_path/"d.csv";c=tmp_path/"c.csv";a=tmp_path/"a.csv"
    ts=["2024-07-01T00:00:00Z","2024-07-01T01:00:00Z"]
    pd.DataFrame([{"timestamp": t, "ba":"CISO","demand_mw":50} for t in ts]).to_csv(d,index=False)
    pd.DataFrame([{"ba":"CISO","technology":"gas","capacity_mw":100,"marginal_cost":70},
                  {"ba":"CISO","technology":"solar","capacity_mw":20,"marginal_cost":0}]).to_csv(c,index=False)
    pd.DataFrame([{"timestamp":t,"ba":"CISO","technology":tech,"availability_pu":value}
                 for t in ts for tech,value in [("gas",1),("solar",0.5)]]).to_csv(a,index=False)
    return d,c,a

def test_two_technology_solve(tmp_path):
    pytest.importorskip("pypsa")
    p=inputs(tmp_path)
    result=solve(*p,tmp_path/"out")
    assert result.unserved_energy_mwh.iloc[0] == pytest.approx(0, abs=1e-5)
    generation=pd.read_csv(tmp_path/"out"/"generation_hourly.csv")
    assert len(generation)==4
    assert set(generation.technology)=={"gas","solar"}

def test_reject_missing_availability(tmp_path):
    pytest.importorskip("pypsa")
    p=inputs(tmp_path)
    df=pd.read_csv(p[2]).iloc[:-1]
    df.to_csv(p[2],index=False)
    with pytest.raises(ValueError,match="availability matrix"):
        solve(*p,tmp_path/"out")
