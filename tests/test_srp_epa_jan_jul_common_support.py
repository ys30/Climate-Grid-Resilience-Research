import numpy as np
import pandas as pd
import pytest
from grid_resilience.srp_epa_jan_jul_common_support import audit
from grid_resilience.srp_epa_2024_january_july_observed_seasonal import EXPECTED_UNITS


def sources(*, july_temp_add=0., july_demand_add=0.):
    january=pd.date_range("2024-01-01T07:00:00Z",periods=744,freq="h")
    july=pd.date_range("2024-07-01T07:00:00Z",periods=744,freq="h")
    n=np.arange(744)
    frame=[]
    for month,hours,shift in (("January",january,0.),("July",july,july_temp_add)):
        parts=[]
        for site,units in EXPECTED_UNITS.items():
            for unit in units:
                parts.append(pd.DataFrame({
                   "facility_id":site,"unit_id":unit,"timestamp_utc":hours,
                   "temperature_2m_c":10+shift+3*np.sin(n*2*np.pi/24),
                   "operating_time":np.ones(744),
                   "gross_load_mw":np.ones(744)*50.,
                   "observed_utc_month_weather_matched":n<737,
                   "era5_full_local_july_matched":True
                }))
        frame.append(pd.concat(parts,ignore_index=True))
    jan_demand=pd.DataFrame({
        "timestamp":pd.date_range("2024-01-01T00:00:00Z",periods=744,freq="h"),
        "ba":"SRP","demand_mw":np.ones(744)*4000})
    jul_demand=pd.DataFrame({
        "UTC Time at End of Hour":pd.date_range("2024-07-01T01:00:00Z",
            periods=744,freq="h").strftime("%m/%d/%Y %I:%M:%S %p"),
        "Balancing Authority":"SRP",
        "Demand (MW)":np.ones(744)*(4000+july_demand_add)})
    return frame[0],jan_demand,frame[1],jul_demand


def test_joint_exact_source_common_support_all_sites():
    result,meta=audit(*sources())
    assert len(result)==10
    assert result.january_joint_cell_covered_hours.eq(737).all()
    assert result.july_joint_cell_covered_hours.eq(737).all()
    assert result.descriptive_covariate_common_support_screen_pass.all()
    assert result.descriptive_running_gross_support_screen_pass.all()
    assert not meta["causal_temperature_derating_or_eens_claimed"]


def test_no_temperature_overlap_rejects_all():
    result,_=audit(*sources(july_temp_add=30))
    assert result.temperature_range_overlap_c.eq(0).all()
    assert not result.temperature_ranges_intersect.any()
    assert not result.descriptive_covariate_common_support_screen_pass.any()
    assert result.january_joint_cell_covered_hours.eq(0).all()


def test_temperature_overlap_alone_insufficient_if_demand_is_separate():
    result,_=audit(*sources(july_demand_add=4000))
    assert result.temperature_ranges_intersect.all()
    assert not result.demand_ranges_intersect.any()
    assert not result.descriptive_covariate_common_support_screen_pass.any()


def test_nonoperating_gross_not_admitted():
    jan,jand,jul,juld=sources()
    jan["operating_time"]=0.
    result,_=audit(jan,jand,jul,juld)
    assert result.descriptive_covariate_common_support_screen_pass.all()
    assert not result.descriptive_running_gross_support_screen_pass.any()
    assert result.january_shared_bin_reported_gross_hours.eq(0).all()


def test_duplicate_epa_hour_fails():
    jan,jand,jul,juld=sources()
    jan.loc[0,"timestamp_utc"]=jan.loc[1,"timestamp_utc"]
    with pytest.raises(ValueError,match="Duplicate EPA"):
        audit(jan,jand,jul,juld)


def test_missing_utc_demand_fails_without_fill():
    jan,jand,jul,juld=sources()
    jand=jand.iloc[:-1]
    with pytest.raises(ValueError,match="official January BA source"):
        audit(jan,jand,jul,juld)


def test_partial_epa_month_rejected():
    jan,jand,jul,juld=sources()
    with pytest.raises(ValueError,match="source-unit cohort"):
        audit(jan.drop(index=jan.index[0]),jand,jul,juld)
