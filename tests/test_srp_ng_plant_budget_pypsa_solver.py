"""Small monthly optimization integration test (model-enabled workflow only)."""
import pandas as pd
import pytest

pypsa=pytest.importorskip("pypsa")
pytest.importorskip("highspy")
from grid_resilience.srp_ng_plant_budget_pypsa import compare


def test_budget_tightening_cannot_improve_isolated_ng_portfolio_coverage():
    times=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    boundary=pd.DataFrame({"timestamp":times,"demand_mw":100.,
                           "interchange_mw":0.})
    plants=pd.DataFrame({"plant_id":["100","200"],"candidate_nameplate_mw":[50.,60.],
                         "page1_signed_ng_mwh":[5000.,6000.]})
    detail,s=compare(boundary,plants,scales=[1.,0.75])
    x=s.set_index("scenario")
    assert x.loc["unlimited_nameplate","modeled_portfolio_gap_mwh"]<1e-3
    assert abs(x.loc["1x_page1","scenario_gas_dispatch_mwh"]-11000)<1e-3
    assert abs(x.loc["0.75x_page1","scenario_gas_dispatch_mwh"]-8250)<1e-3
    assert x.loc["unlimited_nameplate","modeled_portfolio_gap_mwh"] <= x.loc["1x_page1","modeled_portfolio_gap_mwh"]+1e-4
    assert x.loc["1x_page1","modeled_portfolio_gap_mwh"] <= x.loc["0.75x_page1","modeled_portfolio_gap_mwh"]+1e-4
    assert (s.max_hourly_bus_residual_mw<1e-4).all()
    assert not x.loc["1x_page1","portfolio_gap_is_real_unserved_energy"]
    assert len(detail)==6
