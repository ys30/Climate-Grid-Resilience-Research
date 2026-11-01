import json
import pandas as pd
import pytest
from grid_resilience.hydro_model_month_adapter import adapt

def setup_inputs(tmp_path, technology="hydro"):
    monthly=tmp_path/"monthly.csv"
    manifest=tmp_path/"coverage.json"
    pd.DataFrame([{"ba":"BPAT","technology":technology,"period":"2024-02",
                   "generation_mwh":-25.0}]).to_csv(monthly,index=False)
    manifest.write_text(json.dumps({"full_month_utc_coverage":True,
                                    "historical_calibration_certified":False}))
    return monthly,manifest

def test_adapter_keeps_synthetic_uncertified(tmp_path):
    monthly,manifest=setup_inputs(tmp_path)
    result=adapt(monthly,manifest,tmp_path/"out")
    frame=pd.read_csv(tmp_path/"out"/"modeled_hy_ps_monthly_for_comparison.csv")
    assert frame.prime_mover.tolist()==["HY"]
    assert frame.modeled_net_generation_mwh.tolist()==[-25.0]
    assert result["comparison_eligible"] is False
    assert result["historical_calibration_certified"] is False

def test_unknown_technology_fails(tmp_path):
    monthly,manifest=setup_inputs(tmp_path,"battery")
    with pytest.raises(ValueError,match="Unknown technology"):
        adapt(monthly,manifest,tmp_path/"out")

def test_missing_hour_coverage_manifest_fails(tmp_path):
    monthly,manifest=setup_inputs(tmp_path)
    manifest.write_text(json.dumps({"full_month_utc_coverage":False}))
    with pytest.raises(ValueError,match="full-calendar"):
        adapt(monthly,manifest,tmp_path/"out")
