import numpy as np
import pandas as pd
import pytest

from grid_resilience.srp_epa_2024_january_eia930_controlled_transfer import analyze
from grid_resilience.srp_epa_2024_january_july_observed_seasonal import EXPECTED_UNITS

def inputs():
    date=pd.date_range("2024-01-01T07:00:00Z",periods=744,freq="h")
    n=np.arange(744)
    pieces=[]
    for plant,units in EXPECTED_UNITS.items():
        for unit in units:
            pieces.append(pd.DataFrame({
                "facility_id":plant,"unit_id":unit,"timestamp_utc":date,
                "temperature_2m_c":10+7*np.sin(n*2*np.pi/24)+np.cos(n*.31),
                "operating_time":np.where(n%4,1.,0.),
                "gross_load_mw":np.where(n%4,100+np.sin(n*.3),np.nan),
                "observed_utc_month_weather_matched":n<737,
            }))
    ep=pd.concat(pieces,ignore_index=True)
    d=pd.DataFrame({"timestamp":pd.date_range("2024-01-01T00:00:00Z",periods=744,freq="h"),
        "ba":"SRP","demand_mw":4000+150*np.cos(np.arange(744)*.31)})
    j=pd.DataFrame([{"facility_id":plant,"epa_unit_id":unit,
        "operation_model_status":"descriptive_ols_only",
        "gross_load_model_status":"descriptive_ols_only",
        "operation_lpm_temperature_coefficient_per_c":.05,
        "gross_load_temperature_coefficient_mw_per_c":-1.2}
        for plant,units in EXPECTED_UNITS.items() for unit in units])
    return ep,d,j

def test_winter_july_true_cohort_and_not_causal():
    output,meta=analyze(*inputs())
    assert len(output)==10
    assert output.source_matched_hours.eq(737).all()
    assert output.january_operation_model_status.eq("descriptive_ols_only").all()
    assert not meta["causal_effect_or_transfer_predictive_validity_claimed"]
    assert not meta["generator_thermal_derating_or_net_mw_calibrated"]

def test_winter_zero_run_does_not_make_gross_load_zero():
    ep,d,j=inputs()
    ep.loc[ep.unit_id.eq("1"),"operating_time"]=0.
    out,_=analyze(ep,d,j)
    r=out.loc[out.epa_unit_id.eq("1")].iloc[0]
    assert r.source_conditional_gross_valid_hours==0
    assert r.january_operation_model_status=="constant_outcome_no_operational_variation"
    assert pd.isna(r.january_operation_temperature_lpm_per_c)
    assert pd.isna(r.winter_summer_operating_slope_same_sign_descriptively)
    assert r.january_gross_model_status=="insufficient_outcome_records"
    assert pd.isna(r.january_gross_temperature_mw_per_c)

def test_missing_official_demand_fails_closed():
    ep,d,j=inputs()
    d.loc[14,"demand_mw"]=np.nan
    with pytest.raises(ValueError,match="demand missing or invalid"):
        analyze(ep,d,j)

def test_duplicate_official_hour_rejected():
    ep,d,j=inputs()
    d.loc[4,"timestamp"]=d.loc[3,"timestamp"]
    with pytest.raises(ValueError,match="identity/size invalid"):
        analyze(ep,d,j)

def test_duplicate_source_hour_rejected():
    ep,d,j=inputs()
    ep.loc[0,"timestamp_utc"]=ep.loc[1,"timestamp_utc"]
    with pytest.raises(ValueError,match="duplicate UTC hours"):
        analyze(ep,d,j)

def test_july_unit_mismatch_rejected():
    ep,d,j=inputs()
    j.loc[0,"epa_unit_id"]="FAKE"
    with pytest.raises(ValueError,match="cohorts not identical"):
        analyze(ep,d,j)

def test_all_one_source_outcome_has_no_meaningful_temperature_slope():
    ep,d,j=inputs()
    ep.loc[ep.unit_id.eq("2"),"operating_time"]=1.
    out,_=analyze(ep,d,j)
    row=out.loc[out.epa_unit_id.eq("2")].iloc[0]
    assert row.january_operation_model_status=="constant_outcome_no_operational_variation"
    assert pd.isna(row.january_operation_temperature_lpm_per_c)
