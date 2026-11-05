import io
import urllib.error
from grid_resilience.srp_ecmps_production_access_probe import request_status

class Response:
    status = 200
    headers = {"Content-Type": "application/json"}
    def __init__(self, data):
        self.data = io.BytesIO(data)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def read(self, n):
        return self.data.read(n)

def test_success_is_not_historical_plan_admission():
    value = request_status("141", opener=lambda req, timeout: Response(b'{"monitorPlanId":"X"}'))
    assert value["result"] == "json_source_received_schema_unreviewed"
    assert value["admitted_monitoring_plan_rows"] == 0
    assert not value["generator_mapping_verified"]

def test_authorization_does_not_mean_no_units():
    def denied(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", {}, None)
    value = request_status("55129", opener=denied)
    assert value["result"] == "authorization_blocker"
    assert value["admitted_monitoring_plan_rows"] == 0

def test_bad_parameters_are_not_false_negative_units():
    def invalid(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 400, "Bad Request", {}, None)
    assert request_status("147", opener=invalid)["result"] == "request_parameter_or_schema_blocker"

def test_reject_off_target():
    import pytest
    with pytest.raises(ValueError, match="Unexpected"):
        request_status("999")

def test_api_key_in_header_not_url():
    def check(req, timeout):
        assert req.headers["X-api-key"] == "TEST_KEY"
        assert "TEST_KEY" not in req.full_url
        return Response(b"[]")
    request_status("141", opener=check, api_key="TEST_KEY")
