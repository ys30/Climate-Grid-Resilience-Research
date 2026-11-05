import numpy as np
import pandas as pd
import pytest

from grid_resilience.srp_epa_eia930_multiday_block_sensitivity import (
    moving_day_indices, analyze_unit,
)
from grid_resilience.srp_epa_eia930_day_block_bootstrap import partial_temperature_coef


def source():
    t=pd.date_range("2024-07-01T07:00:00Z",periods=737,freq="h")
    n=np.arange(737)
    temp=33+7*np.sin(n*.262)+.08*np.cos(n*.91)+np.cos(n*.13)
    run=(np.sin(n*.13)+.05*temp>1.5).astype(float)
    return pd.DataFrame({
        "timestamp_utc":t,"temperature_2m_c":temp,
        "operating_time":run,
        "gross_load_mw":np.where(run>0,40+0.7*temp+np.cos(n*.28),np.nan),
        "srp_demand_mw":4100+500*np.cos(n*.26)+75*np.cos(n*.45)
    })


def test_moving_blocks_contiguous_no_wrap_and_independent_date_ids():
    pos=[np.array([j*24,k],dtype=int) for j,k in zip(range(31),range(31))]
    idx,group,selected=moving_day_indices(pos,5,np.random.default_rng(44))
    assert len(selected)==31
    assert len(idx)==len(group)==62
    assert max(group)==30
    for start in range(0,25,5):
        assert selected[start:start+5]==list(range(selected[start],selected[start]+5))
    assert max(selected)<31


def test_reproducible_2_3_5_day_diagnostics():
    a=analyze_unit(source(),reps=50,seed=31)
    b=analyze_unit(source(),reps=50,seed=31)
    pd.testing.assert_frame_equal(a,b)
    assert len(a)==6
    assert set(a.block_width_local_days)=={2,3,5}
    assert a.replicates_requested.eq(50).all()
    assert a.replicates_admitted.le(50).all()


def test_preserve_previous_full_original_point_coefficient():
    f=source()
    local=f.timestamp_utc.dt.tz_convert("Etc/GMT+7")
    f["local_hour"]=local.dt.hour
    f["local_date"]=local.dt.strftime("%Y-%m-%d")
    original=partial_temperature_coef(
        f,(f.operating_time>0).astype(float),f.local_date.to_numpy())
    result=analyze_unit(source(),reps=50)
    observed=result.loc[result.outcome.eq("reported_operation_lpm")]
    assert observed.point_estimate_per_c.eq(original).all()


def test_sparse_positive_gross_never_publishes_percentiles():
    f=source()
    f["operating_time"]=0.0
    f.loc[:10,"operating_time"]=1.0
    f.loc[11:,"gross_load_mw"]=np.nan
    result=analyze_unit(f,reps=50)
    gross=result.loc[result.outcome.eq("gross_load_given_positive_operation_mw")]
    assert gross.replicates_admitted.eq(0).all()
    assert not gross.percentile_reportable.any()


def test_calendar_hour_loss_rejected():
    with pytest.raises(ValueError,match="31 exact MST dates and 737"):
        analyze_unit(source().iloc[:-1],reps=50)


def test_unsupported_block_width_rejected():
    with pytest.raises(ValueError,match="Unsupported"):
        analyze_unit(source(),reps=50,widths=[7])
