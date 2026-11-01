import pandas as pd
import pytest
from grid_resilience.eia923_hy_ps_monthly import combine

def test_combined_coverage_not_zero_filled(tmp_path):
    hy=tmp_path/"hy.csv";ps=tmp_path/"ps.csv"
    pd.DataFrame([{"plant_id":"1","reported_ba":"BPAT","prime_mover":"HY","period":"2024-02","net_generation_mwh":-5},
                  {"plant_id":"2","reported_ba":"BPAT","prime_mover":"HY","period":"2024-02","net_generation_mwh":0}]).to_csv(hy,index=False)
    pd.DataFrame([{"plant_id":"3","reported_ba":"CISO","prime_mover":"PS","period":"2024-02","net_generation_mwh":8}]).to_csv(ps,index=False)
    m=combine(hy,ps,tmp_path/"out")
    df=pd.read_csv(tmp_path/"out"/"eia923_hy_ps_ba_month_observed_2024.csv")
    assert len(df)==96 and m["observed_slots"]==2 and m["missing_slots"]==94
    hyrow=df[(df.reported_ba=="BPAT")&(df.prime_mover=="HY")&(df.period=="2024-02")].iloc[0]
    assert hyrow.net_generation_mwh==-5 and hyrow.zero_plant_month_rows==1
    assert pd.isna(df[(df.reported_ba=="AZPS")&(df.prime_mover=="PS")].iloc[0].net_generation_mwh)
    assert m["historical_calibration_certified"] is False

def test_rejects_cross_technology_mislabel(tmp_path):
    hy=tmp_path/"hy.csv";ps=tmp_path/"ps.csv"
    pd.DataFrame([{"plant_id":"1","reported_ba":"BPAT","prime_mover":"PS","period":"2024-02","net_generation_mwh":2}]).to_csv(hy,index=False)
    pd.DataFrame(columns=["plant_id","reported_ba","prime_mover","period","net_generation_mwh"]).to_csv(ps,index=False)
    with pytest.raises(ValueError,match="Unexpected HY"):
        combine(hy,ps,tmp_path/"out")
