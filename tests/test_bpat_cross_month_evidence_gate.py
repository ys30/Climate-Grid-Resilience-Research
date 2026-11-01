import pandas as pd
import pytest
from grid_resilience.bpat_cross_month_evidence_gate import audit

def fixture(tmp_path):
    p=tmp_path/"months.csv"
    pd.DataFrame([
        {"month":"2024-02","hours":696,"pearson_r":0.8934,"mae_pu":0.0748,"rmse_pu":0.1096,"mean_bias_pu":-0.0527,"ci_run":41227782144},
        {"month":"2024-03","hours":744,"pearson_r":0.9045,"mae_pu":0.0865,"rmse_pu":0.1253,"mean_bias_pu":-0.0823,"ci_run":41238968791},
        {"month":"2024-07","hours":737,"pearson_r":0.8644,"mae_pu":0.1025,"rmse_pu":0.141,"mean_bias_pu":-0.0957,"ci_run":41254992133}
    ]).to_csv(p,index=False)
    return p

def test_all_three_months_flag_amplitude_mismatch_without_calibration(tmp_path):
    report=audit(fixture(tmp_path),tmp_path/"out")
    assert report["all_months_high_shape_correlation"]
    assert report["months_with_gt_5pp_amplitude_bias"]==["2024-02","2024-03","2024-07"]
    assert report["calibration_certified"] is False
    result=pd.read_csv(tmp_path/"out"/"bpat_cross_month_shape_amplitude_audit.csv")
    assert result.shape[0]==3
    assert result.shape_amplitude_mismatch.all()

def test_duplicate_months_rejected(tmp_path):
    p=fixture(tmp_path)
    d=pd.read_csv(p)
    d.loc[2,"month"]="2024-03"
    d.to_csv(p,index=False)
    with pytest.raises(ValueError,match="Expected February March July"):
        audit(p,tmp_path/"out")

def test_invalid_correlation_rejected(tmp_path):
    p=fixture(tmp_path)
    d=pd.read_csv(p);d.loc[0,"pearson_r"]=1.2;d.to_csv(p,index=False)
    with pytest.raises(ValueError,match="Invalid error"):
        audit(p,tmp_path/"out")
