import pandas as pd
import pytest
from grid_resilience.screening_gate import assess

def fixtures(tmp_path):
    bas = ["CISO", "AZPS"]
    dispatch = pd.DataFrame([
        {"scenario": s, "ba": ba, "unserved_energy_mwh": 10 if s == "baseline" else 20}
        for s in ["baseline", "heat_only", "wind_only", "heat_wind"] for ba in bas
    ])
    capacity = pd.DataFrame([{"ba": ba, "gas_mw": 80, "wind_mw": 20} for ba in bas])
    excluded = pd.DataFrame([{"ba": ba, "technology": "solar", "capacity_mw": 100} for ba in bas])
    paths = [tmp_path / name for name in ("dispatch.csv", "capacity.csv", "excluded.csv")]
    for frame, path in zip((dispatch, capacity, excluded), paths):
        frame.to_csv(path, index=False)
    return paths

def test_blocks_unvalidated_partial_fleet(tmp_path):
    paths = fixtures(tmp_path)
    result = assess(*paths, tmp_path / "gate.json")
    assert result["excluded_nameplate_fraction"] == pytest.approx(0.5)
    assert result["baseline_unserved_energy_mwh"] == 20
    assert result["baseline_energy_fraction"] is None
    assert result["pass_for_historical_reliability_claims"] is False
    assert len(result["blocking_reasons"]) >= 3

def test_rejects_incomplete_factorial(tmp_path):
    paths = fixtures(tmp_path)
    d = pd.read_csv(paths[0]).iloc[:-1]
    d.to_csv(paths[0], index=False)
    with pytest.raises(ValueError, match="Incomplete factorial"):
        assess(*paths, tmp_path / "gate.json")

def test_rejects_negative_excluded(tmp_path):
    paths = fixtures(tmp_path)
    d = pd.read_csv(paths[2])
    d.loc[0, "capacity_mw"] = -1
    d.to_csv(paths[2], index=False)
    with pytest.raises(ValueError, match="negative"):
        assess(*paths, tmp_path / "gate.json")


def test_baseline_fraction_with_demand(tmp_path):
    paths = fixtures(tmp_path)
    demand = pd.DataFrame([
        {"timestamp": f"2024-07-01T{hour:02d}:00:00Z", "ba": ba, "demand_mw": 100}
        for hour in range(2) for ba in ["CISO", "AZPS"]
    ])
    demand_path = tmp_path / "demand.csv"
    demand.to_csv(demand_path, index=False)
    result = assess(*paths, tmp_path / "gate.json", demand_csv=demand_path)
    assert result["baseline_energy_fraction"] == pytest.approx(0.05)
    assert any("Baseline shortage fraction exceeds" in x for x in result["blocking_reasons"])

def test_rejects_missing_demand_hour(tmp_path):
    paths = fixtures(tmp_path)
    demand = pd.DataFrame([
        {"timestamp": f"2024-07-01T{hour:02d}:00:00Z", "ba": ba, "demand_mw": 100}
        for hour in range(2) for ba in ["CISO", "AZPS"]
    ]).iloc[:-1]
    demand_path = tmp_path / "demand.csv"
    demand.to_csv(demand_path, index=False)
    with pytest.raises(ValueError, match="Incomplete hourly demand panel"):
        assess(*paths, tmp_path / "gate.json", demand_csv=demand_path)
