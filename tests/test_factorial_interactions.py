import pandas as pd
import pytest
from grid_resilience.factorial_interactions import decompose

def sample():
    rows=[]
    for scenario,mwh in [("baseline",10),("heat_only",25),("wind_only",18),("heat_wind",40)]:
        rows.append(dict(event_id="E1",ba="AZPS",network_variant="base",scenario=scenario,
                         unserved_energy_mwh=mwh,shortage_hours=mwh/10,peak_shortfall_mw=mwh/5))
    return pd.DataFrame(rows)

def test_complete_four_way_interaction():
    r=decompose(sample()).iloc[0]
    assert r.unserved_energy_mwh_heat_effect==15
    assert r.unserved_energy_mwh_wind_effect==8
    assert r.unserved_energy_mwh_nonadditive_interaction==7

def test_three_scenario_current_model_cannot_claim_interaction():
    with pytest.raises(ValueError,match="complete factorial"):
        decompose(sample().query("scenario != 'wind_only'"))

def test_rejects_duplicate_scenarios():
    with pytest.raises(ValueError,match="Duplicate"):
        decompose(pd.concat([sample(),sample().iloc[[0]]]))
