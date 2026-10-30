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


def test_hypothetical_link_supplies_second_ba(tmp_path):
    pytest.importorskip("pypsa")
    demand, capacity, avail = inputs(tmp_path)
    d = pd.read_csv(demand)
    d["demand_mw"] = 20
    d2 = d.copy()
    d2["ba"] = "AZPS"
    d2["demand_mw"] = 30
    pd.concat([d, d2], ignore_index=True).to_csv(demand, index=False)
    c = pd.read_csv(capacity)
    c.loc[len(c)] = ["AZPS", "gas", 0, 70]
    c.to_csv(capacity, index=False)
    a = pd.read_csv(avail)
    a2 = a.query("technology == 'gas'").copy()
    a2["ba"] = "AZPS"
    pd.concat([a, a2], ignore_index=True).to_csv(avail, index=False)
    links = tmp_path / "links.csv"
    pd.DataFrame([{"from_ba": "CISO", "to_ba": "AZPS", "capacity_mw": 40}]).to_csv(links, index=False)
    result = solve(demand, capacity, avail, tmp_path / "out", links_csv=links)
    assert result.unserved_energy_mwh.sum() == pytest.approx(0, abs=1e-5)

def test_rejects_unrecognized_link_bus(tmp_path):
    pytest.importorskip("pypsa")
    paths = inputs(tmp_path)
    links = tmp_path / "links.csv"
    pd.DataFrame([{"from_ba": "CISO", "to_ba": "UNKNOWN", "capacity_mw": 40}]).to_csv(links, index=False)
    with pytest.raises(ValueError, match="outside BA inventory"):
        solve(*paths, tmp_path / "out", links_csv=links)
