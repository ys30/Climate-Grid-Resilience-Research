import numpy as np
import pandas as pd
import pytest

from grid_resilience.srp_epa_june_july_multiday_difference_bootstrap import (
    audit, within_month_blocks)
from grid_resilience.srp_epa_june_july_overlap_models import overlap_models
from grid_resilience.srp_epa_2024_january_july_observed_seasonal import EXPECTED_UNITS


def source_panels():
    out=[]
    for month,n,start in [
        ("June",713,"2024-06-01T07:00:00Z"),
        ("July",737,"2024-07-01T07:00:00Z")]:
        t=pd.date_range(start,periods=n,freq="h")
        k=np.arange(n)
        weather=33+2.2*np.sin(k*2*np.pi/24)+0.9*np.cos(k*.23)+.3*np.sin(k*.09)
        demand=5100+220*np.cos(k*.18)+180*np.sin(k*.29)
        units=[]
        for site,unitset in EXPECTED_UNITS.items():
            for unit in unitset:
                op=np.where(k%9>1,1.,0.)
                if unit in ("7","8","DBG4","DBG5") and month=="June":
                    op=np.zeros(n)
                units.append(pd.DataFrame({
                    "facility_id":site,"unit_id":unit,
                    "timestamp_utc":t,"temperature_2m_c":weather,
                    "srp_ba_demand_mw":demand,"operating_time":op,
                    "gross_load_mw":np.where(op>0,80+1.4*weather+np.cos(k*.12),np.nan)}))
        out.append(pd.concat(units,ignore_index=True))
    return out


def test_consecutive_month_blocks_and_repeated_date_fixed_effect_ids():
    t=pd.date_range("2024-06-01T07:00:00Z",periods=713,freq="h")
    dates=t.tz_convert("Etc/GMT+7").strftime("%Y-%m-%d")
    f=pd.DataFrame({"local_date":dates})
    a=within_month_blocks(f,50,3,np.random.default_rng(31))
    b=within_month_blocks(f,50,3,np.random.default_rng(31))
    assert len(a)==50
    assert all(np.array_equal(x[0],y[0]) and np.array_equal(x[1],y[1]) for x,y in zip(a,b))
    for indices,groups in a:
        assert len(indices)==len(groups)
        assert min(indices)>=0 and max(indices)<713
        assert len(np.unique(groups))==30
        # Each consecutively selected date occurrence receives independent FE.
        for gid in np.unique(groups):
            selected=indices[groups==gid]
            assert len(np.unique(dates[selected]))==1


def test_one_supported_width_original_coefficient_is_reproduced():
    june,july=source_panels()
    baseline,_,support,_=overlap_models(june,july)
    assert support.operating_gross_screen_pass.sum()==6
    res,summ,scope=audit(june,july,baseline,replicates=50,seed=41,widths=(2,))
    assert len(res)==6 and len(summ)==6
    assert res.block_width_consecutive_local_dates.eq(2).all()
    assert res.paired_moving_block_draws_requested.eq(50).all()
    assert res.paired_moving_block_draws_admitted.le(50).all()
    assert scope["original_point_coefficient_matches_source_ols"]
    assert not scope["causal_thermal_derating_or_eia_net_mw_estimated"]


def test_false_original_source_slope_is_rejected():
    june,july=source_panels()
    baseline,_,_,_=overlap_models(june,july)
    selector=baseline.epa_unit_id.eq("K-7")&baseline.month.eq("June")
    baseline.loc[selector,"gross_temperature_mw_per_c"]+=2.
    with pytest.raises(ValueError,match="FWL differs"):
        audit(june,july,baseline,replicates=50,widths=(2,))


def test_missing_source_hour_fails_before_resampling():
    june,july=source_panels()
    baseline,_,_,_=overlap_models(june,july)
    with pytest.raises(ValueError,match="cohort/UTC"):
        audit(june.iloc[:-1],july,baseline,replicates=50,widths=(2,))


def test_reject_unsupported_width_and_insufficient_repetitions():
    with pytest.raises(ValueError,match="Unsupported"):
        audit(pd.DataFrame(),pd.DataFrame(),pd.DataFrame(),widths=(7,))
    with pytest.raises(ValueError,match="at least 50"):
        audit(pd.DataFrame(),pd.DataFrame(),pd.DataFrame(),replicates=6)
