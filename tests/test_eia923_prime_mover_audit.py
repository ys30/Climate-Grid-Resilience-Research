import pandas as pd
import pytest
from grid_resilience.eia923_prime_mover_audit import audit

def test_preserves_negative_and_zero_without_fuel_assumption(tmp_path):
    p=tmp_path/"data.csv"
    pd.DataFrame([
      {"plant_id":"001","generator_id":"A","prime_mover":"ST","reported_ba":"CISO","period":"2024-07","generation_mwh":-5},
      {"plant_id":"002","generator_id":"B","prime_mover":"ST","reported_ba":"CISO","period":"2024-07","generation_mwh":0},
      {"plant_id":"003","generator_id":"C","prime_mover":"ST","reported_ba":"CISO","period":"2024-07","generation_mwh":9},
    ]).to_csv(p,index=False)
    result=audit(p,tmp_path/"out")
    x=pd.read_csv(tmp_path/"out"/"ba_prime_mover_month_audit.csv")
    assert x.net_generation_mwh.iloc[0]==4
    assert x.negative_net_mwh.iloc[0]==-5
    assert result["technology_mapping_certified"] is False

def test_rejects_duplicate_generator_month(tmp_path):
    p=tmp_path/"data.csv"
    row={"plant_id":"1","generator_id":"A","prime_mover":"ST","reported_ba":"CISO","period":"2024-07","generation_mwh":10}
    pd.DataFrame([row,row]).to_csv(p,index=False)
    with pytest.raises(ValueError,match="Duplicate"):
        audit(p,tmp_path/"out")
