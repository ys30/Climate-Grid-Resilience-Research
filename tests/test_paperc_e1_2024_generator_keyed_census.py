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


def test_eia860_plural_batteries_and_mwh_ba_are_storage_not_unmapped():
    from grid_resilience.paperc_e1_2024_generator_keyed_census import storage_identity
    frame=pd.DataFrame([
       dict(reported_technology="Batteries",prime_mover="BA",energy_source_1="MWH"),
       dict(reported_technology="Conventional Hydroelectric",prime_mover="HY",energy_source_1="WAT"),
       dict(reported_technology="Hydroelectric Pumped Storage",prime_mover="PS",energy_source_1="WAT"),
       dict(reported_technology="Natural Gas Fired Combined Cycle",prime_mover="CT",energy_source_1="NG")
    ])
    assert storage_identity(frame).tolist()==[True,False,True,False]
