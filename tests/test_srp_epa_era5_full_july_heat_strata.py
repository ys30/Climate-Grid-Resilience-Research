import pandas as pd
import pytest

from grid_resilience.srp_epa_era5_full_july_heat_strata import summarize


def panel():
    utc = pd.date_range("2024-07-01T07:00:00Z", periods=744, freq="h")
    rows = []
    for plant, unit in [("141", "1"), ("141", "7"), ("55129", "DBG1"), ("147", "K-7")]:
        rows.append(pd.DataFrame({
            "facility_id": plant,
            "unit_id": unit,
            "timestamp_utc": utc,
            "temperature_2m_c": [34.] * 200 + [37.] * 300 + [42.] * 244,
            "operating_time": [0.] * 100 + [1.] * 644,
            "gross_load_mw": [float("nan")] * 100 + [50.] * 644,
            "era5_full_local_july_matched": True,
        }))
    return pd.concat(rows, ignore_index=True)


def test_source_and_site_hour_conservation():
    unit, weather, meta = summarize(panel())
    assert unit.groupby(["facility_id", "epa_unit_id"]).source_hours.sum().eq(744).all()
    assert weather.groupby("facility_id").distinct_site_weather_hours.sum().eq(744).all()
    assert weather.loc[weather.facility_id.eq("141")].distinct_site_weather_hours.sum() == 744
    assert len(unit) == 12
    assert not meta["dispatch_selection_adjusted"]
    assert not meta["statistical_significance_or_causal_derating_estimated"]


def test_distinct_site_weather_counts_do_not_double_count_units():
    unit, weather, _ = summarize(panel())
    assert unit.loc[unit.facility_id.eq("141")].source_hours.sum() == 1488
    assert weather.loc[weather.facility_id.eq("141")].distinct_site_weather_hours.sum() == 744


def test_rejects_inconsistent_colocated_weather():
    x = panel()
    x.loc[744, "temperature_2m_c"] = 99.
    with pytest.raises(ValueError, match="disagree on weather"):
        summarize(x)


def test_rejects_missing_unit_hour():
    with pytest.raises(ValueError, match="Incomplete EPA"):
        summarize(panel().iloc[:-1])


def test_rejects_missing_observed_temperature():
    x = panel()
    x.loc[0, "temperature_2m_c"] = float("nan")
    with pytest.raises(ValueError, match="Missing or invalid observed ERA5"):
        summarize(x)


def test_rejects_out_of_range_operating_fraction():
    x = panel()
    x.loc[0, "operating_time"] = 1.5
    with pytest.raises(ValueError, match="operating fraction"):
        summarize(x)
