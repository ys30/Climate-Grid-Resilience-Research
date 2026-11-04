import pandas as pd
import pytest

from grid_resilience.srp_assumed_multitech_threshold_grid import (
    validate_grid,analyze_grid,run
)


def synthetic_grid():
    # Deficit falls (or remains flat) as thermal and wind supply rise.
    return pd.DataFrame([
        {"thermal_factor":t,"wind_factor":w,
         "modeled_gap_mwh":max(0.,100.-80.*t-40.*w)}
        for t in (0.,0.5,1.) for w in (0.,0.5,1.)
    ])


def test_grid_threshold_and_discrete_interactions():
    boundary,interaction,m=analyze_grid(synthetic_grid())
    assert m["grid_points"]==9
    assert m["positive_gap_grid_points"]>0
    assert len(interaction)==4
    assert boundary.loc[boundary.wind_factor.eq(1.),"smallest_tested_thermal_factor_with_no_gap"].iloc[0]==1.
    assert not m["historical_calibration_certified"]


def test_increasing_availability_cannot_make_gap_worse():
    d=synthetic_grid()
    d.loc[d.thermal_factor.eq(1.)&d.wind_factor.eq(1.),"modeled_gap_mwh"]=999.
    with pytest.raises(AssertionError,match="monotonicity"):
        analyze_grid(d)


def test_missing_and_duplicate_factor_pairs_rejected():
    d=synthetic_grid()
    with pytest.raises(ValueError,match="Incomplete"):
        analyze_grid(d.iloc[:-1])
    with pytest.raises(ValueError,match="Duplicate"):
        analyze_grid(pd.concat([d,d.iloc[[0]]],ignore_index=True))


def test_invalid_scenario_grid_rejected():
    with pytest.raises(ValueError,match="distinct"):
        validate_grid([0.,0.],[0.,1.])
    with pytest.raises(ValueError,match="within"):
        validate_grid([0.,1.],[0.,1.1])


def test_small_four_cell_pypsa_grid_has_valid_monotonicity(tmp_path):
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    hours=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    boundary=pd.DataFrame({"timestamp":hours,"demand_mw":10.,
                           "generation_mw":10.,"interchange_mw":0.})
    roster=pd.DataFrame({
        "plant_id":["1","2","3"],"generator_id":["A","B","C"],
        "plant_reported_ba":["SRP"]*3,
        "prime_mover":["GT","WT","PV"],
        "energy_source_1":["NG","WND","SUN"],
        "nameplate_capacity_mw":[10.,3.,1.]})
    table,threshold,interaction,meta=run(
        boundary,roster,tmp_path,thermal=[0.,1.],wind=[0.,1.])
    assert len(table)==4
    assert len(threshold)==2
    assert len(interaction)==1
    assert table.modeled_gap_mwh.ge(0).all()
    assert not meta["uses_observed_generation_as_availability"]
    assert not meta["climate_attribution_certified"]
    assert (tmp_path/"threshold_grid_manifest.json").is_file()
