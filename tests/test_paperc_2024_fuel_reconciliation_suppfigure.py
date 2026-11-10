"""Synthetic smoke and fail-closed tests of supplemental reporting figure."""
import pandas as pd
import pytest

from grid_resilience.paperc_2024_fuel_reconciliation_suppfigure import validate
from grid_resilience.paperc_2024_seven_eight_fuel_reconciliation import reconcile
from grid_resilience.paperc_2024_full_fuel_schema_audit import BAS, START, N


def sample():
    x, s = [], []
    for ba in BAS:
        for h in range(N):
            t = START + pd.Timedelta(hours=h)
            for category, val in [("Other Fuel Sources", 3.0),
                                  ("All Petroleum Products", 1.0 if ba == "CISO" else None)]:
                x.append({"year": 2024, "ba": ba, "utc_hour_start": t,
                          "original_partition": "Jul_Dec",
                          "original_fuel_category": category,
                          "fuel_value_reported": val is not None,
                          "reported_fuel_mwh": val})
            s.append({"ba": ba, "utc_hour_start": t,
                      "net_generation_mw": 104.0 if ba == "CISO" else 103.0,
                      "all_six_original_components_numeric": ba != "BPAT",
                      "sum_six_original_reported_components_mwh": 100.0 if ba != "BPAT" else None})
    return reconcile(pd.DataFrame(x), pd.DataFrame(s))


def test_figure_validation_preserves_missing_cohorts():
    h, s = sample()
    assert len(validate(h, s)) == 644


def test_figure_rejects_reported_number_change():
    h, s = sample()
    h.loc[h.ba.eq("CISO").idxmax(), "net_minus_six_plus_other_petroleum_mwh"] = 10.0
    with pytest.raises(ValueError, match="Summary mismatch"):
        validate(h, s)


def test_figure_rejects_missing_hour():
    h, s = sample()
    with pytest.raises(ValueError, match="cohort|incomplete"):
        validate(h.iloc[1:], s)


def test_figure_writes_two_formats(tmp_path):
    pytest.importorskip("matplotlib")
    from grid_resilience.paperc_2024_fuel_reconciliation_suppfigure import draw
    h, s = sample()
    draw(h, s, tmp_path)
    assert (tmp_path / "paper_c_original_fuel_reconciliation_supplement.png").stat().st_size > 1000
    assert (tmp_path / "paper_c_original_fuel_reconciliation_supplement.pdf").stat().st_size > 1000
