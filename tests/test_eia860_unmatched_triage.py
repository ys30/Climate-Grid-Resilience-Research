import pandas as pd
import pytest
from grid_resilience.eia860_unmatched_triage import triage

def sample():
    u=pd.DataFrame([
      dict(plant_id="00058109",generator_id="TG1",reported_ba="BPAT",period="2024-01"),
      dict(plant_id="58109",generator_id="TG1",reported_ba="BPAT",period="2024-02"),
      dict(plant_id="99",generator_id="GEN1",reported_ba="CISO",period="2024-01")])
    o=pd.DataFrame([
      dict(plant_id="58109",generator_id="TG2"),
      dict(plant_id="20",generator_id="A")])
    return u,o

def test_detects_same_plant_not_generator():
    r=triage(*sample())
    assert len(r)==2
    a=r[r.reported_ba=="BPAT"].iloc[0]
    assert a.unmatched_month_rows==2
    assert a.review_status=="other_generator_at_same_plant"
    assert a.other_2024_operable_ids_same_plant=="TG2"
    assert not a.identity_crosswalk_certified
    assert r[r.reported_ba=="CISO"].iloc[0].review_status=="plant_absent_from_selected_operable_inventory"

def test_duplicate_operable_key_rejected():
    u,o=sample()
    with pytest.raises(ValueError,match="duplicate operable"):
        triage(u,pd.concat([o,o.iloc[[0]]]))

def test_missing_identifier_rejected():
    u,o=sample()
    u.loc[0,"plant_id"]=None
    with pytest.raises(ValueError,match="missing identifiers"):
        triage(u,o)
