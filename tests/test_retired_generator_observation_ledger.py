import pandas as pd
import pytest
from grid_resilience.retired_generator_observation_ledger import reconcile

def inputs():
    obs=pd.DataFrame([
        dict(plant_id="058109",generator_id="TG1",reported_ba="BPAT",period="2024-01",generation_mwh=125.0),
        dict(plant_id="356",generator_id="5",reported_ba="CISO",period="2024-01",generation_mwh=0.0)])
    status=pd.DataFrame([
        dict(plant_id="58109",generator_id="TG1",exact_sheet_matches="Retired and Canceled",exact_reported_statuses="RE")])
    return obs,status

def test_retains_nonzero_retired_energy_and_zero_observation():
    o,s=inputs();r=reconcile(o,s)
    assert r.observed_mwh_retained.sum()==125.0
    assert r.iloc[0].identity_review_group=="2024_retired_or_canceled_sheet"
    assert r.iloc[1].identity_review_group=="not_in_status_exceptions"
    assert not r.eligible_for_2024_operable_capacity.any()

def test_duplicate_status_identity_rejected():
    o,s=inputs()
    with pytest.raises(ValueError,match="Duplicate status"):
        reconcile(o,pd.concat([s,s]))

def test_duplicate_observed_rows_rejected():
    o,s=inputs()
    with pytest.raises(ValueError,match="Duplicate generator"):
        reconcile(pd.concat([o,o.iloc[[0]]]),s)

def test_missing_observed_mwh_rejected():
    o,s=inputs();o.loc[0,"generation_mwh"]=None
    with pytest.raises(ValueError,match="Missing or nonfinite"):
        reconcile(o,s)
