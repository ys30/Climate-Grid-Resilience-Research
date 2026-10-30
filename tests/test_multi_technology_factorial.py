import pandas as pd
import pytest
from grid_resilience.multi_technology_factorial import run

def inputs(tmp_path):
    ts=["2024-07-01T00:00Z","2024-07-01T01:00Z"]
    d=tmp_path/"d.csv"; w=tmp_path/"w.csv"; c=tmp_path/"c.csv"; a=tmp_path/"a.csv"
    pd.DataFrame([{"timestamp":t,"ba":"CISO","demand_mw":50} for t in ts]).to_csv(d,index=False)
    pd.DataFrame([{"timestamp":t,"ba":"CISO","temperature_c":31} for t in ts]).to_csv(w,index=False)
    pd.DataFrame([{"ba":"CISO","technology":"gas","capacity_mw":100,"marginal_cost":70}]).to_csv(c,index=False)
    pd.DataFrame([{"timestamp":t,"ba":"CISO","technology":"gas","availability_pu":1} for t in ts]).to_csv(a,index=False)
    return d,w,c,a

def test_four_matched_multi_tech_scenarios(tmp_path):
    pytest.importorskip("pypsa")
    result=run(*inputs(tmp_path),tmp_path/"out",event_id="synthetic")
    assert result["n_bas"]==1
    assert result["total_nonadditive_interaction_mwh"]==pytest.approx(0,abs=1e-5)
    out=pd.read_csv(tmp_path/"out"/"multi_technology_factorial_dispatch.csv")
    assert set(out.scenario)=={"baseline","heat_only","wind_only","heat_wind"}
    assert len(out)==4

def test_missing_weather_rejected(tmp_path):
    pytest.importorskip("pypsa")
    paths=inputs(tmp_path)
    pd.read_csv(paths[1]).iloc[:-1].to_csv(paths[1],index=False)
    with pytest.raises(ValueError,match="coverage mismatch"):
        run(*paths,tmp_path/"out")
