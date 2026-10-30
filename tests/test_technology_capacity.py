import pandas as pd
import pytest
from grid_resilience.technology_capacity import validate

def make(tmp_path):
    p=tmp_path/"capacity.csv"
    pd.DataFrame([
        {"ba":"CISO","technology":"gas","capacity_mw":100,"source_year":2024,"capacity_source":"audited_test"},
        {"ba":"CISO","technology":"wind","capacity_mw":40,"source_year":2024,"capacity_source":"audited_test"}
    ]).to_csv(p,index=False)
    return p

def test_missing_not_zero(tmp_path):
    result=validate(make(tmp_path),tmp_path/"out",expected_bas=["CISO"],expected_year=2024)
    assert result["total_nameplate_mw"]==140
    assert ["CISO","solar"] in result["missing_ba_technology_combinations"]
    assert not result["calibration_complete"]

def test_reject_thermal_aggregate(tmp_path):
    p=make(tmp_path)
    d=pd.read_csv(p);d.loc[0,"technology"]="thermal";d.to_csv(p,index=False)
    with pytest.raises(ValueError,match="Unknown technology"):
        validate(p,tmp_path/"out")

def test_reject_wrong_year(tmp_path):
    p=make(tmp_path)
    with pytest.raises(ValueError,match="Source year mismatch"):
        validate(p,tmp_path/"out",expected_year=2023)
