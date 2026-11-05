import numpy as np
import pandas as pd
import pytest

from grid_resilience.srp_epa_june_july_overlap_models import overlap_models
from grid_resilience.srp_epa_2024_january_july_observed_seasonal import EXPECTED_UNITS


def panels(*, hot_shift=0, zero_operating_unit=None):
    parts=[]
    for month,n,start,shift in [
        ("June",713,"2024-06-01T07:00:00Z",0.),
        ("July",737,"2024-07-01T07:00:00Z",hot_shift)]:
        t=pd.date_range(start,periods=n,freq="h")
        k=np.arange(n,dtype=float)
        temp=32+shift+3*np.sin(k*2*np.pi/24)+np.cos(k*.37)+.35*np.sin(k*.027)
        demand=5100+200*np.sin(k*.22)+130*np.cos(k*.078)
        frames=[]
        for site,units in EXPECTED_UNITS.items():
            for unit in units:
                op=np.where((k.astype(int)%9)>1,1.,0.)
                if unit==zero_operating_unit and month=="June":
                    op=np.zeros(n)
                frames.append(pd.DataFrame({
                    "facility_id":site,"unit_id":unit,"timestamp_utc":t,
                    "temperature_2m_c":temp,"srp_ba_demand_mw":demand,
                    "operating_time":op,
                    "gross_load_mw":np.where(op>0,70+1.1*temp+np.cos(k*.45),np.nan)
                }))
        parts.append(pd.concat(frames,ignore_index=True))
    return parts


def test_verified_joint_overlap_months_and_noncausal_gates():
    r,p,s,m=overlap_models(*panels())
    assert len(r)==20 and len(p)==10 and len(s)==10
    assert r.groupby("month").size().eq(10).all()
    assert r.joint_support_screen_pass.all()
    assert r.joint_conditional_gross_screen_pass.all()
    assert not m["physical_thermal_derating_or_observed_eens_estimated"]
    assert not m["predictive_out_of_sample_validation_performed"]


def test_missing_operating_history_does_not_create_gross_coefficients():
    june,july=panels(zero_operating_unit="1")
    result,paired,summary,_=overlap_models(june,july)
    subset=result.loc[(result.epa_unit_id=="1")&(result.month=="June")]
    assert len(subset)==1
    assert subset.iloc[0].gross_model_status=="conditional_gross_support_screen_failed"
    assert pd.isna(subset.iloc[0].gross_temperature_mw_per_c)
    assert subset.iloc[0].operating_model_status=="constant_outcome_no_operational_variation"


def test_no_temperature_common_support_rejects_transfer():
    june,july=panels(hot_shift=30)
    result,paired,summary,_=overlap_models(june,july)
    assert not summary.covariate_screen_pass.any()
    assert result.operating_model_status.eq("joint_support_screen_failed").all()
    assert result.gross_model_status.eq("conditional_gross_support_screen_failed").all()
    assert paired.june_operation_temp_per_c.isna().all()


def test_reject_duplicate_source_hour():
    june,july=panels()
    june.loc[0,"timestamp_utc"]=june.loc[1,"timestamp_utc"]
    with pytest.raises(ValueError,match="Duplicate source"):
        overlap_models(june,july)


def test_reject_missing_source_unit_hour():
    june,july=panels()
    with pytest.raises(ValueError,match="cohort/UTC"):
        overlap_models(june.iloc[:-1],july)
