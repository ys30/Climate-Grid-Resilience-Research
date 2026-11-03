"""Zero-observed-output fuel-derated capacity sensitivity. Synthetic only."""
import numpy as np
import pandas as pd
import pytest
from grid_resilience.srp_zero_observed_capacity_sensitivity import scenario

def inputs():
    t=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    d=pd.DataFrame({"timestamp_utc":t.astype(str),"demand_mw":50.0,
     "observed_import_mw":0.0,"observed_export_mw":0.0,
     "screened_fleet_generation_mw":50.0,"modeled_unserved_mw":0.0,
     "boundary_spill_mw":0.0,"hydro_dispatch_mw":0.0,"ps_charge_mw":0.0,
     "ps_discharge_mw":0.0,"bus_balance_residual_mw":0.0})
    r=pd.DataFrame({"plant_id":["001","2"],"generator_id":["A","B"],
     "screening_candidate":[True,True],
     "nameplate_capacity_mw":[60.0,40.0],"energy_source_1":["NG","NG"]})
    o=pd.DataFrame({"plant_id":["1","2"],"generator_id":["A","B"],
     "generation_mwh":[0.0,100.0],
     "identity_scope":["exact_screened_generator","exact_screened_generator"]})
    c=pd.DataFrame({"ba":["SRP"],"technology":["NG"],"capacity_mw":[80.0],
     "original_nameplate_mw":[100.0],"marginal_cost":[55.0]})
    return d,r,o,c

def test_zero_output_removal_only_hypothetical():
    z=scenario(*inputs())
    assert z["source_matched_screened_zero_output_units"]==1
    assert z["source_matched_screened_zero_output_nameplate_mw"]==60
    assert z["scenario_capacity_removed_after_original_deratings_mw"]==48
    assert z["scenario_available_mw"]==32
    assert z["scenario_modeled_unserved_mwh"]==18*744
    assert z["scenario_gap_hours"]==744
    assert z["historical_availability_inferred"] is False

def test_incomplete_source_join_fails():
    d,r,o,c=inputs()
    with pytest.raises(ValueError,match="Incomplete source identity"):
        scenario(d,r,o.iloc[:-1],c)

def test_nameplate_mismatch_fails_closed():
    d,r,o,c=inputs()
    c.loc[0,"original_nameplate_mw"]=99.
    with pytest.raises(ValueError,match="does not reconcile"):
        scenario(d,r,o,c)

def test_missing_model_fuel_fails_closed():
    d,r,o,c=inputs()
    r.loc[1,"energy_source_1"]="SUB"
    with pytest.raises(ValueError,match="fuel populations differ"):
        scenario(d,r,o,c)

def test_incorrect_scope_fails_closed():
    d,r,o,c=inputs()
    o.loc[1,"identity_scope"]="reviewed_but_excluded"
    with pytest.raises(ValueError,match="eligibility scope"):
        scenario(d,r,o,c)
