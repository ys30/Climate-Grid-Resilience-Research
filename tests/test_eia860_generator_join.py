import pandas as pd
import pytest
from grid_resilience.eia860_generator_join import join

def files(tmp_path, fuel="NG"):
    a=tmp_path/"923.csv";b=tmp_path/"860.csv"
    pd.DataFrame([{"plant_id":"001","generator_id":"G1","reported_ba":"CISO",
       "period":"2024-07","prime_mover":"CT","generation_mwh":-3}]).to_csv(a,index=False)
    pd.DataFrame([{"plant_id":"001","generator_id":"G1",
       "energy_source_1":fuel,"prime_mover":"CT"}]).to_csv(b,index=False)
    return a,b

def test_exact_match_preserves_negative_net_generation(tmp_path):
    a,b=files(tmp_path)
    m=join(a,b,tmp_path/"out")
    out=pd.read_csv(tmp_path/"out"/"observed_ba_technology_month.csv")
    assert out.technology.iloc[0]=="gas"
    assert out.generation_mwh.iloc[0]==-3
    assert m["historical_calibration_certified"] is False

def test_unknown_fuel_fails_closed(tmp_path):
    a,b=files(tmp_path,"XXX")
    with pytest.raises(ValueError,match="Unresolved"):
        join(a,b,tmp_path/"out")
def test_unmatched_generator_fails_closed(tmp_path):
    a,b=files(tmp_path)
    d=pd.read_csv(b,dtype=str);d.loc[0,"generator_id"]="G2";d.to_csv(b,index=False)
    with pytest.raises(ValueError,match="Unresolved"):
        join(a,b,tmp_path/"out")
