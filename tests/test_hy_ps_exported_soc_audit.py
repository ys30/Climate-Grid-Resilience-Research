import numpy as np
import pandas as pd
import pytest

from grid_resilience.hy_ps_exported_soc_audit import audit_exported_hourly


def sample():
    ts = pd.date_range("2024-07-01T00:00:00Z", periods=672, freq="h")
    rows = []
    for case in ("baseline", "heat_only", "wind_only", "heat_wind"):
        charge = np.zeros(672)
        discharge = np.zeros(672)
        soc = np.zeros(672)
        charge[0] = 10.0
        discharge[1] = 8.0  # assumed 80% roundtrip; sqrt(0.8) both ways
        soc[0] = np.sqrt(0.8) * 10.0
        for i, t in enumerate(ts):
            rows.append({"resource_scenario": "PS_20MW_40MWh_eta80", "scenario": case,
                         "timestamp": t.isoformat(), "hydro_optimized_mw": 2.0,
                         "ps_charge_mw": charge[i],
                         "ps_discharge_delivered_mw": discharge[i],
                         "ps_soc_mwh": soc[i]})
    return pd.DataFrame(rows)


def check(frame):
    return audit_exported_hourly(frame, {"PS_20MW_40MWh_eta80": (20, 40, .8)})


def test_valid_closed_cycle_exports_pass():
    result = check(sample())
    assert result["groups_checked"] == 4
    assert all(g["energy_balance_audited"] for g in result["groups"])
    assert not result["measured_ps_equipment_operation"]


def test_corrupted_soc_rejected():
    x = sample()
    x.loc[0, "ps_soc_mwh"] = 20.0
    with pytest.raises(ValueError, match="energy conservation"):
        check(x)


def test_overpower_rejected():
    x = sample()
    x.loc[0, "ps_charge_mw"] = 25.0
    with pytest.raises(ValueError, match="power or capacity"):
        check(x)


def test_nonzero_terminal_soc_rejected():
    x = sample()
    x.loc[671, "ps_soc_mwh"] = 1.0
    with pytest.raises(ValueError, match="terminal SOC"):
        check(x)


def test_missing_hour_rejected():
    with pytest.raises(ValueError, match="record count"):
        check(sample().iloc[:-1])


def test_duplicate_hour_rejected():
    x = sample()
    x.loc[1, "timestamp"] = x.loc[0, "timestamp"]
    with pytest.raises(ValueError, match="Duplicated"):
        check(x)


def test_hydro_budget_reset_rejected():
    x = sample()
    x["hydro_optimized_mw"] = 1000.0
    with pytest.raises(ValueError, match="HY power or single-horizon budget"):
        check(x)
