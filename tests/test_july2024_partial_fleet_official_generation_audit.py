import numpy as np
import pandas as pd
import pytest
from grid_resilience.july2024_partial_fleet_official_generation_audit import audit

BAS=("AZPS","BPAT","CISO","SRP")


def sample():
    ts=pd.date_range("2024-07-01T00:00:00Z",periods=672,freq="h")
    demand=pd.DataFrame([{
        "timestamp":t,"ba":ba,"demand_mw":1200.+int(ba=="SRP")*100.}
        for t in ts for ba in BAS])
    cap=pd.DataFrame([{
        "ba":ba,"gas_mw":600.,"wind_mw":100.,"source_year":2024,
        "capacity_source":"GENERIC_THERMAL_PROXY_2024_PARTIAL"}
        for ba in BAS])
    official=pd.DataFrame([{
        "Balancing Authority":ba,
        "UTC Time at End of Hour":(t+pd.Timedelta(hours=1)).strftime(
            "%m/%d/%Y %I:%M:%S %p"),
        "Demand (MW)":1200.+int(ba=="SRP")*100.,
        "Net Generation (MW)":900.+int(ba=="SRP")*200.}
        for t in ts for ba in BAS])
    solved=pd.DataFrame([{
        "event_id":f"JULY2024_WEEK_{i}","network_variant":"isolated",
        "scenario":"baseline","ba":ba,"unserved_energy_mwh":(1200.+int(ba=="SRP")*100.-650.)*168}
        for i in range(1,5) for ba in BAS])
    return demand,cap,official,solved


def test_original_model_shortage_envelope_and_reported_net_generation():
    out,m=audit(*sample())
    assert len(out)==16
    assert out.hours.eq(168).all()
    assert out.total_partial_gas_wind_nameplate_mw.eq(700.).all()
    assert out.hours_reported_ba_net_gen_above_partial_nameplate.eq(168).all()
    assert (out.modeled_shortage_above_partial_nameplate_bound_mwh>=0).all()
    assert not m["historical_real_eens_or_forced_outages_estimated"]
    assert m["observed_eia930_ba_net_gen_vs_nameplate_are_not_same_generator_cohort"]


def test_reject_one_hour_official_demand_misalignment():
    demand,cap,official,solved=sample()
    official.loc[0,"Demand (MW)"]=999.
    with pytest.raises(ValueError,match="differs from same-hour"):
        audit(demand,cap,official,solved)


def test_reject_gap_in_official_era():
    demand,cap,official,solved=sample()
    with pytest.raises(ValueError,match="Incomplete original observed EIA930"):
        audit(demand,cap,official.iloc[:-1],solved)


def test_reject_violated_nameplate_model_bound():
    demand,cap,official,solved=sample()
    solved.loc[0,"unserved_energy_mwh"]=1.
    with pytest.raises(ValueError,match="violates obvious"):
        audit(demand,cap,official,solved)


def test_nonphysical_capacity_label_rejected():
    demand,cap,official,solved=sample()
    cap.loc[0,"capacity_source"]="FULL_CALIBRATED_FLEET"
    with pytest.raises(ValueError,match="original partial-fleet proxy"):
        audit(demand,cap,official,solved)
