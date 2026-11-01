import json
import pandas as pd
from grid_resilience.historical_hydro_comparison_gate import run
from grid_resilience.hydro_calibration_readiness import REQUIRED_OBS, REQUIRED_MODEL

def fixture_inputs(tmp_path, verified):
    obs=tmp_path/"observed.csv";mod=tmp_path/"modeled.csv"
    op=tmp_path/"observation_provenance.json";mp=tmp_path/"model_provenance.json"
    pd.DataFrame([{"reported_ba":"BPAT","prime_mover":"HY","period":"2024-02",
                   "net_generation_mwh":100,"coverage_status":"observed_source_rows"}]).to_csv(obs,index=False)
    pd.DataFrame([{"ba":"BPAT","technology":"hydro","period":"2024-02",
                   "generation_mwh":110}]).to_csv(mod,index=False)
    op.write_text(json.dumps({key:verified for key in REQUIRED_OBS}))
    mp.write_text(json.dumps({key:verified for key in REQUIRED_MODEL}))
    return obs,mod,op,mp

def test_unverified_inputs_block_fit_and_no_metrics_written(tmp_path):
    result=run(*fixture_inputs(tmp_path,False),tmp_path/"out")
    assert result["status"]=="blocked_unverified_historical_inputs"
    assert result["comparison_performed"] is False
    assert not (tmp_path/"out"/"comparison").exists()
    assert not result["historical_adequacy_validation_certified"]

def test_explicitly_verified_fixture_calculates_diagnostic_not_adequacy(tmp_path):
    result=run(*fixture_inputs(tmp_path,True),tmp_path/"out")
    assert result["status"]=="generation_fit_diagnostic_computed"
    assert result["matched_observed_cells"]==1
    assert result["historical_adequacy_validation_certified"] is False
    metrics=pd.read_csv(tmp_path/"out"/"comparison"/"monthly_hydro_model_error_metrics.csv")
    assert metrics.mae_mwh.iloc[0]==10
