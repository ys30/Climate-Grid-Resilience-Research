"""Independent hourly oracle audit contracts. No PyPSA import required."""
import numpy as np
import pandas as pd
import pytest
from grid_resilience.srp_hourly_oracle_audit import audit

def fixture():
    t=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    demand=np.full(744,50.)
    signed=np.where(np.arange(744)%2==0,-70.,20.)
    exports=np.maximum(signed,0.)
    imports=np.maximum(-signed,0.)
    cap=30.
    required=demand+exports-imports
    local=np.clip(required,0,cap)
    unserved=np.maximum(required-local,0.)
    spill=np.maximum(-required,0.)
    d=pd.DataFrame({
        "timestamp_utc":t.astype(str),
        "demand_mw":demand,
        "observed_export_mw":exports,
        "observed_import_mw":imports,
        "screened_fleet_generation_mw":local,
        "modeled_unserved_mw":unserved,
        "boundary_spill_mw":spill,
        "hydro_dispatch_mw":0.,
        "ps_charge_mw":0.,
        "ps_discharge_mw":0.,
        "bus_balance_residual_mw":0.
    })
    c=pd.DataFrame([{"ba":"SRP","technology":"NG","capacity_mw":cap,"marginal_cost":55.}])
    return d,c

def test_744h_oracle_matches_correct_dispatch():
    d,c=fixture()
    r=audit(d,c)
    assert r["source_hour_count"]==744
    assert r["modeled_unserved_mwh"]==372*40
    assert r["hours_with_modeled_unserved"]==372
    assert r["maximum_hourly_unserved_mw"]==40.
    assert max(r["largest_hourly_error_mw_by_component"].values())<1e-6
    assert r["historical_calibration_certified"] is False

@pytest.mark.parametrize("field",["screened_fleet_generation_mw","modeled_unserved_mw","boundary_spill_mw","bus_balance_residual_mw"])
def test_hourly_tampering_is_detected(field):
    d,c=fixture()
    d.loc[0,field]+=1.
    with pytest.raises(RuntimeError,match="Analytic dispatch disagreement"):
        audit(d,c)

def test_missing_hour_rejected():
    d,c=fixture()
    with pytest.raises(ValueError,match="UTC baseline"):
        audit(d.iloc[:-1],c)

def test_incorrect_hydro_dispatch_rejected():
    d,c=fixture()
    d.loc[0,"hydro_dispatch_mw"]=2.
    with pytest.raises(ValueError,match="without HY/PS"):
        audit(d,c)

def test_negative_cost_rejected():
    d,c=fixture()
    c.loc[0,"marginal_cost"]=-1.
    with pytest.raises(ValueError,match="positive local generation"):
        audit(d,c)
