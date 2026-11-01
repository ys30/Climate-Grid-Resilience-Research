import pandas as pd
import pytest

from grid_resilience.srp_hourly_figures import prepare


def fixture(hours=168):
    times = pd.date_range("2024-07-01", periods=hours, freq="h", tz="UTC")
    return pd.DataFrame({
        "case": ["scenario_c100_n100_g40"] * hours,
        "timestamp": times.astype(str),
        "demand_mw": [100.0 + i % 24 for i in range(hours)],
        "assumed_solar_availability_pu": [0.0 if i % 24 < 8 else 0.5 for i in range(hours)],
        "shortfall_mw": [5.0 if i % 24 == 20 else 0.0 for i in range(hours)],
    })


def test_hourly_and_diurnal_conserve_shortfall():
    hourly, diurnal = prepare(fixture())
    assert len(hourly) == 168
    assert len(diurnal) == 24
    assert hourly.shortfall_hour.sum() == 7
    assert abs(diurnal.shortfall_mwh.sum() - 35.0) < 1e-8


def test_reject_missing_hour():
    with pytest.raises(ValueError, match="expected 168"):
        prepare(fixture().iloc[:-1])


def test_reject_duplicate_hour():
    frame = fixture()
    frame.loc[1, "timestamp"] = frame.loc[0, "timestamp"]
    with pytest.raises(ValueError, match="Duplicate"):
        prepare(frame)


def test_reject_solar_proxy_outside_bounds():
    frame = fixture()
    frame.loc[0, "assumed_solar_availability_pu"] = 1.2
    with pytest.raises(ValueError, match="Solar proxy"):
        prepare(frame)



def test_zero_shortfall_case_is_retained():
    frame = fixture()
    frame["shortfall_mw"] = 0.0
    hourly, diurnal = prepare(frame)
    assert len(hourly) == 168
    assert len(diurnal) == 24
    assert diurnal.shortfall_mwh.sum() == 0.0
    assert diurnal.shortfall_hours.sum() == 0


def test_reject_nonconsecutive_hours_even_at_correct_length():
    frame = fixture()
    frame.loc[167, "timestamp"] = "2024-07-09 00:00:00+00:00"
    with pytest.raises(ValueError, match="nonconsecutive"):
        prepare(frame)


def test_multiple_scenarios_remain_independent():
    first = fixture()
    second = fixture()
    second["case"] = "scenario_c50_n75_g60"
    second["shortfall_mw"] = 0.0
    hourly, diurnal = prepare(pd.concat([first, second], ignore_index=True))
    assert len(hourly) == 336
    assert len(diurnal) == 48
    assert hourly.groupby("case").size().eq(168).all()
    assert diurnal.groupby("case").shortfall_mwh.sum().sort_values().tolist() == [0.0, 35.0]
