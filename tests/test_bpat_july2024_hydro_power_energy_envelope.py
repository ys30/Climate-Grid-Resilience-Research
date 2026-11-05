import pandas as pd
import pytest
from grid_resilience.bpat_july2024_hydro_power_energy_envelope import audit

def inputs():
    monthly=pd.DataFrame([{"reported_ba":"BPAT","prime_mover":"HY","period":"2024-07",
            "net_generation_mwh":6000000.,"coverage_status":"observed_source_rows"}])
    scope=pd.DataFrame([{"official_eia930_complete_july_hour_count":744,
            "eia923_observed_hy_mwh":6000000.,
            "source_reporting_grains_equivalent_certified":False}])
    solved=pd.DataFrame([{"event_id":f"JULY2024_WEEK_{i}","network_variant":"isolated",
            "scenario":"baseline","ba":"BPAT","unserved_energy_mwh":200000.}
            for i in range(1,5)])
    coverage=pd.DataFrame({"week":[1,2,3,4],"distinct_hours":[168]*4})
    return monthly,solved,scope,coverage

def test_source_confirmed_assumption_grid_and_never_dispatch_label():
    x,m=audit(*inputs())
    assert len(x)==16
    assert x.hypothetical_incremental_hydro_power_mw.nunique()==4
    assert x.assumed_fraction_of_2024_july_observed_hy_mwh.nunique()==4
    a=x.loc[(x.hypothetical_incremental_hydro_power_mw==500)&
            (x.assumed_fraction_of_2024_july_observed_hy_mwh==.1)].iloc[0]
    assert a.optimistic_total_shortfall_mitigation_ceiling_mwh==336000
    assert a.residual_original_model_shortage_floor_mwh==464000
    assert m["optimistic_bounds_not_feasible_generation_or_solver_results"]
    assert not m["historical_eens_or_real_outage_inference"]

def test_missing_month_source_rejected():
    data=list(inputs())
    data[0].loc[0,"coverage_status"]="missing_source_rows"
    with pytest.raises(ValueError,match="missing or duplicated"):
        audit(*data)

def test_month_reference_mismatch_rejected():
    data=list(inputs())
    data[2].loc[0,"eia923_observed_hy_mwh"]=999.
    with pytest.raises(ValueError,match="Conflicting"):
        audit(*data)

def test_duplicated_week_rejected():
    data=list(inputs())
    data[3].loc[3,"week"]=3
    with pytest.raises(ValueError,match="nonoverlapping"):
        audit(*data)

def test_no_31_day_as_28_day_source_substitution():
    data=list(inputs())
    data[3].loc[0,"distinct_hours"]=744
    with pytest.raises(ValueError,match="nonoverlapping"):
        audit(*data)

def test_missing_isolated_week_rejected():
    data=list(inputs())
    data[1]=data[1].iloc[:3]
    with pytest.raises(ValueError,match="four-week"):
        audit(*data)
