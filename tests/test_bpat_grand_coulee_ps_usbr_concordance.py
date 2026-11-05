import pandas as pd
import pytest
from grid_resilience.bpat_grand_coulee_ps_usbr_concordance import audit,EXPECTED

def sample():
    return pd.DataFrame([{
      "plant_id":"6163","generator_id":k,"prime_mover":"PS",
      "reported_technology":"Hydroelectric Pumped Storage",
      "nameplate_capacity_mw":v,"ba":"BPAT","storage_sheet_join":"left_only"
    } for k,v in EXPECTED.items()])

def test_verified_six_grand_coulee_ps_units_source_and_irrigation_limits():
    x,m=audit(sample())
    assert len(x)==6 and x.nameplate_capacity_mw.sum()==314
    assert m["physical_reversible_PS_generating_units"]==6
    assert m["Banks_Lake_active_storage_acre_feet_usbr_described"]==715000
    assert m["active_storage_acre_feet_is_not_usable_PS_energy_MWh"]
    assert not m["PS_usable_MWh_verified"]
    assert not m["earlier_model_zero_initial_final_SOC_is_historical_fact"]

def test_ps_unit_missing_rejected():
    with pytest.raises(ValueError,match="six BPAT"):
        audit(sample().iloc[:-1])

def test_ps_unit_not_separate_from_storage_sheet_rejected():
    q=sample();q.loc[0,"storage_sheet_join"]="both"
    with pytest.raises(ValueError,match="six BPAT"):
        audit(q)

def test_total_capacity_wrong_rejected():
    q=sample();q.loc[q.generator_id.eq("PG7"),"nameplate_capacity_mw"]=55
    with pytest.raises(ValueError,match="Source-nameplate"):
        audit(q)

def test_plant_ba_not_verified_rejected():
    q=sample();q.loc[0,"plant_id"]="9999"
    with pytest.raises(ValueError,match="six BPAT"):
        audit(q)
