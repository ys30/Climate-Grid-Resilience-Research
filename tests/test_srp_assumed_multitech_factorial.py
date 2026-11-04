"""Synthetic assumptions must not be confused with observed generation/weather."""
import pandas as pd
import pytest

from grid_resilience.srp_assumed_multitech_factorial import (
    capacity_from_annual_roster,matched_availability,run
)


def roster():
    return pd.DataFrame({
        "plant_id":["1","1","2","3","4","5","6","7"],
        "generator_id":["A","B","C","D","E","F","G","H"],
        "plant_reported_ba":["SRP"]*7+["AZPS"],
        "energy_source_1":["NG","NG","NUC","SUB","SUN","WND","WAT","NG"],
        "nameplate_capacity_mw":[3.,2.,5.,4.,1.,2.,3.,999.]
    })


def balance():
    times=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    return pd.DataFrame({"timestamp":times,"demand_mw":25.,
                         "generation_mw":25.,"interchange_mw":0.})


def test_primary_source_roster_unique_and_excluded_other_ba():
    c,m=capacity_from_annual_roster(roster())
    assert len(c)==6
    assert m["official_ba_generator_rows"]==7
    assert m["included_generator_rows"]==7
    assert c.loc[c.technology.eq("gas"),"capacity_mw"].iloc[0]==5.
    assert m["assigned_nameplate_mw"]==20.
    assert not m["historical_calibration_certified"]


def test_solar_is_zero_during_assumed_local_night_and_all_rows_present():
    c,_=capacity_from_annual_roster(roster())
    d=balance().assign(ba="SRP")[["timestamp","ba","demand_mw"]]
    a=matched_availability(d,c)
    assert len(a)==744*len(c)
    assert a.availability_pu.between(0,1).all()
    pv=a[a.technology.eq("solar")]
    assert pv.availability_pu.eq(0).any()
    assert pv.availability_pu.gt(0).any()
    assert a[a.technology.eq("nuclear")].availability_pu.eq(.9).all()


def test_duplicate_annual_generator_identity_rejected():
    r=roster()
    with pytest.raises(ValueError,match="duplicate"):
        capacity_from_annual_roster(pd.concat([r,r.iloc[[0]]],ignore_index=True))


def test_solver_four_case_monotonicity_and_noncausal_flags(tmp_path):
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    summary,m=run(balance(),roster(),tmp_path)
    assert set(summary.scenario)=={"baseline","thermal_derating","wind_derating","compound"}
    assert summary.modeled_gap_mwh.ge(0).all()
    assert m["independent_of_eia930_fuel_generation_replay"]
    assert m["technology_availability_is_synthetic_not_meteorology"]
    assert not m["historical_calibration_certified"]
    assert (tmp_path/"compound"/"shortfall_hourly_mw.csv").exists()
