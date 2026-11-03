"""Verify one-technology exchange oracle without a solver."""
import numpy as np
import pytest
from grid_resilience.exchange_analytical_reference import reference

def test_large_import_spills_without_local_generation():
    r=reference(np.full(744,50.),np.full(744,-70.),100.)
    assert r["local_generation_mwh"]==0.
    assert r["scheduled_import_mwh"]==70*744
    assert r["spilled_mwh"]==20*744
    assert r["unserved_mwh"]==0.

def test_export_requires_local_generation():
    r=reference(np.full(744,50.),np.full(744,20.),100.)
    assert r["local_generation_mwh"]==70*744
    assert r["spilled_mwh"]==r["unserved_mwh"]==0.

def test_hourly_mixed_with_capacity_shortage():
    load=np.full(744,50.)
    exchange=np.tile([-70.,20.],372)
    r=reference(load,exchange,30.)
    assert r["local_generation_mwh"]==30*372
    assert r["unserved_mwh"]==40*372
    assert r["spilled_mwh"]==20*372
    assert r["hours_with_unserved"]==r["hours_with_spillage"]==372

@pytest.mark.parametrize("bad_capacity",[-1.,float("nan"),float("inf")])
def test_reject_bad_capacity(bad_capacity):
    with pytest.raises(ValueError):
        reference([1.],[0.],bad_capacity)

def test_reject_input_length_mismatch():
    with pytest.raises(ValueError):
        reference([1.],[0.,0.],1.)
