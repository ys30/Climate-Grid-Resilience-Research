import pandas as pd
import pytest
from grid_resilience.observation_coverage import audit

def fixture(tmp_path):
    obs=tmp_path/"obs.csv";exp=tmp_path/"expected.csv"
    rows=[{"plant_id":"1","technology":"wind","period":"2024-07"}]
    pd.DataFrame([{**rows[0],"generation_mwh":0,"source_file":"fixture.csv",
                   "reporting_basis":"net"}]).to_csv(obs,index=False)
    pd.DataFrame(rows).to_csv(exp,index=False)
    return obs,exp

def test_zero_observation_is_valid(tmp_path):
    o,e=fixture(tmp_path)
    result=audit(o,e,tmp_path/"out")
    assert result["rows"]==1
    assert result["source_authenticated"] is False

def test_missing_observation_rejected(tmp_path):
    o,e=fixture(tmp_path)
    expected=pd.read_csv(e,dtype=str)
    expected.loc[len(expected)]=["2","solar","2024-07"]
    expected.to_csv(e,index=False)
    with pytest.raises(ValueError,match="coverage mismatch"):
        audit(o,e,tmp_path/"out")

def test_mixed_reporting_basis_rejected(tmp_path):
    o,e=fixture(tmp_path)
    x=pd.read_csv(o,dtype=str)
    x.loc[len(x)]=["2","solar","2024-07","25","fixture.csv","gross"]
    x.to_csv(o,index=False)
    pd.DataFrame(x[["plant_id","technology","period"]]).to_csv(e,index=False)
    with pytest.raises(ValueError,match="Mixed reporting bases"):
        audit(o,e,tmp_path/"out")
