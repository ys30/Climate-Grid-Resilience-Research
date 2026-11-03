"""Model-gap relief must use hourly minima, not nameplate times all hours."""
import numpy as np
import pandas as pd
import pytest
from grid_resilience.srp_firm_capacity_frontier import frontier

def sample():
    t=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    gaps=np.zeros(744)
    gaps[:2]=[10.,20.]
    return pd.DataFrame({"timestamp_utc":t.astype(str),
             "modeled_unserved_mw":gaps,"bus_balance_residual_mw":0.})

def test_hourly_capacity_relief():
    rows,summary=frontier(sample(),[0,5,10,20])
    assert list(rows.remaining_model_gap_mwh)==[30.,20.,10.,0.]
    assert list(rows.remaining_positive_gap_hours)==[2,2,1,0]
    assert summary["minimum_additional_perfectly_firm_mw_to_eliminate_all_model_gaps"]==20
    assert rows.loc[rows.incremental_firm_capacity_mw.eq(5),
                    "hypothetical_full_output_month_mwh"].iloc[0]==3720.

def test_monotonicity_and_bounded_contribution():
    rows,_=frontier(sample(),[20,10,5,0])
    assert rows.remaining_model_gap_mwh.is_monotonic_decreasing
    assert (rows.maximum_gap_reduction_mwh<=rows.hypothetical_full_output_month_mwh+1e-8).all()

@pytest.mark.parametrize("mode",["missing","duplicate","nonfinite","negative","imbalance"])
def test_bad_source_rejected(mode):
    a=sample()
    if mode=="missing":a=a.iloc[:-1]
    elif mode=="duplicate":a.loc[1,"timestamp_utc"]=a.loc[0,"timestamp_utc"]
    elif mode=="nonfinite":a.loc[0,"modeled_unserved_mw"]=np.inf
    elif mode=="negative":a.loc[0,"modeled_unserved_mw"]=-2
    elif mode=="imbalance":a.loc[0,"bus_balance_residual_mw"]=1
    with pytest.raises(ValueError):frontier(a,[0,5])

def test_bad_capacity_rejected():
    with pytest.raises(ValueError):frontier(sample(),[0,-1])
    with pytest.raises(ValueError):frontier(sample(),[0,np.inf])
    with pytest.raises(ValueError):frontier(sample(),[0,0])
