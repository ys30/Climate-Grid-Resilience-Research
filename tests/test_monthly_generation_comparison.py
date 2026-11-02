import pandas as pd
import pytest
from grid_resilience.monthly_generation_comparison import compare

def inputs():
    obs=pd.DataFrame([
        {"year":y,"month":mo,"ba":"SRP","technology":"gas","net_generation_mwh":100.,"source":"audited_eia923"}
        for y in (2023,2024) for mo in range(1,13)])
    model=obs[["year","month","ba","technology"]].copy()
    model["modeled_generation_mwh"]=110.
    return obs,model

def test_train_and_holdout_comparison():
    o,m=inputs()
    rows,metrics=compare(o,m,holdout_years={2024})
    assert len(rows)==24
    assert set(metrics.period)=={"training","holdout"}
    assert metrics.mae_mwh.eq(10).all()
    assert metrics.signed_bias_mwh.eq(10).all()
    assert metrics.rmse_mwh.eq(10).all()

def test_reject_missing_month():
    o,m=inputs()
    with pytest.raises(ValueError,match="Incomplete"):
        compare(o,m.iloc[:-1],holdout_years={2024})

def test_reject_duplicate_month():
    o,m=inputs()
    with pytest.raises(ValueError,match="duplicate"):
        compare(pd.concat([o,o.iloc[[0]]]),m,holdout_years={2024})

def test_require_holdout():
    o,m=inputs()
    with pytest.raises(ValueError,match="holdout"):
        compare(o,m,holdout_years={2025})

def test_no_invented_training_year():
    o,m=inputs()
    with pytest.raises(ValueError,match="Training"):
        compare(o[o.year==2024],m[m.year==2024],holdout_years={2024})

def test_missing_source_provenance_fails():
    o,m=inputs()
    o.loc[0,"source"]=""
    with pytest.raises(ValueError,match="source provenance"):
        compare(o,m,holdout_years={2024})
