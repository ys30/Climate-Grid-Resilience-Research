import pandas as pd
import pytest
from grid_resilience.hydro_monthly_model_comparison import compare

def test_monthly_error_and_missing_exclusion(tmp_path):
    obs=tmp_path/"obs.csv";mod=tmp_path/"model.csv"
    pd.DataFrame([
        {"reported_ba":"BPAT","prime_mover":"HY","period":"2024-01","net_generation_mwh":10,"coverage_status":"observed_source_rows"},
        {"reported_ba":"BPAT","prime_mover":"HY","period":"2024-02","net_generation_mwh":20,"coverage_status":"observed_source_rows"},
        {"reported_ba":"AZPS","prime_mover":"HY","period":"2024-01","net_generation_mwh":"","coverage_status":"missing_source_rows"}
    ]).to_csv(obs,index=False)
    pd.DataFrame([
        {"reported_ba":"BPAT","prime_mover":"HY","period":"2024-01","modeled_net_generation_mwh":12},
        {"reported_ba":"BPAT","prime_mover":"HY","period":"2024-02","modeled_net_generation_mwh":18}
    ]).to_csv(mod,index=False)
    report=compare(obs,mod,tmp_path/"out")
    metric=pd.read_csv(tmp_path/"out"/"monthly_hydro_model_error_metrics.csv").iloc[0]
    assert report["matched_observed_cells"]==2
    assert report["unobserved_source_cells_excluded"]==1
    assert metric.mae_mwh==2 and metric.bias_mwh==0 and metric.rmse_mwh==2
    assert report["historical_calibration_certified"] is False

def test_requires_full_model_coverage(tmp_path):
    obs=tmp_path/"obs.csv";mod=tmp_path/"model.csv"
    pd.DataFrame([{"reported_ba":"CISO","prime_mover":"PS","period":"2024-04",
                   "net_generation_mwh":5,"coverage_status":"observed_source_rows"}]).to_csv(obs,index=False)
    pd.DataFrame(columns=["reported_ba","prime_mover","period","modeled_net_generation_mwh"]).to_csv(mod,index=False)
    with pytest.raises(ValueError,match="does not cover"):
        compare(obs,mod,tmp_path/"out")
