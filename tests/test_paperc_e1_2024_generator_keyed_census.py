import pandas as pd
import pytest
from grid_resilience.paperc_e1_2024_generator_keyed_census import REASONS


def test_exclusion_priority_is_unique():
    assert len(REASONS)==5 and len(set(REASONS))==5
    assert REASONS[0]=="admitted_single_fuel_nonstorage_candidate"


def test_disjoint_reason_labels_have_a_single_member():
    from numpy import select
    x=pd.DataFrame([
      dict(valid=False,multi=True,storage=True,supported=False),
      dict(valid=True,multi=True,storage=True,supported=False),
      dict(valid=True,multi=False,storage=True,supported=False),
      dict(valid=True,multi=False,storage=False,supported=False),
      dict(valid=True,multi=False,storage=False,supported=True)
    ])
    actual=select([~x.valid,x.multi,x.storage,~x.supported],list(REASONS)[1:],default=REASONS[0])
    assert list(actual)==list(REASONS)[1:]+list(REASONS)[:1]
