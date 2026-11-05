import pandas as pd
import pytest
from grid_resilience.srp_epa_era5_eia930_demand_context import summarize


def fixture():
    epatime = pd.date_range("2024-07-01T07:00:00Z", periods=744, freq="h")
    epa = pd.concat([pd.DataFrame({
        "facility_id": site, "unit_id": unit, "timestamp_utc": epatime,
        "temperature_2m_c": [34.] * 300 + [37.] * 300 + [41.] * 144,
        "era5_full_local_july_matched": True})
        for site, unit in [("141", "1"), ("141", "7"), ("55129", "DBG1"), ("147", "K-7")]],
        ignore_index=True)
    eia = pd.DataFrame({
        "UTC Time at End of Hour": pd.date_range("2024-07-01T01:00:00Z", periods=744, freq="h").strftime("%m/%d/%Y %I:%M:%S %p"),
        "Balancing Authority": "SRP", "Demand (MW)": 3000.})
    return epa, eia


def test_conserve_737_utc_july_and_seven_true_august_boundary():
    panel, eia = fixture()
    joined, summary, manifest = summarize(panel, eia)
    assert len(joined) == 3 * 744
    assert joined.groupby("facility_id").srp_demand_source_matched.sum().eq(737).all()
    assert summary.groupby("facility_id").unique_site_weather_hours.sum().eq(737).all()
    assert manifest["utc_august_boundary_hours_per_plant_unmatched_to_july_eia930"] == 7
    assert not manifest["thermal_derating_calibrated"]


def test_shared_site_weather_not_duplicated():
    joined, summary, _ = summarize(*fixture())
    assert joined.loc[joined.facility_id.eq("141")].shape[0] == 744


def test_reject_incomplete_official_930():
    p, e = fixture()
    with pytest.raises(ValueError, match="Incomplete or duplicate official"):
        summarize(p, e.iloc[:-1])


def test_reject_missing_demand_no_zero_fill():
    p, e = fixture()
    e.loc[10, "Demand (MW)"] = None
    with pytest.raises(ValueError, match="Missing or invalid official"):
        summarize(p, e)


def test_reject_duplicate_site_utc_weather():
    p, e = fixture()
    p.loc[744, "temperature_2m_c"] = 42.
    with pytest.raises(ValueError, match="disagree on temperature"):
        summarize(p, e)


def test_reject_partial_epa_hour_calendar():
    p, e = fixture()
    with pytest.raises(ValueError, match="Incomplete EPA local-July"):
        summarize(p.iloc[:-1], e)
