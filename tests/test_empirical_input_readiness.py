import pandas as pd
import pytest
from grid_resilience.empirical_input_readiness import assess

REQUIRED=("demand_hourly","capacity_technology","availability_hourly",
          "observed_generation_monthly","ba_transfer_capacity")
def test_assumed_transfer_is_not_empirically_ready(tmp_path):
    p=tmp_path/"provenance.csv"
    pd.DataFrame([{"dataset":name,"source_url":"https://example.org/test",
        "source_year":"2024","measurement_basis":"synthetic fixture",
        "status":"assumed" if name=="ba_transfer_capacity" else "official_observed"}
        for name in REQUIRED]).to_csv(p,index=False)
    manifest=assess(p,tmp_path/"out")
    assert manifest["empirical_input_readiness"] is False
    assert manifest["unverified_datasets"]==["ba_transfer_capacity"]
    assert manifest["historical_calibration_certified"] is False

def test_missing_required_input_rejected(tmp_path):
    p=tmp_path/"missing.csv"
    pd.DataFrame([{"dataset":"demand_hourly","source_url":"x",
                  "source_year":"2024","measurement_basis":"test",
                  "status":"synthetic"}]).to_csv(p,index=False)
    with pytest.raises(ValueError,match="Missing required"):
        assess(p,tmp_path/"out")
