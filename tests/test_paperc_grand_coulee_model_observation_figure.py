"""Grand Coulee Paper C observed-vs-model plot source and scope regression."""
import json
import pandas as pd
import pytest

from grid_resilience.paperc_grand_coulee_model_observation_figure import verify, render

def fixture():
    names = ["PS_0MW_0MWh_eta100", "PS_78MW_314MWh_eta80",
             "PS_157MW_628MWh_eta80", "PS_314MW_1256MWh_eta80"]
    baseline = [1508297.366980, 1500630.261214, 1493497.715304, 1480655.729555]
    m = []
    for name, base in zip(names, baseline):
        m.append(dict(resource_scenario=name, baseline=base, heat_only=base+1000,
                      wind_only=base+2000, heat_wind=base+4000,
                      compound_interaction_mwh=1000))
    scope = dict(hypothetical_available_PS_fraction_of_nameplate=[0, .25, .5, 1],
                 original_eia860_six_ps_2024_nameplate_mw=314,
                 water_allocation_fraction_observed=False,
                 source_energy_capacity_MWh_observed=False,
                 historical_real_blackouts_or_avoided_EENS=False,
                 counterfactual_model_is_four_isolated_BA_incomplete_fleet=True)
    # Dates deliberately complete and independently audited cumulative source totals.
    d = pd.DataFrame(dict(date=pd.date_range("2024-07-01", periods=31),
                          usace_banks_lake_pumping_electricity_mwh=[6040]*27+[6080]+[2160]*2+[2161]))
    # July 1–28: 27*6040+6080=169160 ; July 29–31 = 6481.
    return pd.DataFrame(m), scope, d


def test_valid_source_separation():
    model, scope, data = fixture()
    m, d = verify(model, scope, data)
    assert len(m)==4 and len(d)==31
    assert list(m.resource_scenario)==list(model.resource_scenario)


def test_missing_source_day_rejected():
    model, scope, data = fixture()
    with pytest.raises(ValueError, match="daily cohort"):
        verify(model, scope, data.iloc[:-1])


def test_original_2024_pump_source_totals_guard():
    model, scope, data = fixture()
    data.loc[0,"usace_banks_lake_pumping_electricity_mwh"] += 10
    with pytest.raises(ValueError, match="source totals"):
        verify(model, scope, data)


def test_irrigation_fraction_cannot_claim_observation():
    model, scope, data = fixture()
    scope["water_allocation_fraction_observed"]=True
    with pytest.raises(ValueError, match="source/scope"):
        verify(model, scope, data)


def test_original_model_factorial_recomputed():
    model, scope, data = fixture()
    model.loc[1,"compound_interaction_mwh"] += 3
    with pytest.raises(ValueError, match="arithmetic"):
        verify(model, scope, data)


def test_render_png_and_pdf(tmp_path):
    pytest.importorskip("matplotlib")
    model, scope, data = fixture()
    verified, dates = verify(model, scope, data)
    render(verified, dates, tmp_path)
    assert (tmp_path/"paper_c_grand_coulee_model_vs_observed_context.png").stat().st_size>1000
    assert (tmp_path/"paper_c_grand_coulee_model_vs_observed_context.pdf").stat().st_size>1000
