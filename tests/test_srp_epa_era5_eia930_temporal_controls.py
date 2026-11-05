import numpy as np
import pandas as pd
import pytest
from grid_resilience.srp_epa_era5_eia930_temporal_controls import audit, fit

def sources():
    hours=pd.date_range("2024-07-01T07:00:00Z",periods=744,freq="h")
    epa=pd.concat([pd.DataFrame({
        "facility_id":plant,"unit_id":unit,"timestamp_utc":hours,
        "temperature_2m_c":30+9*np.sin(np.arange(744)/24*2*np.pi)+np.arange(744)/744,
        "operating_time":np.where(np.arange(744)%7<4,1.,0.),
        "gross_load_mw":np.where(np.arange(744)%7<4,80.+np.arange(744)%24,np.nan),
        "era5_full_local_july_matched":True})
        for plant,units in (("141",["1","2","3","7","8"]),
                            ("55129",["DBG1","DBG2","DBG4","DBG5"]),
                            ("147",["K-7"])) for unit in units],ignore_index=True)
    eia=pd.DataFrame({
        "UTC Time at End of Hour":pd.date_range("2024-07-01T01:00:00Z",periods=744,freq="h").strftime("%m/%d/%Y %I:%M:%S %p"),
        "Balancing Authority":"SRP",
        "Demand (MW)":4000+500*np.sin(np.arange(744)/24*2*np.pi)})
    return epa,eia

def test_complete_source_hour_controls_and_no_causal_claim():
    result,scope=audit(*sources())
    assert len(result)==10
    assert result.hours_with_ba_demand_context.eq(737).all()
    assert scope["source_matched_hours_per_unit"]==737
    assert not scope["causal_temperature_derating_or_eia_generator_net_mw_estimated"]
    assert not scope["physical_generator_identity_admitted"]

def test_cannot_identify_temperature_perfectly_explained_by_controls():
    a=np.column_stack([np.ones(100),np.linspace(0,1,100)])
    v=fit(np.ones(100),a,a[:,1])
    assert v["status"]=="temperature_unidentified_after_controls"

def test_not_enough_operating_gross_load():
    y=np.full(100,np.nan);y[:12]=20.
    v=fit(y,np.ones((100,1)),np.arange(100))
    assert v["status"]=="insufficient_outcome_records"

def test_missing_source_hour_rejected():
    epa,eia=sources()
    with pytest.raises(ValueError,match="Incomplete EPA local-July calendar"):
        audit(epa.iloc[:-1],eia)

def test_missing_official_ba_demand_rejected():
    epa,eia=sources()
    eia.loc[0,"Demand (MW)"]=None
    with pytest.raises(ValueError,match="Missing or invalid official SRP demand"):
        audit(epa,eia)

def test_invalid_operating_fraction_rejected():
    epa,eia=sources()
    epa.loc[0,"operating_time"]=2.
    with pytest.raises(ValueError,match="out of bounds"):
        audit(epa,eia)
