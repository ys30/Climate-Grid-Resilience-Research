import pandas as pd
import pytest
from grid_resilience.generation_calibration import compare

def setup(tmp_path):
    observed = pd.DataFrame([
        {"ba": "CISO", "technology": "wind", "period": "2024-07", "generation_mwh": 100},
        {"ba": "CISO", "technology": "wind", "period": "2024-08", "generation_mwh": 200},
    ])
    modeled = observed.copy()
    modeled["generation_mwh"] = [90, 230]
    o, m = tmp_path / "observed.csv", tmp_path / "modeled.csv"
    observed.to_csv(o, index=False)
    modeled.to_csv(m, index=False)
    return o, m

def test_comparison_metrics(tmp_path):
    o, m = setup(tmp_path)
    result = compare(o, m, tmp_path / "out")
    assert result["aggregate_bias_mwh"] == pytest.approx(20)
    assert result["aggregate_wape"] == pytest.approx(40 / 300)
    assert result["historical_calibration_certified"] is False
    assert (tmp_path / "out" / "generation_matched.csv").exists()

def test_rejects_unmatched_period(tmp_path):
    o, m = setup(tmp_path)
    df = pd.read_csv(m)
    df.loc[1, "period"] = "2024-09"
    df.to_csv(m, index=False)
    with pytest.raises(ValueError, match="Incomplete matched"):
        compare(o, m, tmp_path / "out")

def test_rejects_duplicate(tmp_path):
    o, m = setup(tmp_path)
    df = pd.read_csv(o)
    pd.concat([df, df.iloc[[0]]]).to_csv(o, index=False)
    with pytest.raises(ValueError, match="duplicate"):
        compare(o, m, tmp_path / "out")

def test_zero_observed_denominator(tmp_path):
    o, m = setup(tmp_path)
    df = pd.read_csv(o)
    df["generation_mwh"] = 0
    df.to_csv(o, index=False)
    result = compare(o, m, tmp_path / "out")
    assert result["aggregate_wape"] is None
