import pandas as pd
import pytest
from grid_resilience.plant_ba_crosswalk import aggregate

def fixtures(tmp_path):
    g=tmp_path/"g.csv";x=tmp_path/"x.csv"
    pd.DataFrame([
        {"plant_id":"1","period":"2024-07","technology":"wind","generation_mwh":12},
        {"plant_id":"2","period":"2024-07","technology":"wind","generation_mwh":13}
    ]).to_csv(g,index=False)
    pd.DataFrame([
        {"plant_id":"1","ba":"CISO","technology":"wind","mapping_source":"audited_fixture"},
        {"plant_id":"2","ba":"CISO","technology":"wind","mapping_source":"audited_fixture"}
    ]).to_csv(x,index=False)
    return g,x

def test_aggregates_only_matched_plants(tmp_path):
    g,x=fixtures(tmp_path)
    result=aggregate(g,x,tmp_path/"out")
    d=pd.read_csv(tmp_path/"out"/"observed_ba_technology_month.csv")
    assert d.generation_mwh.iloc[0]==25
    assert result["source_validation_certified"] is False

def test_rejects_unmapped_plant(tmp_path):
    g,x=fixtures(tmp_path)
    df=pd.read_csv(x).iloc[:-1];df.to_csv(x,index=False)
    with pytest.raises(ValueError,match="Missing plant/technology"):
        aggregate(g,x,tmp_path/"out")

def test_rejects_ambiguous_crosswalk(tmp_path):
    g,x=fixtures(tmp_path)
    df=pd.read_csv(x)
    pd.concat([df,df.iloc[[0]]]).to_csv(x,index=False)
    with pytest.raises(ValueError,match="Ambiguous duplicate"):
        aggregate(g,x,tmp_path/"out")
