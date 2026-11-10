"""Main-figure provenance and exact recomputation tests (synthetic)."""
import pandas as pd
import pytest

from grid_resilience.july2024_four_week_factorial_replication import summarize
from grid_resilience.paperc_2024_four_week_mainfigure import prepare, draw, REQUIRED_META


def sample():
    rows = []
    for i in range(1, 5):
        for variant in ("isolated", "links_10pct"):
            for ba in ("AZPS", "BPAT", "CISO", "SRP"):
                base = 10000 + 200 * i
                for scenario, increment in [
                    ("baseline", 0), ("heat_only", 20), ("wind_only", 30),
                    ("heat_wind", 60 if variant == "isolated" else 70)
                ]:
                    rows.append({
                        "event_id": f"JULY2024_WEEK_{i}",
                        "network_variant": variant,
                        "ba": ba, "scenario": scenario,
                        "unserved_energy_mwh": base + increment,
                        "shortage_hours": 20, "peak_shortfall_mw": 100
                    })
    dispatch = pd.DataFrame(rows)
    ba, contrast = summarize(dispatch)
    return dispatch, ba, contrast, dict(REQUIRED_META)


def test_recomputes_same_factorial_with_exact_keys():
    dispatch, ba, contrast, scope = sample()
    independent, system = prepare(dispatch, ba, contrast, scope)
    assert len(independent) == 40
    assert len(system) == 4
    assert system["links_minus_isolated_interaction_mwh"].eq(40).all()


def test_rejects_changed_archived_result():
    dispatch, ba, contrast, scope = sample()
    ba.loc[0, "modeled_factorial_interaction_mwh"] += 1
    with pytest.raises(ValueError, match="disagree"):
        prepare(dispatch, ba, contrast, scope)


def test_rejects_uncalibrated_result_falsely_represented_as_eens():
    dispatch, ba, contrast, scope = sample()
    scope["modeled_shortage_is_observed_eens"] = True
    with pytest.raises(ValueError, match="scope gate"):
        prepare(dispatch, ba, contrast, scope)


def test_figures_written_from_recomputed_model_results(tmp_path):
    pytest.importorskip("matplotlib")
    dispatch, ba, contrast, scope = sample()
    independent, system = prepare(dispatch, ba, contrast, scope)
    draw(independent, system, tmp_path)
    assert (tmp_path / "paper_c_july2024_four_week_factorial_main.png").stat().st_size > 1000
    assert (tmp_path / "paper_c_july2024_four_week_factorial_main.pdf").stat().st_size > 1000
