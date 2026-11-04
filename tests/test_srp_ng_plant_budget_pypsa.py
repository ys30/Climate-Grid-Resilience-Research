"""Input-contract tests run in ordinary CI; model tests run in model workflow."""
import pandas as pd
import pytest
from grid_resilience.srp_ng_plant_budget_pypsa import validate_inputs


def inputs(year=2024,month=1):
    start=pd.Timestamp(f"{year}-{month:02d}-01",tz="UTC")
    times=pd.date_range(start,periods=pd.Period(f"{year}-{month:02d}").days_in_month*24,freq="h")
    b=pd.DataFrame({"timestamp":times,"demand_mw":100.0,"interchange_mw":0.0})
    p=pd.DataFrame({"plant_id":["001","2"],"candidate_nameplate_mw":[200.,50.],
                    "page1_signed_ng_mwh":[2000.,500.]})
    return b,p


def test_complete_utc_calendar_and_de_dup_plant_id():
    b,p=inputs()
    out,plants,times=validate_inputs(b,p)
    assert len(times)==744
    assert plants.plant_id.tolist()==["1","2"]
    assert out.demand_mw.sum()==74400.


def test_monthly_incomplete_fails():
    b,p=inputs()
    with pytest.raises(ValueError,match="Missing/duplicate"):
        validate_inputs(b.iloc[:-1],p)


def test_duplicate_plant_ids_fail():
    b,p=inputs()
    p.loc[1,"plant_id"]="0001"
    with pytest.raises(ValueError,match="Missing/duplicate plant"):
        validate_inputs(b,p)


def test_monthly_observed_above_theoretical_ceiling_fails():
    b,p=inputs()
    p.loc[0,"page1_signed_ng_mwh"]=200000.
    with pytest.raises(ValueError,match="exceeds candidate"):
        validate_inputs(b,p)


def test_negative_source_energy_fails():
    b,p=inputs()
    p.loc[0,"page1_signed_ng_mwh"]=-1.
    with pytest.raises(ValueError,match="negative NG"):
        validate_inputs(b,p)


def test_february_2024_has_696_hours():
    b,p=inputs(month=2)
    _,_,times=validate_inputs(b,p,year=2024,month=2)
    assert len(times)==696
