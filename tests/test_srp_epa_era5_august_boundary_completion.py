import pandas as pd
import pytest

from grid_resilience.srp_epa_era5_august_boundary_completion import complete_july_panel

PROVENANCE = {"source_url": "https://example.org/verified/august.csv", "sha256": "a" * 64}


def fixtures():
    full = pd.date_range("2024-07-01T07:00:00Z", periods=744, freq="h")
    boundary = pd.date_range("2024-08-01T00:00:00Z", periods=7, freq="h")
    units = [("141", "1"), ("141", "7"), ("55129", "DBG1"), ("147", "K-7")]
    epa = pd.concat([
        pd.DataFrame({"facility_id": plant, "unit_id": unit,
                      "timestamp_utc": full, "era5_july_hour_matched": [True] * 737 + [False] * 7,
                      "temperature_2m_c": [36.] * 737 + [float("nan")] * 7})
        for plant, unit in units], ignore_index=True)
    weather = pd.concat([
        pd.DataFrame({"plant_id": plant, "timestamp_utc": boundary,
                      "temperature_2m_c": [40., 39., 38., 37., 36., 35., 34.]})
        for plant in ("141", "55129", "147")], ignore_index=True)
    return epa, weather


def test_completes_744_only_from_actual_august_observations():
    panel, weather = fixtures()
    completed, summary, manifest = complete_july_panel(panel, weather, PROVENANCE)
    assert len(completed) == 4 * 744
    assert summary.jul_utc_source_matched.eq(737).all()
    assert summary.aug_utc_observed_boundary_matched.eq(7).all()
    assert summary.complete_matched_hours.eq(744).all()
    assert completed.era5_full_local_july_matched.all()
    assert completed.loc[completed.era5_august_boundary_matched, "temperature_2m_c"].notna().all()
    assert not manifest["weather_interpolation_or_imputation_used"]
    assert not manifest["thermal_derating_identified"]


def test_rejects_missing_boundary_hour():
    panel, weather = fixtures()
    with pytest.raises(ValueError, match="precisely"):
        complete_july_panel(panel, weather.iloc[:-1], PROVENANCE)


def test_rejects_duplicate_boundary_hour():
    panel, weather = fixtures()
    with pytest.raises(ValueError, match="Duplicate actual August"):
        complete_july_panel(panel, pd.concat([weather, weather.iloc[[0]]]), PROVENANCE)


def test_rejects_unverified_july_calendar():
    panel, weather = fixtures()
    with pytest.raises(ValueError, match="Unverified local-July"):
        complete_july_panel(panel.iloc[:-1], weather, PROVENANCE)


def test_rejects_backfilled_july_weather():
    panel, weather = fixtures()
    panel.loc[737, "temperature_2m_c"] = 40.
    with pytest.raises(ValueError, match="already been filled"):
        complete_july_panel(panel, weather, PROVENANCE)


def test_rejects_missing_source_provenance():
    panel, weather = fixtures()
    with pytest.raises(ValueError, match="provenance"):
        complete_july_panel(panel, weather, {})
