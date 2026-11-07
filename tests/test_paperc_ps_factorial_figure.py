import pandas as pd
import pytest
from grid_resilience.paperc_ps_factorial_figure import prepare, SPEC, CASES


def fixture():
    system = pd.DataFrame([{"resource_scenario":name,"scenario":case,
                            "total_model_shortage_mwh":1000000+1000*i+100*j}
                           for i,(name,_,_,_) in enumerate(SPEC)
                           for j,case in enumerate(CASES)])
    scope={"model_hours_single_contiguous_horizon":672,
           "historically_calibrated_capacity_or_outage_or_eens":False,
           "isolated_only_no_hypothetical_interties":True,
           "pumped_storage_separate_closed_zero_soc":True,
           "ps_sensitivity_configurations":[[mw,mwh,1.0 if pct==0 else .8]
                                             for _,pct,mw,mwh in SPEC]}
    audit={"groups_checked":16,"hours_per_group":672,
           "measured_ps_equipment_operation":False,"historical_eens_identified":False,
           "groups":[{"resource_scenario":name,"scenario":case,
                      "energy_balance_audited":True,"historically_calibrated":False}
                     for name,_,_,_ in SPEC for case in CASES]}
    return system,scope,audit


def test_prepare_four_access_four_factorial_complete():
    t=prepare(*fixture())
    assert len(t)==4
    assert list(t.assumed_access_pct)==[0,25,50,100]
    assert (t.interaction_mwh.abs()<.0001).all()
    assert not t.historical_calibration_certified.any()


def test_missing_factorial_case_rejected():
    s,c,a=fixture()
    with pytest.raises(ValueError,match="4x4"):
        prepare(s.iloc[:-1],c,a)


def test_missing_independent_audit_rejected():
    s,c,a=fixture()
    a["groups"][0]["energy_balance_audited"]=False
    with pytest.raises(ValueError,match="independent audit"):
        prepare(s,c,a)


def test_uncalibrated_scope_required():
    s,c,a=fixture()
    c["historically_calibrated_capacity_or_outage_or_eens"]=True
    with pytest.raises(ValueError,match="scope"):
        prepare(s,c,a)


def test_duplicate_scenario_rejected():
    s,c,a=fixture()
    s.loc[1,"scenario"]="baseline"
    with pytest.raises(ValueError,match="4x4"):
        prepare(s,c,a)
