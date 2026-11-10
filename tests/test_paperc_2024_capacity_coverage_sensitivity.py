import pandas as pd
import pytest
from grid_resilience.paperc_2024_capacity_coverage_sensitivity import (
    capacity_grid, summarize, validate_original_no_change, FRACTIONS, WEEKS, VARIANTS
)

BAS=("AZPS","BPAT","CISO","SRP")
SCENARIOS=("baseline","heat_only","wind_only","heat_wind")


def inputs():
    d=pd.DataFrame([dict(timestamp=t,ba=b,demand_mw=100+10*i) for t in
                    pd.date_range("2024-07-01",periods=168,freq="h",tz="UTC")
                    for i,b in enumerate(BAS)])
    c=pd.DataFrame([dict(ba=b,gas_mw=80.,wind_mw=20.,
                         source_year=2024,capacity_source="GENERIC_THERMAL_PROXY")
                    for b in BAS])
    return c,d


def model_rows():
    return pd.DataFrame([
        dict(fraction=frac,week=week,network_variant=net,scenario=case,ba=ba,
             unserved_energy_mwh={ "baseline":100, "heat_only":110,
                                   "wind_only":120,"heat_wind":150}[case]
                                    - frac*50 + week)
        for frac in FRACTIONS for week in WEEKS for net in VARIANTS
        for case in SCENARIOS for ba in BAS
    ])


def original_summary():
    return pd.DataFrame([
        dict(event_id=f"JULY2024_WEEK_{w}",network_variant=net,ba=ba,
             baseline_shortage_mwh=(100+w)*(4 if ba=="SYSTEM" else 1),
             modeled_factorial_interaction_mwh=80 if ba=="SYSTEM" else 20)
        for w in WEEKS for net in VARIANTS for ba in (*BAS,"SYSTEM")
    ])


def test_capacity_is_frozen_from_week_one_observed_peak():
    c,d=inputs()
    grid=capacity_grid(c,d)
    assert list(grid)==list(FRACTIONS)
    assert grid[0].gas_mw.eq(80).all()
    assert list(grid[0.25].additional_hypothetical_firm_mw)==[25,27.5,30,32.5]
    assert grid[0.50].gas_mw.iloc[0]==130


def test_fail_closed_source_coverage():
    c,d=inputs()
    with pytest.raises(ValueError,match="incomplete"):
        capacity_grid(c,d.iloc[:-1])


def test_scenario_matrix_and_ba_system_reconcile():
    x=summarize(model_rows())
    assert len(x)==120
    assert x.loc[x.ba.eq("SYSTEM"),"modeled_heat_wind_second_difference_mwh"].eq(80).all()
    assert validate_original_no_change(x,original_summary())==0


def test_original_reproduction_mismatch_fails():
    x=summarize(model_rows())
    o=original_summary()
    o.loc[0,"baseline_shortage_mwh"]+=1
    with pytest.raises(ValueError,match="REPRODUCTION"):
        validate_original_no_change(x,o)


def test_missing_one_scenario_fails():
    with pytest.raises(ValueError,match="coverage"):
        summarize(model_rows().iloc[:-1])


def test_duplicate_model_output_fails():
    x=model_rows()
    with pytest.raises(ValueError,match="coverage"):
        summarize(pd.concat([x,x.iloc[[0]]],ignore_index=True))
