import pandas as pd
import pytest
from grid_resilience.year_scoped_plant_ba import aggregate

def fixtures(tmp_path):
    g = tmp_path / "generation.csv"
    x = tmp_path / "crosswalk.csv"
    pd.DataFrame([
        {"plant_id": "123", "period": "2023-07", "technology": "wind", "generation_mwh": 10},
        {"plant_id": "123", "period": "2024-07", "technology": "wind", "generation_mwh": 20}
    ]).to_csv(g, index=False)
    pd.DataFrame([
        {"plant_id": "123", "source_year": "2023", "technology": "wind", "ba": "CISO", "mapping_source": "fixture"},
        {"plant_id": "123", "source_year": "2024", "technology": "wind", "ba": "AZPS", "mapping_source": "fixture"}
    ]).to_csv(x, index=False)
    return g, x

def test_year_scoped_mapping_switches_ba(tmp_path):
    g, x = fixtures(tmp_path)
    result = aggregate(g, x, tmp_path / "out")
    out = pd.read_csv(tmp_path / "out" / "observed_ba_technology_month.csv")
    assert set(zip(out.period, out.ba)) == {("2023-07", "CISO"), ("2024-07", "AZPS")}
    assert result["historical_calibration_certified"] is False

def test_missing_year_fails_closed(tmp_path):
    g, x = fixtures(tmp_path)
    pd.read_csv(x).iloc[:1].to_csv(x, index=False)
    with pytest.raises(ValueError, match="Missing year-specific"):
        aggregate(g, x, tmp_path / "out")

def test_conflicting_year_mapping_rejected(tmp_path):
    g, x = fixtures(tmp_path)
    data = pd.read_csv(x, dtype=str)
    dup = data.iloc[[1]].copy()
    dup["ba"] = "CISO"
    pd.concat([data, dup]).to_csv(x, index=False)
    with pytest.raises(ValueError, match="Ambiguous"):
        aggregate(g, x, tmp_path / "out")
