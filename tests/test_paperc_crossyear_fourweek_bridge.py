"""Source-based crossyear versus four-week shared-2024-anchor tests."""
import pandas as pd
import pytest

from grid_resilience.paperc_crossyear_fourweek_bridge import (
    REQUIRED_CROSS_GATE, REQUIRED_FOUR_GATE, bridge,
)


def sample():
    cross = pd.DataFrame([
        {"network_variant": variant,
         "july2023_interaction_model_mwh": 10.0 + i,
         "july2024_interaction_model_mwh": 100.0 + i,
         "july2024_baseline_model_gap_mwh": 1000.0 + i,
         "frozen_2024_partial_fleet_used_in_2023": True,
         "historical_eens": False, "real_grid_calibration": False}
        for i, variant in enumerate(("isolated", "links_10pct"))
    ])
    four_system = pd.DataFrame([
        {"event_id": f"JULY2024_WEEK_{week}", "isolated": 100.0,
         "links_10pct": 101.0,
         "links_minus_isolated_interaction_mwh": 1.0}
        for week in range(1, 5)
    ])
    four_ba = []
    for week in range(1, 5):
        for i, variant in enumerate(("isolated", "links_10pct")):
            for ba in ("AZPS", "BPAT", "CISO", "SRP", "SYSTEM"):
                four_ba.append({
                    "event_id": f"JULY2024_WEEK_{week}", "network_variant": variant,
                    "ba": ba, "modeled_factorial_interaction_mwh": 100.0 + i,
                    "baseline_shortage_mwh": 1000.0 + i,
                })
    return cross, four_system, pd.DataFrame(four_ba), dict(REQUIRED_CROSS_GATE), dict(REQUIRED_FOUR_GATE)


def test_original_model_week_one_shared_anchor_agrees():
    result, scope = bridge(*sample())
    assert len(result) == 2
    assert scope["max_abs_2024_anchor_discrepancy_mwh"] == 0
    assert scope["crossyear_and_fourweek_2024_results_not_independent_replications"]


def test_rejects_crossyear_year2024_new_solver_disagreement():
    data = list(sample())
    data[0].loc[0, "july2024_interaction_model_mwh"] += 5
    with pytest.raises(ValueError, match="anchor mismatch"):
        bridge(*data)


def test_rejects_same_week_but_mismatched_baseline():
    data = list(sample())
    data[0].loc[0, "july2024_baseline_model_gap_mwh"] += 1
    with pytest.raises(ValueError, match="anchor mismatch"):
        bridge(*data)


def test_rejects_unverified_generator_fleet():
    data = list(sample())
    data[3]["capacity_is_2024_partial_fleet_held_fixed_on_2023_not_true_2023_fleet"] = False
    with pytest.raises(ValueError, match="scope gate"):
        bridge(*data)


def test_rejects_missing_or_duplicate_common_anchor():
    data = list(sample())
    data[2] = data[2].iloc[1:]
    with pytest.raises(ValueError, match="40 BA"):
        bridge(*data)


def test_rejects_false_historical_eens():
    data = list(sample())
    data[0].loc[0, "historical_eens"] = True
    with pytest.raises(ValueError, match="reliability flags"):
        bridge(*data)
