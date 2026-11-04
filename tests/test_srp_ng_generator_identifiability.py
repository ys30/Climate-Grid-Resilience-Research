import pandas as pd
import pytest
from grid_resilience.srp_ng_generator_identifiability import audit


def candidates():
    return pd.DataFrame({
        "plant_id":["1","1","2","3"],
        "prime_mover":["CT","GT","ST","GT"],
        "reported_fuel":["NG"]*4,
        "page1_signed_net_mwh":[10.,20.,-2.,5.],
        "fuel_candidate_units":[2,1,0,3],
        "fuel_candidate_generator_ids":["A;B","C","","D;E;F"]
    })


def test_signed_mwh_and_candidate_classes_conserved():
    rows,groups,plants,m=audit(candidates())
    assert m["source_rows"]==4
    assert m["total_page1_signed_mwh"]==33.
    assert m["multiple_candidate_signed_mwh"]==15.
    assert m["multiple_candidate_rows"]==2
    assert m["single_candidate_rows"]==1
    assert m["no_candidate_rows"]==1
    assert groups.source_rows.sum()==4
    assert groups.source_signed_mwh.sum()==33.
    assert not m["candidate_identity_is_generator_dispatch_attribution"]
    assert not m["historical_calibration_certified"]


def test_invalid_candidate_counts_fail_closed():
    d=candidates()
    d.loc[0,"fuel_candidate_units"]=-1
    with pytest.raises(ValueError,match="Invalid"):
        audit(d)
    d=candidates()
    d.loc[0,"fuel_candidate_units"]=1.5
    with pytest.raises(ValueError,match="Invalid"):
        audit(d)


def test_nonfinite_observed_generation_fails_closed():
    d=candidates()
    d.loc[0,"page1_signed_net_mwh"]=float("inf")
    with pytest.raises(ValueError,match="nonfinite"):
        audit(d)


def test_no_target_fuel_fails_closed():
    with pytest.raises(ValueError,match="No source"):
        audit(candidates(),fuel="SUB")
