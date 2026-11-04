import pandas as pd
import pytest
from grid_resilience.eia930_fuel_decomposition import FUELS
from grid_resilience.srp_ng_nongas_hourly_replay import prepare_fuel_replay,compare

def inputs():
    hours=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    b=pd.DataFrame({"timestamp":hours,"demand_mw":100.,"interchange_mw":0.})
    p=pd.DataFrame({"plant_id":["1"],"candidate_nameplate_mw":[50.],
                    "page1_signed_ng_mwh":[744*40.]})
    raw=pd.DataFrame({
        "Balancing Authority":["SRP"]*744,
        "UTC Time at End of Hour":(hours+pd.Timedelta(hours=1)).strftime("%m/%d/%Y %I:%M:%S %p"),
        "Net Generation (MW)":[100.]*744,
    })
    for fuel in FUELS:
        raw["Net Generation (MW) from "+fuel]=""
    raw["Net Generation (MW) from Natural Gas"]=40.
    raw["Net Generation (MW) from Nuclear"]=60.
    for fuel in ("Coal","Hydropower and Pumped Storage","Solar","Wind","Other Fuel Sources"):
        raw["Net Generation (MW) from "+fuel]=0.
    return b,p,raw,hours

def test_source_missing_fuel_not_zero_and_category_sum():
    _,_,raw,hours=inputs()
    fuels,ng,manifest=prepare_fuel_replay(raw,hours)
    assert float(ng.sum())==44640.
    assert manifest["reported_eia930_natural_gas_mwh"]==29760.
    assert len(manifest["missing_source_fuel_categories"])==2
    assert all(not r["assumed_zero"] for r in manifest["missing_source_fuel_categories"])
    assert fuels["Nuclear"].sum()==44640.

def test_replay_fails_if_required_category_blank():
    _,_,raw,hours=inputs()
    raw["Net Generation (MW) from Nuclear"]=raw["Net Generation (MW) from Nuclear"].astype("object")
    raw.loc[0,"Net Generation (MW) from Nuclear"]=""
    with pytest.raises(ValueError,match="Missing/nonfinite"):
        prepare_fuel_replay(raw,hours)

def test_oil_present_must_not_be_silently_dropped():
    _,_,raw,hours=inputs()
    raw.loc[0,"Net Generation (MW) from All Petroleum Products"]="1"
    with pytest.raises(ValueError,match="Unexpected"):
        prepare_fuel_replay(raw,hours)

def test_missing_hour_rejected():
    _,_,raw,hours=inputs()
    with pytest.raises(ValueError,match="Incomplete"):
        prepare_fuel_replay(raw.iloc[:-1],hours)

def test_pypsa_scenario_monotonicity_and_hourly_conservation():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    b,p,raw,_=inputs()
    results,hourly,_,_=compare(b,raw,p)
    r=results.set_index("scenario")
    assert r.loc["unlimited","artificial_portfolio_gap_mwh"]<1e-4
    assert r.loc["1x_page1","artificial_portfolio_gap_mwh"]<1e-4
    assert abs(r.loc["0.75x_page1","artificial_portfolio_gap_mwh"]-7440.)<1e-3
    assert abs(r.loc["0.5x_page1","artificial_portfolio_gap_mwh"]-14880.)<1e-3
    assert (results.max_hourly_bus_residual_mw<1e-4).all()
    assert len(hourly["0.75x_page1"])==744
    assert all(not x for x in results.artificial_gap_is_observed_outage)
