import pandas as pd
import pytest
from grid_resilience.calibration_pipeline import run

def inputs(tmp_path):
    ts = pd.date_range("2024-02-01", periods=29*24, freq="h", tz="UTC")
    hourly = tmp_path/"hourly.csv"
    observed = tmp_path/"observed.csv"
    pd.DataFrame([{"timestamp":t.isoformat(),"ba":"CISO","technology":"wind","generation_mwh":2.0}
                  for t in ts]).to_csv(hourly,index=False)
    pd.DataFrame([{"ba":"CISO","technology":"wind","period":"2024-02","generation_mwh":1392.0}]).to_csv(observed,index=False)
    return hourly, observed

def test_partial_fleet_diagnostic_is_never_calibration_certified(tmp_path):
    h,o=inputs(tmp_path)
    manifest=run(h,o,tmp_path/"out",allow_partial_fleet=True)
    assert manifest["comparison_rows"]==1
    assert manifest["historical_calibration_certified"] is False

def test_full_fleet_gate_rejects_wind_only(tmp_path):
    h,o=inputs(tmp_path)
    with pytest.raises(ValueError,match="Full fleet gate"):
        run(h,o,tmp_path/"out")

def test_partial_month_rejected_before_comparison(tmp_path):
    h,o=inputs(tmp_path)
    pd.read_csv(h).iloc[:-1].to_csv(h,index=False)
    with pytest.raises(ValueError,match="Incomplete calendar month"):
        run(h,o,tmp_path/"out",allow_partial_fleet=True)

def test_generic_proxy_rejected(tmp_path):
    h,o=inputs(tmp_path)
    df=pd.read_csv(h)
    df["technology"]="generic_thermal_proxy"
    df.to_csv(h,index=False)
    with pytest.raises(ValueError,match="proxy"):
        run(h,o,tmp_path/"out",allow_partial_fleet=True)
