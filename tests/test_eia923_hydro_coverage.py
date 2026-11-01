import pandas as pd
import pytest
from grid_resilience.eia923_hydro_coverage import audit

def test_missing_distinct_from_observed_zero_and_negative_ps(tmp_path):
    inp = tmp_path / "source.csv"
    pd.DataFrame([
        {"reported_ba": "AZPS", "prime_mover": "HY", "period": "2024-02",
         "net_generation_mwh": 0, "generator_month_records": 3},
        {"reported_ba": "BPAT", "prime_mover": "PS", "period": "2024-02",
         "net_generation_mwh": -20, "generator_month_records": 2},
    ]).to_csv(inp, index=False)
    m = audit(inp, tmp_path / "out")
    x = pd.read_csv(tmp_path / "out" / "hydro_ps_coverage_2024.csv")
    assert len(x) == 96
    assert m["observed_slots"] == 2
    assert m["missing_slots"] == 94
    assert m["observed_zero_generation_slots"] == 1
    az = x[(x.reported_ba == "AZPS") & (x.prime_mover == "HY")]
    assert az[az.period == "2024-02"].iloc[0].net_generation_mwh == 0
    assert az[az.period == "2024-03"].iloc[0].coverage_status == "missing_record"
    assert pd.isna(az[az.period == "2024-03"].iloc[0].net_generation_mwh)
    ps = x[(x.reported_ba == "BPAT") & (x.prime_mover == "PS") & (x.period == "2024-02")]
    assert ps.iloc[0].net_generation_mwh == -20
    assert m["historical_calibration_certified"] is False

def test_duplicate_source_category_rejected(tmp_path):
    inp = tmp_path / "source.csv"
    row = {"reported_ba": "AZPS", "prime_mover": "HY", "period": "2024-02",
           "net_generation_mwh": 1, "generator_month_records": 1}
    pd.DataFrame([row, row]).to_csv(inp, index=False)
    with pytest.raises(ValueError, match="duplicate"):
        audit(inp, tmp_path / "out")

def test_no_hydro_rows_still_outputs_missing_not_zero(tmp_path):
    inp = tmp_path / "source.csv"
    pd.DataFrame([{"reported_ba": "CISO", "prime_mover": "CT", "period": "2024-02",
                   "net_generation_mwh": 5, "generator_month_records": 1}]).to_csv(inp, index=False)
    m = audit(inp, tmp_path / "out")
    assert m["observed_slots"] == 0 and m["missing_slots"] == 96
