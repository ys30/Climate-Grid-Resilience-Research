import pandas as pd
import pytest
from grid_resilience.eia923_page1_ps_reconciliation import reconcile

def test_ps_coverage_preserves_missing_zero_and_negative(tmp_path):
    p=tmp_path/"ps.csv"
    pd.DataFrame([
      {"plant_id":"1","reported_ba":"BPAT","prime_mover":"PS","period":"2024-02","net_generation_mwh":-12},
      {"plant_id":"2","reported_ba":"BPAT","prime_mover":"PS","period":"2024-02","net_generation_mwh":0},
      {"plant_id":"3","reported_ba":"CISO","prime_mover":"PS","period":"2024-03","net_generation_mwh":4}
    ]).to_csv(p,index=False)
    m=reconcile(p,tmp_path/"out")
    x=pd.read_csv(tmp_path/"out"/"page1_ps_ba_month_2024.csv")
    assert len(x)==48 and m["observed_ba_months"]==2 and m["missing_ba_months"]==46
    b=x[(x.reported_ba=="BPAT")&(x.period=="2024-02")].iloc[0]
    assert b.net_generation_mwh==-12 and b.zero_plant_rows==1 and b.negative_plant_rows==1
    missing=x[(x.reported_ba=="AZPS")&(x.period=="2024-02")].iloc[0]
    assert missing.coverage_status=="missing_source_rows" and pd.isna(missing.net_generation_mwh)
    assert m["historical_calibration_certified"] is False

def test_duplicate_plant_month_rejected(tmp_path):
    p=tmp_path/"ps.csv"
    row={"plant_id":"1","reported_ba":"BPAT","prime_mover":"PS","period":"2024-02","net_generation_mwh":1}
    pd.DataFrame([row,row]).to_csv(p,index=False)
    with pytest.raises(ValueError,match="Duplicate"):
        reconcile(p,tmp_path/"out")
