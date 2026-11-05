import numpy as np
import pandas as pd
import pytest

from grid_resilience.srp_epa_june_july_common_support_bootstrap import (
    audit, date_draws)
from grid_resilience.srp_epa_june_july_overlap_models import overlap_models
from grid_resilience.srp_epa_2024_january_july_observed_seasonal import EXPECTED_UNITS


def observed_like_panels():
    panels=[]
    for month,n,start in (
        ("June",713,"2024-06-01T07:00:00Z"),
        ("July",737,"2024-07-01T07:00:00Z")):
        t=pd.date_range(start,periods=n,freq="h")
        k=np.arange(n)
        temp=34+2.3*np.sin(k*2*np.pi/24)+.9*np.cos(k*.27)+.4*np.sin(k*.073)
        demand=5100+290*np.sin(k*.16)+150*np.cos(k*.31)
        source=[]
        for plant,unitids in EXPECTED_UNITS.items():
            for unit in unitids:
                active=np.where(k%7>1,1.,0.)
                if unit in ("7","8","DBG4","DBG5") and month=="June":
                    active=np.zeros(n)
                source.append(pd.DataFrame({
                    "facility_id":plant,"unit_id":unit,"timestamp_utc":t,
                    "temperature_2m_c":temp,"srp_ba_demand_mw":demand,
                    "operating_time":active,
                    "gross_load_mw":np.where(active>0,
                        65+1.0*temp+np.cos(k*.13),np.nan)}))
        panels.append(pd.concat(source,ignore_index=True))
    return panels


def test_paired_block_sensitivity_and_original_point_reproduction():
    a,b=observed_like_panels()
    original,_,support,_=overlap_models(a,b)
    assert support.operating_gross_screen_pass.sum()==6
    result,manifest=audit(a,b,original,replicates=50,seed=51)
    assert len(result)==6
    assert result.paired_date_block_replicates_requested.eq(50).all()
    assert result.paired_date_block_replicates_admitted.le(50).all()
    assert manifest["source_point_coefficients_fwl_match_prior_ols"]
    assert not manifest["causal_thermal_derating_or_generator_available_net_mw_estimated"]
    assert not manifest["predictive_holdout_validation_performed"]


def test_date_bootstrap_relabels_repeated_days():
    t=pd.date_range("2024-06-01T07:00:00Z",periods=713,freq="h")
    f=pd.DataFrame({"local_date":t.tz_convert("Etc/GMT+7").strftime("%Y-%m-%d")})
    draws=date_draws(f,50,np.random.default_rng(7))
    assert len(draws)==50
    for indices,ids in draws:
        assert len(indices)==len(ids)
        assert len(np.unique(ids))==30
        assert indices.max()<713


def test_reject_incomplete_baseline():
    a,b=observed_like_panels()
    with pytest.raises(ValueError,match="baseline"):
        audit(a,b,pd.DataFrame(),replicates=50)


def test_reject_unverified_source_hour():
    a,b=observed_like_panels()
    original,_,_,_=overlap_models(a,b)
    with pytest.raises(ValueError,match="cohort/UTC"):
        audit(a.iloc[:-1],b,original,replicates=50)


def test_reject_tiny_resample_count():
    a,b=observed_like_panels()
    with pytest.raises(ValueError,match="at least 50"):
        audit(a,b,pd.DataFrame(),replicates=12)
