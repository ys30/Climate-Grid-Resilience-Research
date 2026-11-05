import numpy as np
import pandas as pd
import pytest

from grid_resilience.srp_epa_eia930_day_block_bootstrap import (
    bootstrap_unit, partial_temperature_coef
)
from grid_resilience.srp_epa_era5_eia930_temporal_controls import design, fit


def fixture():
    t = pd.date_range("2024-07-01T07:00:00Z", periods=737, freq="h")
    k = np.arange(737)
    # Independent variation beyond common hour and day effects prevents exact collinearity.
    temp = 31 + 7*np.sin(k*2*np.pi/24) + 0.01*k/24 + np.cos(k*0.31)
    demand = 4500 + 500*np.sin(k*2*np.pi/24+0.2) + 25*np.cos(k*0.29)
    active = (np.sin(k*.15)+np.cos(k*.023)+.04*temp > 1.2).astype(float)
    return pd.DataFrame({
        "timestamp_utc":t,
        "temperature_2m_c":temp,
        "srp_demand_mw":demand,
        "operating_time":active,
        "gross_load_mw":np.where(active > 0, 70.+0.7*temp+np.sin(k*.19), np.nan)
    })


def test_fwl_day_demeaning_matches_full_fe_ols():
    f=fixture()
    local=f.timestamp_utc.dt.tz_convert("Etc/GMT+7")
    f["local_hour"]=local.dt.hour
    f["local_date"]=local.dt.strftime("%Y-%m-%d")
    y=(f.operating_time > 0).astype(float).to_numpy()
    a=partial_temperature_coef(f,y,f.local_date.to_numpy())
    controls,temp=design(f)
    b=fit(y,controls,temp)
    assert b["status"]=="descriptive_ols_only"
    assert a==pytest.approx(b["temp_coef"],abs=1e-7)


def test_reproducible_day_block_diagnostics():
    f=fixture()
    a=bootstrap_unit(f,n_rep=50,seed=123)
    b=bootstrap_unit(f,n_rep=50,seed=123)
    pd.testing.assert_frame_equal(a,b)
    assert len(a)==2
    assert a.days_in_source.eq(31).all()
    assert a.replicates_requested.eq(50).all()
    assert a.replicates_admitted.le(50).all()
    assert not a.point_estimate_per_c.isna().any()


def test_insufficient_running_records_not_reported_as_bootstrap():
    f=fixture()
    f["operating_time"]=0.0
    f.loc[:12,"operating_time"]=1.0
    f.loc[13:,"gross_load_mw"]=np.nan
    x=bootstrap_unit(f,n_rep=50)
    g=x.loc[x.outcome.eq("gross_load_given_positive_operation_mw")].iloc[0]
    assert g.source_valid_observations<=13
    assert not g.interval_reportable
    assert g.replicates_admitted==0
    assert np.isnan(g.percentile_2_5)


def test_reject_fewer_than_31_local_date_blocks():
    f=fixture().iloc[:-30]
    with pytest.raises(ValueError,match="31 local July"):
        bootstrap_unit(f,n_rep=50)


def test_reject_too_few_requested_replicates():
    with pytest.raises(ValueError,match="At least 50"):
        bootstrap_unit(fixture(),n_rep=8)
