import pytest
from grid_resilience.hy_ps_budget_scenario import assumptions

def test_hydro_and_storage_dimensions():
    d=assumptions(1015.0,4.0,.81)
    assert d["hydro_nameplate_mw"]==91.1
    assert d["ps_discharge_nameplate_mw"]==154.1
    assert d["ps_energy_capacity_mwh_assumed"]==pytest.approx(616.4)
    assert d["historical_calibration_certified"] is False

@pytest.mark.parametrize("budget,hours,eff",[
    (-1,4,.81),(None,4,.81),(10,0,.81),(10,49,.81),(10,4,0),(10,4,1.1)])
def test_invalid_or_undocumented_scenarios_rejected(budget,hours,eff):
    with pytest.raises(ValueError):
        assumptions(budget,hours,eff)
