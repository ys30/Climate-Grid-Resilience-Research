import json
import pytest
from grid_resilience.bpat_grand_coulee_ps_irrigation_access_sensitivity import derive_scenarios

def gates(tmp_path):
    u={"eia860_2024_plant_id":"6163",
       "physical_reversible_PS_generating_units":6,
       "Banks_Lake_upper_reservoir_and_irrigation_water_storage":True,
       "PS_usable_MWh_verified":False}
    p={"bpat_ps_prime_mover_records":6,"bpat_ps_positive_nameplate_mw":314.,
       "physical_ps_672h_dispatch_parameters_admitted":False}
    a=tmp_path/"usbr.json";b=tmp_path/"eia.json"
    a.write_text(json.dumps(u));b.write_text(json.dumps(p))
    return a,b,u,p

def test_irrigation_sensitive_access_is_hypothetical_not_measured(tmp_path):
    a,b,_,_=gates(tmp_path)
    s=derive_scenarios(a,b)
    assert s==((0.,0.,1.),(78.5,314.,.8),(157.,628.,.8),(314.,1256.,.8))

def test_refuse_ps_mwh_source_claim(tmp_path):
    a,b,u,_=gates(tmp_path)
    u["PS_usable_MWh_verified"]=True
    a.write_text(json.dumps(u))
    with pytest.raises(ValueError,match="protection gate"):
        derive_scenarios(a,b)

def test_wrong_grand_coulee_plant_fails(tmp_path):
    a,b,u,_=gates(tmp_path)
    u["eia860_2024_plant_id"]="6167"
    a.write_text(json.dumps(u))
    with pytest.raises(ValueError,match="protection gate"):
        derive_scenarios(a,b)

def test_unverified_six_unit_capacity_fails(tmp_path):
    a,b,_,p=gates(tmp_path)
    p["bpat_ps_positive_nameplate_mw"]=1000.
    b.write_text(json.dumps(p))
    with pytest.raises(ValueError,match="protection gate"):
        derive_scenarios(a,b)
