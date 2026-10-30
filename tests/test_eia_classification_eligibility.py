import pandas as pd
from grid_resilience.eia_classification_eligibility import audit

def test_multifuel_unmatched_and_clean_separation(tmp_path):
    a=tmp_path/"a.csv"; b=tmp_path/"b.csv"
    pd.DataFrame([
      {"plant_id":"1","generator_id":"G1","reported_ba":"CISO","period":"2024-07","generation_mwh":20,"prime_mover":"CT"},
      {"plant_id":"2","generator_id":"G2","reported_ba":"CISO","period":"2024-07","generation_mwh":10,"prime_mover":"CT"},
      {"plant_id":"3","generator_id":"G3","reported_ba":"CISO","period":"2024-07","generation_mwh":5,"prime_mover":"CT"}
    ]).to_csv(a,index=False)
    pd.DataFrame([
      {"plant_id":"1","generator_id":"G1","energy_source_1":"NG","energy_source_2":"","multiple_fuels":"N","prime_mover":"CT","reported_technology":"Natural Gas"},
      {"plant_id":"2","generator_id":"G2","energy_source_1":"NG","energy_source_2":"DFO","multiple_fuels":"Y","prime_mover":"CT","reported_technology":"Natural Gas"}
    ]).to_csv(b,index=False)
    result=audit(a,b,tmp_path/"out")
    assert result["eligibility_counts"]=={
        "clean_single_fuel_candidate":1,"multifuel_requires_review":1,"unmatched":1
    }
