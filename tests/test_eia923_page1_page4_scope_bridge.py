"""Synthetic scope comparisons; never assert Page 1 + Page 4 is BA generation."""
import pandas as pd
import pytest
from grid_resilience.eia923_page1_page4_scope_bridge import bridge


def source_frames():
    page1 = pd.DataFrame({
        "plant_id": ["0007", "9", "10"],
        "reported_ba": ["SRP"] * 3,
        "period": ["2024-01"] * 3,
        "prime_mover": ["HY", "PS", "ST"],
        "reported_fuel": ["WAT", "WAT", "NG"],
        "net_generation_mwh": [30.0, -4.0, 6.0],
    })
    page4 = pd.DataFrame({
        "plant_id": ["7", "8", "11"],
        "generator_id": ["001", "2", "3"],
        "reported_ba": ["SRP"] * 3,
        "period": ["2024-01"] * 3,
        "generation_mwh": [10.0, 20.0, -2.0],
    })
    return page1, page4


def test_overlap_and_signed_source_sums_are_kept_separate():
    rows, overlap, result = bridge(*source_frames())
    assert overlap.plant_id.tolist() == ["7"]
    assert result["page1_reported_mwh_source_only"] == 32.0
    assert result["page4_reported_mwh_source_only"] == 28.0
    assert result["plants_present_in_both_sheets"] == 1
    assert result["page1_only_plants"] == 2
    assert result["page4_only_plants"] == 2
    assert not result["page1_page4_sum_permitted"]
    assert not result["duplicate_physical_generation_ruled_out"]
    assert not result["eia930_ba_wide_calibration_certified"]
    assert rows.loc[rows.source.eq("page1"), "record_count"].sum() == 3
    assert rows.loc[rows.source.eq("page4"), "record_count"].sum() == 3


def test_duplicate_page1_plant_fuel_month_fails_closed():
    a, b = source_frames()
    with pytest.raises(ValueError, match="Duplicate Page 1"):
        bridge(pd.concat([a, a.iloc[[0]]], ignore_index=True), b)


def test_duplicate_page4_generator_month_fails_closed():
    a, b = source_frames()
    with pytest.raises(ValueError, match="Duplicate Page 4"):
        bridge(a, pd.concat([b, b.iloc[[0]]], ignore_index=True))


@pytest.mark.parametrize("source,column", [
    ("page1", "net_generation_mwh"),
    ("page4", "generation_mwh"),
])
def test_nonfinite_generation_fails_closed(source, column):
    a, b = source_frames()
    target = a if source == "page1" else b
    target.loc[0, column] = float("inf")
    with pytest.raises(ValueError, match="nonfinite"):
        bridge(a, b)


def test_missing_source_rows_is_not_silently_zero():
    a, b = source_frames()
    with pytest.raises(ValueError, match="no selected"):
        bridge(a.iloc[:0], b)


def test_invalid_month_and_missing_generator_identity_fail():
    a, b = source_frames()
    with pytest.raises(ValueError, match="Invalid requested period"):
        bridge(a, b, period="2024-13")
    b.loc[0, "generator_id"] = ""
    with pytest.raises(ValueError, match="missing identity"):
        bridge(a, b)


def test_scope_filter_never_sums_other_ba_months():
    a, b = source_frames()
    a = pd.concat([a, a.assign(period="2024-02")], ignore_index=True)
    b = pd.concat([b, b.assign(reported_ba="AZPS")], ignore_index=True)
    _, _, result = bridge(a, b)
    assert result["page1_source_rows"] == 3
    assert result["page4_source_rows"] == 3
