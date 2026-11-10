"""Regression guards for EIA-930 signed reporting arithmetic (synthetic fixtures)."""
import pandas as pd
import pytest

from grid_resilience.paperc_2024_seven_eight_fuel_reconciliation import (
    reconcile, OTHER, PETROLEUM,
)
from grid_resilience.paperc_2024_full_fuel_schema_audit import BAS, N, START


def fixtures():
    fuel_rows, six_rows = [], []
    for ba in BAS:
        for i in range(N):
            hour = START + pd.Timedelta(hours=i)
            other = {"AZPS": 2.0, "BPAT": 3.0, "CISO": -4.0, "SRP": -1.0}[ba]
            petro = 1.0 if ba == "CISO" else None
            for label, value in [(OTHER, other), (PETROLEUM, petro)]:
                fuel_rows.append(dict(year=2024, ba=ba, utc_hour_start=hour,
                    original_partition="Jul_Dec", original_fuel_category=label,
                    fuel_value_reported=value is not None,
                    reported_fuel_mwh=value))
            six_rows.append(dict(ba=ba, utc_hour_start=hour,
                net_generation_mw=110.0 + other + (petro or 0),
                all_six_original_components_numeric=ba != "BPAT",
                sum_six_original_reported_components_mwh=110.0 if ba != "BPAT" else None))
    return pd.DataFrame(fuel_rows), pd.DataFrame(six_rows)


def test_signed_reconciliation_admits_only_source_complete_selected_categories():
    fuel, six = fixtures()
    hourly, summary = reconcile(fuel, six)
    assert len(hourly) == 4 * N
    counts = summary.set_index("ba")
    assert counts.loc["AZPS", "seven_numeric_hours"] == N
    assert counts.loc["SRP", "seven_numeric_hours"] == N
    assert counts.loc["CISO", "eight_numeric_hours"] == N
    assert counts.loc["AZPS", "eight_numeric_hours"] == 0
    assert counts.loc["BPAT", "seven_numeric_hours"] == 0
    assert pd.isna(counts.loc["BPAT", "signed_seven_difference_mwh"])
    assert counts.loc["CISO", "signed_eight_difference_mwh"] == pytest.approx(0)
    assert hourly.all_16_categories_certified_complete.eq(False).all()


def test_missing_other_must_not_become_zero():
    fuel, six = fixtures()
    idx = fuel.index[(fuel.ba == "AZPS") &
                     (fuel.original_fuel_category == OTHER)][0]
    fuel.loc[idx, "fuel_value_reported"] = False
    fuel.loc[idx, "reported_fuel_mwh"] = float("nan")
    hourly, summary = reconcile(fuel, six)
    az = summary.set_index("ba").loc["AZPS"]
    assert az.seven_numeric_hours == N - 1
    assert pd.isna(hourly[(hourly.ba == "AZPS") &
                         (hourly.utc_hour_start == START)]
                  .net_minus_six_plus_other_mwh.iloc[0])


def test_reject_invalid_original_source_null_flag():
    fuel, six = fixtures()
    idx = fuel.index[(fuel.ba == "SRP") &
                     (fuel.original_fuel_category == PETROLEUM)][0]
    fuel.loc[idx, "fuel_value_reported"] = True
    with pytest.raises(ValueError, match="flags inconsistent"):
        reconcile(fuel, six)


def test_reject_duplicate_source_hour_category():
    fuel, six = fixtures()
    with pytest.raises(ValueError, match="Duplicate"):
        reconcile(pd.concat([fuel, fuel.iloc[:1]], ignore_index=True), six)
