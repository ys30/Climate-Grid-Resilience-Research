import pandas as pd
import pytest

from grid_resilience.srp_fossil_nuclear_decoupled_grid import (
    summarize,validate_factors,run
)


def sample():
    return pd.DataFrame([
        {"fossil_factor":f,"nuclear_factor":n,"wind_factor":w,
         "modeled_gap_mwh":max(0.,100.-85*f-15*n-8*w)}
        for f in (0.5,1.) for n in (0.75,1.) for w in (0.,1.)
    ])


def test_decoupled_brackets_and_monotonicity():
    bounds,m=summarize(sample())
    assert m["grid_scenarios"]==8
    assert len(bounds)==4
    assert m["availability_monotonicity_verified"]
    assert not m["historical_calibration_certified"]


def test_monotonicity_violation_rejected():
    s=sample()
    s.loc[s.fossil_factor.eq(1.)&s.nuclear_factor.eq(1.)&
          s.wind_factor.eq(1.),"modeled_gap_mwh"]=1000.
    with pytest.raises(AssertionError,match="Monotonicity"):
        summarize(s)


def test_incomplete_and_duplicate_grid_rejected():
    s=sample()
    with pytest.raises(ValueError,match="Incomplete"):
        summarize(s.iloc[:-1])
    with pytest.raises(ValueError,match="Duplicate"):
        summarize(pd.concat([s,s.iloc[[0]]],ignore_index=True))


def test_factors_finite_distinct_within_zero_one():
    with pytest.raises(ValueError,match="Invalid or duplicate"):
        validate_factors([0.5,0.5],"fossil")
    with pytest.raises(ValueError,match="Invalid or duplicate"):
        validate_factors([0.5,1.5],"nuclear")


def test_two_by_two_by_two_pypsa_synthetic_integration(tmp_path):
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    ts=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    boundary=pd.DataFrame({"timestamp":ts,"demand_mw":10.,
                           "generation_mw":10.,"interchange_mw":0.})
    roster=pd.DataFrame({
        "plant_id":["1","2","3"],"generator_id":["A","B","C"],
        "plant_reported_ba":["SRP"]*3,
        "prime_mover":["GT","ST","WT"],
        "energy_source_1":["NG","NUC","WND"],
        "nameplate_capacity_mw":[10.,4.,2.]})
    result,bounds,m=run(boundary,roster,tmp_path,
                        fossil=(0.5,1.),nuclear=(0.75,1.),wind=(0.,1.))
    assert len(result)==8
    assert len(bounds)==4
    assert m["eia930_generation_replayed"] is False
    assert m["simulated_gap_is_actual_unserved_electricity"] is False
    assert (tmp_path/"decoupled_grid_manifest.json").exists()
