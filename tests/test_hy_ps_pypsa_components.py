"""Regression for missing pumped-storage discharge link and rated output."""
import pytest
from grid_resilience.hy_ps_budget_scenario import assumptions
from grid_resilience.hy_ps_pypsa_components import add_hy_ps

def test_hy_ps_components_exist_and_discharge_output_is_nameplate():
    pypsa=pytest.importorskip("pypsa")
    n=pypsa.Network()
    n.set_snapshots(range(24))
    n.add("Bus","SRP")
    settings=assumptions(12.0,4.0,0.81)
    mapping=add_hy_ps(n,"SRP",settings)
    assert mapping["hydro_link"] in n.links.index
    assert mapping["storage_charge_link"] in n.links.index
    assert mapping["storage_discharge_link"] in n.links.index
    assert "SRP_ps_energy" in n.stores.index
    discharge=n.links.loc[mapping["storage_discharge_link"]]
    assert discharge.p_nom*discharge.efficiency==pytest.approx(154.1)
    assert n.stores.loc["SRP_ps_energy","e_nom"]==pytest.approx(616.4)
    assert not bool(n.stores.loc["SRP_ps_energy","e_cyclic"])
    assert n.stores.loc["SRP_ps_energy","e_initial"]==pytest.approx(0)
    assert n.stores_t.e_max_pu["SRP_ps_energy"].iloc[-1]==pytest.approx(0)
    assert n.stores_t.e_min_pu["SRP_ps_energy"].iloc[-1]==pytest.approx(0)
