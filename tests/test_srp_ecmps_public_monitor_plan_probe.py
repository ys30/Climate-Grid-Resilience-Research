import json
import pytest
from grid_resilience.srp_ecmps_public_monitor_plan_probe import acquire, inspect_response

def test_http_403_is_access_blocker_not_zero_units():
    rows, manifest, body = acquire(fetch=lambda url: (403, b""))
    assert rows == [] and body is None
    assert manifest["http_access_blocked"]
    assert not manifest["data_admitted"]
    assert not manifest["2024_monitoring_plan_verified"]

def test_http_200_official_inventory_still_not_2024_physical_generator_map():
    data = {"items": [{"id": "plan-1", "orisCode": 141, "name": "A",
                       "beginReportPeriodId": 12, "monitoringLocationData": [],
                       "unitStackConfigurationData": []}]}
    rows, manifest, body = acquire(fetch=lambda url: (200, json.dumps(data).encode()))
    assert len(rows) == 1
    assert manifest["data_admitted"]
    assert not rows[0]["2024_effective_plan_validated"]
    assert not rows[0]["eia_generator_physical_identity_validated"]
    assert not manifest["physical_eia_generator_mapping_verified"]
    assert len(manifest["source_response_sha256"]) == 64

def test_reject_wrong_oris_in_response():
    with pytest.raises(ValueError, match="Unexpected source plant"):
        inspect_response({"items":[{"id":"1","orisCode":999}]}, "url")

def test_reject_missing_id():
    with pytest.raises(ValueError, match="missing ID"):
        inspect_response({"items":[{"orisCode":141}]}, "url")

def test_reject_duplicate_plan_ids():
    with pytest.raises(ValueError, match="Duplicate official"):
        inspect_response({"items":[{"id":"1","orisCode":141},{"id":"1","orisCode":141}]}, "url")

def test_reject_wrong_payload_shape():
    with pytest.raises(ValueError, match="items list"):
        inspect_response({"records":[]}, "url")

def test_reject_empty_body_on_success():
    with pytest.raises(ValueError, match="empty or oversized"):
        acquire(fetch=lambda url: (200, b""))
