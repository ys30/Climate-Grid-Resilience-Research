import pandas as pd
import pytest

from grid_resilience.paperc_crossyear_figure import summarize


def sample():
    rows=[]
    for name in ("isolated","links_10pct"):
        rows.append({"network_variant":name,
                     "july2023_interaction_model_mwh":12968.9,
                     "july2024_interaction_model_mwh":14630.3,
                     "july2023_baseline_model_gap_mwh":417730.6,
                     "july2024_baseline_model_gap_mwh":440029.1,
                     "frozen_2024_partial_fleet_used_in_2023":True,
                     "real_grid_calibration":False,"historical_eens":False})
    gate={"cross_period_holdout_source_admitted":True,
          "different_calendar_year_candidate_available":True,
          "source_supported_physical_grid_adequacy":False,
          "capacity_is_2024_partial_fleet_held_fixed_on_2023_not_true_2023_fleet":True}
    heat={"heat_load_response_active_ba_hours":509,"total_four_ba_hours":672,
          "measured_grid_heat_response":False}
    return pd.DataFrame(rows),gate,heat


def test_complete_2023_2024_comparison_admitted():
    t=summarize(*sample())
    assert len(t)==2
    assert set(t.network_variant)=={"isolated","links_10pct"}


def test_missing_year_specific_fleet_warning_rejected():
    t,g,h=sample()
    t["frozen_2024_partial_fleet_used_in_2023"]=False
    with pytest.raises(ValueError,match="fleet"):
        summarize(t,g,h)


def test_missing_cross_year_source_rejected():
    t,g,h=sample()
    g["different_calendar_year_candidate_available"]=False
    with pytest.raises(ValueError,match="source"):
        summarize(t,g,h)


def test_heat_not_activated_rejected():
    t,g,h=sample()
    h["heat_load_response_active_ba_hours"]=0
    with pytest.raises(ValueError,match="Heat"):
        summarize(t,g,h)


def test_historical_eens_claim_rejected():
    t,g,h=sample()
    t["historical_eens"]=True
    with pytest.raises(ValueError,match="EENS"):
        summarize(t,g,h)


def test_missing_network_rejected():
    t,g,h=sample()
    t.loc[1,"network_variant"]="isolated"
    with pytest.raises(ValueError,match="variants"):
        summarize(t,g,h)
