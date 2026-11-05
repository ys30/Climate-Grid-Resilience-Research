import numpy as np
import pandas as pd
import pytest
from grid_resilience.srp_epa_june_july_month_predictive_transfer import audit,score,matrix
from grid_resilience.srp_epa_2024_january_july_observed_seasonal import EXPECTED_UNITS

def panels():
    out=[]
    for n,start in [(713,"2024-06-01T07:00:00Z"),(737,"2024-07-01T07:00:00Z")]:
        t=pd.date_range(start,periods=n,freq="h")
        k=np.arange(n)
        temp=33+3*np.sin(k*2*np.pi/24)+np.cos(k*.27)+.2*np.sin(k*.39)
        demand=4500+180*np.sin(k*.19)+90*np.cos(k*.27)
        items=[]
        for site,unitids in EXPECTED_UNITS.items():
            for unit in unitids:
                active=np.where(k%10>1,1.,0.)
                if unit in ("7","8","DBG4","DBG5"):
                    active=np.where(k%10>1,1.,0.) if n==737 else np.zeros(n)
                items.append(pd.DataFrame({
                    "facility_id":site,"unit_id":unit,"timestamp_utc":t,
                    "temperature_2m_c":temp,"srp_ba_demand_mw":demand,
                    "operating_time":active,
                    "gross_load_mw":np.where(active>0,100+.3*temp+np.cos(k*.13),np.nan)}))
        out.append(pd.concat(items,ignore_index=True))
    return out

def test_actual_month_direction_isolation_and_eligible_counts():
    out,m=audit(*panels())
    assert len(out)==32
    assert set(out.training_to_validation)=={"June_to_July","July_to_June"}
    assert out.groupby("training_to_validation").size().eq(16).all()
    assert not m["predictive_evaluation_is_not_operational_ex_ante_forecast"] is False
    assert m["no_unknown_heldout_month_date_fixed_effects"]
    assert m["not_usable_as_calibrated_pypsa_temperature_capacity_curve"]

def test_temperature_not_needed_for_baseline_and_later_date_unseen():
    a,_=panels()
    u=a.loc[(a.facility_id=="147")&(a.unit_id=="K-7")]
    assert matrix(u,False).shape[1]==25
    assert matrix(u,True).shape[1]==26

def test_insufficient_gross_never_imputed():
    a,b=panels()
    x=a.loc[(a.facility_id=="141")&(a.unit_id=="7")]
    y=b.loc[(b.facility_id=="141")&(b.unit_id=="7")]
    result=score(x,y,"conditional_gross_mw",True)
    assert result["status"]=="insufficient_operating_source_records"
    assert np.isnan(result["rmse"])

def test_duplicate_source_timestamps_fail():
    a,b=panels()
    a.loc[0,"timestamp_utc"]=a.loc[1,"timestamp_utc"]
    with pytest.raises(ValueError,match="Duplicate"):
        audit(a,b)

def test_missing_source_unit_hour_fails():
    a,b=panels()
    with pytest.raises(ValueError,match="cohort/UTC"):
        audit(a.iloc[:-1],b)
