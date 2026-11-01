import json
from grid_resilience.hydro_calibration_readiness import assess, REQUIRED_OBS, REQUIRED_MODEL

def test_unverified_inputs_fail_closed(tmp_path):
    o=tmp_path/"obs.json";m=tmp_path/"model.json"
    o.write_text(json.dumps({"hydro_fleet_coverage_verified": True}))
    m.write_text(json.dumps({"full_month_utc_coverage": True}))
    r=assess(o,m,tmp_path/"gate.json")
    assert not r["historical_generation_comparison_eligible"]
    assert "historical_ba_crosswalk_verified" in r["missing_observation_checks"]
    assert "modeled_generation_is_net_mwh" in r["missing_model_checks"]
    assert not r["historical_adequacy_validation_certified"]

def test_all_explicitly_verified_checks_allow_generation_fit_only(tmp_path):
    o=tmp_path/"obs.json";m=tmp_path/"model.json"
    o.write_text(json.dumps({key: True for key in REQUIRED_OBS}))
    m.write_text(json.dumps({key: True for key in REQUIRED_MODEL}))
    r=assess(o,m,tmp_path/"gate.json")
    assert r["historical_generation_comparison_eligible"]
    assert r["historical_adequacy_validation_certified"] is False
