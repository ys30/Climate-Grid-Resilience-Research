import json
from grid_resilience.srp_epa_live_facility_admission import assess_response,probe

def test_explicit_oris_identity_required():
    v=assess_response("141",200,json.dumps({"id":141,"units":[{"unitId":"1"}]}).encode())
    assert v["retrieval_success"]
    assert not v["facility_identity_verified"]
    assert not v["hourly_electrical_net_output_verified"]

def test_verified_facility_does_not_admit_unit_or_net_mw():
    v=assess_response("141",200,json.dumps({"orisCode":141,"units":[{"unitId":"GT1"}]}).encode())
    assert v["facility_identity_verified"]
    assert not v["monitoring_units_verified"]
    assert not v["hourly_electrical_net_output_verified"]

def test_bad_http_status_never_implies_unmonitored():
    v=assess_response("147",403,b"Forbidden")
    assert not v["retrieval_success"]
    assert v["reason"]=="non_200_api_status"

def test_three_facility_probe_records_sha_and_no_2024_calibration(tmp_path):
    def fake(url):
        return 200,json.dumps({"orisCode":url.split("/")[-1]}).encode()
    m=probe(tmp_path,transport=fake)
    assert m["all_three_facility_identities_verified"]
    assert not m["2024_ecmps_monitoring_plan_admitted"]
    assert not m["measured_hourly_electric_net_mw_admitted"]
    assert len(m["results"])==3

def test_wrong_internal_id_does_not_validate_facility(tmp_path):
    m=probe(tmp_path,transport=lambda _: (200,b'{"id":141}'))
    assert not m["all_three_facility_identities_verified"]
    assert not m["epa_unit_to_eia_generator_crosswalk_certified"]
