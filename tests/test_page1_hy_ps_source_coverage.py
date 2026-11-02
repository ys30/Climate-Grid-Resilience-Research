import pandas as pd
from grid_resilience.page1_hy_ps_source_coverage import audit

def test_source_grains_not_mixed():
    sample=pd.DataFrame([
      {"plant_id":"1","ba":"SRP","prime_mover":"HY","period":"2024-01","net_generation_mwh":11},
      {"plant_id":"2","ba":"SRP","prime_mover":"PS","period":"2024-01","net_generation_mwh":-3}])
    t,m=audit(sample)
    assert m["observed_month_slots"]==2
    assert m["missing_page1_month_slots"]==22
    jan=t.loc[t.period.eq("2024-01")]
    assert set(jan.coverage_status)=={"observed_page1_rows"}
    assert float(jan.observed_net_mwh.sum())==8
    assert t.loc[t.period.eq("2024-02"),"observed_net_mwh"].isna().all()
