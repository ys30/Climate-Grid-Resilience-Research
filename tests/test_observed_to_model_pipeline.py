import pandas as pd
import pytest
from grid_resilience.observed_to_model_pipeline import run

def inputs(tmp_path):
    observed = tmp_path/"obs.csv"
    expected = tmp_path/"expected.csv"
    crosswalk = tmp_path/"crosswalk.csv"
    model = tmp_path/"model.csv"
    pd.DataFrame([{"plant_id":"123","technology":"wind","period":"2024-02",
                   "generation_mwh":696.0,"source_file":"synthetic_fixture",
                   "reporting_basis":"net"}]).to_csv(observed,index=False)
    pd.DataFrame([{"plant_id":"123","technology":"wind","period":"2024-02"}]).to_csv(expected,index=False)
    pd.DataFrame([{"plant_id":"123","technology":"wind","source_year":"2024",
                   "ba":"CISO","mapping_source":"synthetic_fixture"}]).to_csv(crosswalk,index=False)
    times=pd.date_range("2024-02-01",periods=29*24,freq="h",tz="UTC")
    pd.DataFrame([{"timestamp":t.isoformat(),"ba":"CISO",
                   "technology":"wind","generation_mwh":1.0}
                  for t in times]).to_csv(model,index=False)
    return observed,expected,crosswalk,model

def test_end_to_end_synthetic_audit(tmp_path):
    paths=inputs(tmp_path)
    result=run(*paths,tmp_path/"out",allow_partial_fleet=True)
    assert result["historical_calibration_certified"] is False
    assert result["generation_comparison"]["comparison_rows"]==1
    assert result["generation_comparison"]["historical_calibration_certified"] is False

def test_missing_observation_fails_before_mapping(tmp_path):
    paths=inputs(tmp_path)
    e=pd.read_csv(paths[1],dtype=str)
    e.loc[len(e)]=["999","wind","2024-02"]
    e.to_csv(paths[1],index=False)
    with pytest.raises(ValueError,match="coverage mismatch"):
        run(*paths,tmp_path/"out",allow_partial_fleet=True)
