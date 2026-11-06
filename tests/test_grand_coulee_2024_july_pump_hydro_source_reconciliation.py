import pandas as pd
import pytest
from grid_resilience.grand_coulee_2024_july_pump_hydro_source_reconciliation import audit

def sample():
    dates=pd.date_range("2024-07-01",periods=31,freq="D").strftime("%Y-%m-%d")
    usace=pd.DataFrame({"date":dates,
      "usace_banks_lake_pumping_electricity_mwh":[5000.]*30+[25641.],
      "usace_banks_lake_pump_flow_kcfs":[5.]*31,
      "usace_banks_lake_reported_elev_ft":[1568.]*31,
      "usace_roosevelt_midnight_elev_ft":[1286.]*31})
    banks=pd.DataFrame({"date":dates,"elevation_ft":[1568.]*31})
    roosevelt=pd.DataFrame({"date":dates,
      "lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29":[1286.]*31})
    return usace,banks,roosevelt

def test_real_31day_project_pump_energy_not_ps_discharge():
    rows,m=audit(*sample())
    assert len(rows)==31 and m["actual_USACE_Banks_pumping_July_2024_complete_31days_MWh"]==175641.
    assert m["actual_USACE_Banks_pumping_July_1_28_2024_28day_MWh"]==140000
    assert m["USACE_pump_MWh_is_whole_Banks_irrigation_site_not_PG7_PG12_only"]
    assert not m["usable_electric_PS_MWh_or_reservoir_water_balance_calibrated"]
    scope = m["hypothetical_314mw_ps_scope_diagnostic"]
    assert scope["project_pumping_observation_days"] == 31
    assert scope["project_pumping_reported_total_mwh"] == 175641.0
    assert scope["hypothetical_ps_only_max_daily_charge_mwh"] == 7536.0
    assert scope["project_daily_energy_above_hypothetical_ps_envelope_days"] == 1
    assert scope["ps_charge_energy_disaggregated"] is False

def test_missing_actual_site_pump_energy_rejected():
    a,b,c=sample();a.loc[1,"usace_banks_lake_pumping_electricity_mwh"]=None
    with pytest.raises(ValueError,match="missing observed"):
        audit(a,b,c)

def test_different_official_source_cohort_rejected():
    a,b,c=sample();c=c.iloc[:-1]
    with pytest.raises(ValueError,match="missing/duplicate"):
        audit(a,b,c)

def test_month_energy_total_must_match_independent_usace_source():
    a,b,c=sample();a.loc[1,"usace_banks_lake_pumping_electricity_mwh"]=1000.
    with pytest.raises(ValueError,match="checksum"):
        audit(a,b,c)
