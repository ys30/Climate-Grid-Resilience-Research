import pandas as pd
from grid_resilience.eia_monthly_coverage_profile import profile

def test_missing_month_kept_missing_not_zero(tmp_path):
    source=tmp_path/"candidates.csv"
    pd.DataFrame([{"ba":"CISO","technology":"wind","period":"2024-07","generation_mwh":0}]).to_csv(source,index=False)
    result=profile(source,tmp_path/"out")
    assert result["missing_cells"]==11
    x=pd.read_csv(tmp_path/"out"/"candidate_monthly_coverage_matrix.csv")
    assert not bool(x.loc[x.period=="2024-06","record_present"].iloc[0])
    assert pd.isna(x.loc[x.period=="2024-06","generation_mwh"].iloc[0])
    assert x.loc[x.period=="2024-07","generation_mwh"].iloc[0]==0
