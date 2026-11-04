import pandas as pd
import pytest
from itertools import product

from grid_resilience.srp_gas_coal_nuclear_grid import summarize,run


def synthetic():
    return pd.DataFrame([
        {"gas_factor":g,"coal_factor":c,"nuclear_factor":n,
         "wind_factor":w,"modeled_gap_mwh":max(0.,100-60*g-20*c-30*n-10*w)}
        for g,c,n,w in product((0.5,1.),(0.5,1.),(0.75,1.),(0.,1.))
    ])


def test_cartesian_completeness_monotonicity_and_gas_brackets():
    b,m=summarize(synthetic())
    assert m["scenario_count"]==16
    assert m["monotonicity_verified"] and not m["historical_calibration_certified"]
    assert len(b)==8


def test_duplicate_missing_or_nonmonotone_values_fail():
    s=synthetic()
    with pytest.raises(ValueError,match="Incomplete"):
        summarize(s.iloc[:-1])
    with pytest.raises(ValueError,match="Duplicate"):
        summarize(pd.concat([s,s.iloc[:1]],ignore_index=True))
    s.loc[(s.gas_factor==1.)&(s.coal_factor==1.)&
          (s.nuclear_factor==1.)&(s.wind_factor==1.),"modeled_gap_mwh"]=999
    with pytest.raises(AssertionError,match="monotonicity"):
        summarize(s)


def test_small_complete_grid_uses_solver_without_replay(tmp_path):
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    ts=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    balance=pd.DataFrame({"timestamp":ts,"demand_mw":10.,
                          "generation_mw":10.,"interchange_mw":0.})
    roster=pd.DataFrame({
        "plant_id":["1","2","3","4"],
        "generator_id":["G","C","N","W"],
        "plant_reported_ba":["SRP"]*4,
        "prime_mover":["GT","ST","ST","WT"],
        "energy_source_1":["NG","SUB","NUC","WND"],
        "nameplate_capacity_mw":[8.,3.,2.,1.]})
    table,boundaries,manifest=run(balance,roster,tmp_path,
        gas=(0.5,1.),coal=(0.5,1.),nuclear=(0.75,1.),wind=(0.,1.))
    assert len(table)==16 and len(boundaries)==8
    assert manifest["historical_eia930_generation_replayed"] is False
    assert manifest["artificial_gap_is_observed_eens"] is False
    assert not manifest["historical_calibration_certified"]
