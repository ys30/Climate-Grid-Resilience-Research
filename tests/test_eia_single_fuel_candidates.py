import pandas as pd
from grid_resilience.eia_single_fuel_candidates import build

def test_only_clean_single_fuel_is_aggregated(tmp_path):
    a=tmp_path/"923.csv";b=tmp_path/"860.csv"
    pd.DataFrame([
        {"plant_id":"1","generator_id":"A","reported_ba":"CISO","period":"2024-07","generation_mwh":10,"prime_mover":"CT"},
        {"plant_id":"2","generator_id":"B","reported_ba":"CISO","period":"2024-07","generation_mwh":20,"prime_mover":"CT"},
        {"plant_id":"3","generator_id":"C","reported_ba":"CISO","period":"2024-07","generation_mwh":30,"prime_mover":"CT"},
    ]).to_csv(a,index=False)
    pd.DataFrame([
        {"plant_id":"1","generator_id":"A","energy_source_1":"NG","energy_source_2":"","multiple_fuels":"N","prime_mover":"CT","reported_technology":"Natural Gas"},
        {"plant_id":"2","generator_id":"B","energy_source_1":"NG","energy_source_2":"DFO","multiple_fuels":"Y","prime_mover":"CT","reported_technology":"Natural Gas"},
    ]).to_csv(b,index=False)
    m=build(a,b,tmp_path/"out")
    x=pd.read_csv(tmp_path/"out"/"observed_single_fuel_candidate_ba_technology_month.csv")
    assert m["included_candidate_records"]==1
    assert m["excluded_records"]==2
    assert x.generation_mwh.iloc[0]==10
    assert x.technology.iloc[0]=="gas"
    assert m["historical_calibration_certified"] is False
