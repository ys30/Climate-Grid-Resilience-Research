"""Smoke-test actual SRP figure rendering with synthetic inputs only."""
from pathlib import Path

import pytest

from grid_resilience.srp_hourly_figures import prepare
from grid_resilience.plot_srp_adequacy import render


def test_png_figures_from_synthetic_168_hour_data(tmp_path: Path):
    pd = pytest.importorskip("pandas")
    pytest.importorskip("matplotlib")
    times = pd.date_range("2024-07-01", periods=168, freq="h", tz="UTC")
    raw = pd.DataFrame({
        "case": ["synthetic_c100_n100_g40"] * 168,
        "timestamp": times,
        "demand_mw": [120 + i % 24 for i in range(168)],
        "assumed_solar_availability_pu": [0.0 if i % 24 < 8 else 0.6 for i in range(168)],
        "shortfall_mw": [2.0 if i % 24 == 20 else 0.0 for i in range(168)],
    })
    hourly, diurnal = prepare(raw)
    hourly_path = tmp_path / "hourly.csv"
    diurnal_path = tmp_path / "diurnal.csv"
    hourly.to_csv(hourly_path, index=False)
    diurnal.to_csv(diurnal_path, index=False)
    render(hourly_path, diurnal_path, tmp_path / "figures")
    images = sorted((tmp_path / "figures").glob("*.png"))
    assert len(images) == 2
    assert all(image.stat().st_size > 1000 for image in images)


def test_figure_renderer_rejects_energy_mismatch(tmp_path: Path):
    pd = pytest.importorskip("pandas")
    pytest.importorskip("matplotlib")
    times = pd.date_range("2024-07-01", periods=168, freq="h", tz="UTC")
    raw = pd.DataFrame({
        "case": ["synthetic"] * 168,
        "timestamp": times, "demand_mw": [100.] * 168,
        "assumed_solar_availability_pu": [0.5] * 168,
        "shortfall_mw": [1.] * 168,
    })
    hourly, diurnal = prepare(raw)
    diurnal.loc[0, "shortfall_mwh"] += 10
    h = tmp_path / "hourly.csv"
    d = tmp_path / "diurnal.csv"
    hourly.to_csv(h, index=False)
    diurnal.to_csv(d, index=False)
    with pytest.raises(ValueError, match="disagree"):
        render(h, d, tmp_path / "figures")


def test_figure_renderer_rejects_duplicate_utc_bins(tmp_path: Path):
    pd = pytest.importorskip("pandas")
    pytest.importorskip("matplotlib")
    times = pd.date_range("2024-07-01", periods=168, freq="h", tz="UTC")
    raw = pd.DataFrame({
        "case": ["synthetic"] * 168, "timestamp": times,
        "demand_mw": [100.] * 168,
        "assumed_solar_availability_pu": [0.5] * 168,
        "shortfall_mw": [0.] * 168,
    })
    hourly, diurnal = prepare(raw)
    diurnal.loc[0, "hour_utc"] = diurnal.loc[1, "hour_utc"]
    h, d = tmp_path / "hourly.csv", tmp_path / "diurnal.csv"
    hourly.to_csv(h, index=False)
    diurnal.to_csv(d, index=False)
    with pytest.raises(ValueError, match="UTC hour-of-day bins"):
        render(h, d, tmp_path / "figures")
