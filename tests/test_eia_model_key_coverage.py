import pandas as pd
from grid_resilience.eia_model_key_coverage import audit

def test_missing_coal_not_imputed_zero(tmp_path):
    obs=tmp_path/"obs.csv";model=tmp_path/"model.csv"
    pd.DataFrame([{"ba":"CISO","technology":"wind","period":"2024-07","generation_mwh":12}]).to_csv(obs,index=False)
    pd.DataFrame([
      {"ba":"CISO","technology":"wind","period":"2024-07","generation_mwh":10},
      {"ba":"CISO","technology":"coal","period":"2024-07","generation_mwh":4}
    ]).to_csv(model,index=False)
    result=audit(obs,model,tmp_path/"out")
    assert result["status_counts"]=={"matched":1,"modeled_only":1,"observed_only":0}
    assert not result["comparison_complete"]
    x=pd.read_csv(tmp_path/"out"/"comparison_key_coverage.csv")
    coal=x[x.technology=="coal"].iloc[0]
    assert pd.isna(coal.generation_mwh_observed)
