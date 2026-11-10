"""Strict source-model bridge: 2023/2024 summer figure versus July-2024 four-week figure.

This is a deterministic artifact-to-artifact consistency check, NOT a new
PyPSA simulation, observed physical resource adequacy or independent sampling.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

VARIANTS = ("isolated", "links_10pct")
REQUIRED_CROSS_GATE = {
    "cross_period_holdout_source_admitted": True,
    "different_calendar_year_candidate_available": True,
    "source_supported_physical_grid_adequacy": False,
    "capacity_is_2024_partial_fleet_held_fixed_on_2023_not_true_2023_fleet": True,
}
REQUIRED_FOUR_GATE = {
    "same_partial_eia860_annual_capacity_all_events": True,
    "same_hypothetical_intertie_rating_all_events": True,
    "same_assumed_heat_load_wind_response_all_events": True,
    "modeled_shortage_is_observed_eens": False,
    "physical_intertie_ratings_verified": False,
    "distinct_real_july_weeks": 4,
}


def bridge(cross, four_system, four_ba, cross_gate, four_gate, tolerance_mwh=0.001):
    for key, val in REQUIRED_CROSS_GATE.items():
        if cross_gate.get(key) != val:
            raise ValueError(f"Cross-year scope gate invalid: {key}")
    for key, val in REQUIRED_FOUR_GATE.items():
        if four_gate.get(key) != val:
            raise ValueError(f"Four-week scope gate invalid: {key}")
    cross_cols = {
        "network_variant", "july2023_interaction_model_mwh",
        "july2024_interaction_model_mwh", "july2024_baseline_model_gap_mwh",
        "frozen_2024_partial_fleet_used_in_2023", "historical_eens",
        "real_grid_calibration",
    }
    if not cross_cols.issubset(cross) or len(cross) != 2:
        raise ValueError("Cross-year comparison source columns incomplete")
    if (not cross.frozen_2024_partial_fleet_used_in_2023.eq(True).all()
            or not cross.historical_eens.eq(False).all()
            or not cross.real_grid_calibration.eq(False).all()):
        raise ValueError("Cross-year 2024 proxy fleet or reliability flags invalid")
    if cross.network_variant.duplicated().any() or set(cross.network_variant) != set(VARIANTS):
        raise ValueError("Cross-year network variants incomplete")
    need_system = {"event_id", "isolated", "links_10pct", "links_minus_isolated_interaction_mwh"}
    if not need_system.issubset(four_system) or len(four_system) != 4:
        raise ValueError("Four-week source system columns incomplete")
    if four_system.event_id.duplicated().any() or set(four_system.event_id) != {
        f"JULY2024_WEEK_{k}" for k in range(1, 5)
    }:
        raise ValueError("Four-week event keys not exactly matched")
    need_ba = {"event_id", "network_variant", "ba", "baseline_shortage_mwh",
               "modeled_factorial_interaction_mwh"}
    if not need_ba.issubset(four_ba):
        raise ValueError("Four-week BA source columns absent")
    if four_ba.duplicated(["event_id", "network_variant", "ba"]).any():
        raise ValueError("Duplicate four-week BA source key")
    if len(four_ba) != 40:
        raise ValueError("Expected 40 BA and system factorial results")
    rows = []
    week1 = four_system.set_index("event_id").loc["JULY2024_WEEK_1"]
    for variant in VARIANTS:
        c = cross.set_index("network_variant").loc[variant]
        b = four_ba.loc[(four_ba.event_id == "JULY2024_WEEK_1") &
                        (four_ba.network_variant == variant) &
                        (four_ba.ba == "SYSTEM")]
        if len(b) != 1:
            raise ValueError("Four-week SYSTEM baseline key incomplete")
        original = b.iloc[0]
        anchor = float(week1[variant])
        ba_anchor = float(original.modeled_factorial_interaction_mwh)
        cross_anchor = float(c.july2024_interaction_model_mwh)
        base_cross = float(c.july2024_baseline_model_gap_mwh)
        base_four = float(original.baseline_shortage_mwh)
        vals = [anchor, ba_anchor, cross_anchor, base_cross, base_four,
                float(c.july2023_interaction_model_mwh)]
        if not np.isfinite(vals).all():
            raise ValueError("Nonfinite source model evidence")
        if (abs(anchor - ba_anchor) > tolerance_mwh
                or abs(anchor - cross_anchor) > tolerance_mwh
                or abs(base_cross - base_four) > tolerance_mwh):
            raise ValueError(f"2024 common Week 1 original-model anchor mismatch: {variant}")
        rows.append({
            "network_variant": variant,
            "source_2023_window": "2023-07-10/2023-07-16",
            "source_2024_shared_window": "2024-07-01/2024-07-07",
            "july2023_interaction_model_mwh": float(c.july2023_interaction_model_mwh),
            "shared_2024_week1_interaction_model_mwh": anchor,
            "shared_2024_week1_baseline_model_gap_mwh": base_four,
            "crossyear_minus_fourweek_interaction_mwh": cross_anchor - anchor,
            "crossyear_minus_fourweek_baseline_mwh": base_cross - base_four,
            "frozen_2024_partial_fleet_both_years": True,
            "real_grid_calibration_certified": False,
            "historical_eens_estimated": False,
        })
    result = pd.DataFrame(rows).sort_values("network_variant").reset_index(drop=True)
    # The shared 2024 anchor is a reused model run, NOT an independent replication.
    scope = {
        "shared_2024_week1_is_same_original_model_anchor": True,
        "crossyear_and_fourweek_2024_results_not_independent_replications": True,
        "source_year_2023_uses_frozen_2024_partial_capacity": True,
        "hypothetical_network_and_derived_wind_response": True,
        "year_2023_and_year_2024_windows_not_severity_matched": True,
        "number_of_independent_physical_adequacy_validations": 0,
        "modeled_shortage_not_historical_eens": True,
        "max_abs_2024_anchor_discrepancy_mwh": float(max(
            result.crossyear_minus_fourweek_interaction_mwh.abs().max(),
            result.crossyear_minus_fourweek_baseline_mwh.abs().max()
        )),
    }
    return result, scope


def main():
    p = argparse.ArgumentParser()
    for x in ("cross", "four-system", "four-ba", "cross-gate", "four-gate", "output"):
        p.add_argument("--" + x, required=True)
    a = p.parse_args()
    read_scope = lambda f: json.loads(Path(f).read_text())
    out, scope = bridge(pd.read_csv(a.cross), pd.read_csv(a.four_system),
                        pd.read_csv(a.four_ba), read_scope(a.cross_gate),
                        read_scope(a.four_gate))
    dest = Path(a.output)
    dest.mkdir(parents=True, exist_ok=True)
    out.to_csv(dest / "paper_c_crossyear_fourweek_shared_2024_anchor.csv", index=False)
    (dest / "paper_c_crossyear_fourweek_common_anchor_scope.json").write_text(
        json.dumps(scope, indent=2) + "\n")
    print(out.to_string(index=False))
    print(json.dumps(scope, indent=2))


if __name__ == "__main__":
    main()
