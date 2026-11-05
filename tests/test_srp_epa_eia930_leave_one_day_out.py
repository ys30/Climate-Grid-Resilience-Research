import numpy as np
import pandas as pd
import pytest

from grid_resilience.srp_epa_eia930_leave_one_day_out import leave_one_day


def source():
    t=pd.date_range("2024-07-01T07:00:00Z",periods=737,freq="h")
    n=np.arange(len(t))
    hour=np.sin(n*2*np.pi/24)
    temp=30+8*hour+np.cos(n*.23)+n*.002
    operating=np.where(np.sin(n*.11)+0.05*temp>1.4,1.,0.)
    f=pd.DataFrame({"timestamp_utc":t,
       "temperature_2m_c":temp,
       "operating_time":operating,
       "gross_load_mw":np.where(operating>0,100+2*temp+np.cos(n*.17),np.nan),
       "srp_demand_mw":4000+600*hour+np.cos(n*.32)*100})
    return f


def test_31_day_deletions_and_noncausal_outputs():
    out=leave_one_day(source())
    assert len(out)==2
    assert out.local_days_tested.eq(31).all()
    assert out.date_deletions_identified.le(31).all()
    assert not out.full_sample_coef_per_c.isna().any()


def test_sparse_gross_source_remains_not_estimated():
    f=source()
    f["operating_time"]=0.
    f.loc[:12,"operating_time"]=1.
    f.loc[13:,"gross_load_mw"]=np.nan
    result=leave_one_day(f)
    gross=result.loc[result.outcome.eq("gross_load_given_positive_operation_mw")].iloc[0]
    assert gross.status=="full_model_insufficient_or_unidentified"
    assert gross.date_deletions_identified==0


def test_incomplete_date_calendar_rejected():
    with pytest.raises(ValueError,match="31 local July"):
        leave_one_day(source().iloc[:600])
