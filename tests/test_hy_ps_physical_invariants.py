"""Physical regression: no free energy from initially empty pumped storage."""
import pytest
from grid_resilience.hy_ps_budget_scenario import assumptions
from grid_resilience.hy_ps_pypsa_components import add_hy_ps

def test_empty_pumped_storage_cannot_supply_free_energy():
    pypsa=pytest.importorskip("pypsa")
    n=pypsa.Network()
    n.set_snapshots(range(4))
    n.add("Bus","SRP")
    n.add("Load","load",bus="SRP",p_set=[1.0]*4)
    n.add("Generator","unserved",bus="SRP",p_nom=2.0,marginal_cost=100000)
    # No real generation, no hydro energy, empty PS at beginning and end.
    settings=assumptions(0.0,4.0,0.81)
    components=add_hy_ps(n,"SRP",settings)
    status,condition=n.optimize(solver_name="highs")
    assert condition=="optimal",(status,condition)
    assert n.generators_t.p["unserved"].sum()==pytest.approx(4.0,abs=1e-5)
    assert (-n.links_t.p1[components["hydro_link"]]).sum()==pytest.approx(0,abs=1e-5)
    charge=n.links_t.p0[components["storage_charge_link"]].sum()
    discharge=(-n.links_t.p1[components["storage_discharge_link"]]).sum()
    assert discharge<=charge*0.81+1e-5
    assert n.stores_t.e["SRP_ps_energy"].iloc[-1]==pytest.approx(0,abs=1e-5)
