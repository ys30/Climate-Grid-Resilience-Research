import pandas as pd
import pytest
from grid_resilience.multi_technology_factorial import run

def inputs(tmp_path):
    ts=["2024-07-01T00:00Z","2024-07-01T01:00Z"]
    d=tmp_path/"d.csv"; w=tmp_path/"w.csv"; c=tmp_path/"c.csv"; a=tmp_path/"a.csv"
    pd.DataFrame([{"timestamp":t,"ba":"CISO","demand_mw":50} for t in ts]).to_csv(d,index=False)
    pd.DataFrame([{"timestamp":t,"ba":"CISO","temperature_c":31} for t in ts]).to_csv(w,index=False)
    pd.DataFrame([{"ba":"CISO","technology":"gas","capacity_mw":100,"marginal_cost":70}]).to_csv(c,index=False)
    pd.DataFrame([{"timestamp":t,"ba":"CISO","technology":"gas","availability_pu":1} for t in ts]).to_csv(a,index=False)
    return d,w,c,a

def test_four_matched_multi_tech_scenarios(tmp_path):
    pytest.importorskip("pypsa")
    result=run(*inputs(tmp_path),tmp_path/"out",event_id="synthetic")
    assert result["n_bas"]==1
    assert result["total_nonadditive_interaction_mwh"]==pytest.approx(0,abs=1e-5)
    out=pd.read_csv(tmp_path/"out"/"multi_technology_factorial_dispatch.csv")
    assert set(out.scenario)=={"baseline","heat_only","wind_only","heat_wind"}
    assert len(out)==4
    audit=pd.read_csv(tmp_path/"out"/"factorial_interaction_audit.csv")
    assert len(audit)==1
    assert set(["baseline","heat_only","wind_only","heat_wind","interaction_mwh"]).issubset(audit.columns)
    row=audit.iloc[0]
    assert row.interaction_mwh==pytest.approx(row.heat_wind-row.heat_only-row.wind_only+row.baseline)
    assert result["factorial_accounting_verified"] is True
    assert result["interaction_is_causal_attribution"] is False
    assert result["system_nonadditive_interaction_mwh"]==pytest.approx(result["total_nonadditive_interaction_mwh"])

def test_missing_weather_rejected(tmp_path):
    pytest.importorskip("pypsa")
    paths=inputs(tmp_path)
    pd.read_csv(paths[1]).iloc[:-1].to_csv(paths[1],index=False)
    with pytest.raises(ValueError,match="coverage mismatch"):
        run(*paths,tmp_path/"out")


def test_four_scenarios_with_finite_storage(tmp_path):
    pytest.importorskip("pypsa")
    paths = inputs(tmp_path)
    capacity = pd.read_csv(paths[2])
    capacity["capacity_mw"] = 0
    capacity.to_csv(paths[2], index=False)
    storage = tmp_path / "storage.csv"
    pd.DataFrame([{
        "ba": "CISO", "power_mw": 50, "energy_mwh": 50,
        "efficiency_store": 1, "efficiency_dispatch": 1,
        "initial_soc_fraction": 1,
    }]).to_csv(storage, index=False)
    result = run(*paths, tmp_path / "out", event_id="storage_synthetic", storage=storage)
    assert result["n_bas"] == 1
    summary = pd.read_csv(tmp_path / "out" / "multi_technology_factorial_dispatch.csv")
    assert set(summary.scenario) == {"baseline", "heat_only", "wind_only", "heat_wind"}
    baseline = summary.loc[summary.scenario == "baseline", "unserved_energy_mwh"].iloc[0]
    heat = summary.loc[summary.scenario == "heat_only", "unserved_energy_mwh"].iloc[0]
    assert baseline == pytest.approx(50, abs=1e-4)
    assert heat > baseline
    assert summary.loc[summary.scenario == "wind_only", "unserved_energy_mwh"].iloc[0] == pytest.approx(baseline, abs=1e-4)
    for scenario in ("baseline", "heat_only", "wind_only", "heat_wind"):
        soc = pd.read_csv(tmp_path / "out" / "solved" / scenario / "storage_soc_mwh.csv")
        assert soc["CISO_battery"].between(-1e-4, 50 + 1e-4).all()
