"""Bounded, read-only probe of the EPA production ECMPS monitor-plan export API.

A network response is *access evidence*, not historical monitoring-plan
admission or generator identity. Never call dev/perf; never print credentials.
"""
import argparse
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://api.epa.gov/easey/monitor-plan-mgmt/plans/export"
PLANTS = ("141", "55129", "147")
MAX_BYTES = 5_000_000


def request_status(plant, *, opener=None, api_key=None):
    if str(plant) not in PLANTS:
        raise ValueError("Unexpected EPA target plant")
    url = BASE + "?" + urllib.parse.urlencode({"orisCode": str(plant)})
    headers = {"Accept": "application/json",
               "User-Agent": "ClimateGridResilienceResearch/1.0"}
    if api_key:
        headers["x-api-key"] = api_key
    req = urllib.request.Request(url, headers=headers, method="GET")
    if opener is None:
        opener = urllib.request.urlopen
    payload = b""
    status = None
    content_type = ""
    try:
        with opener(req, timeout=30) as response:
            status = int(response.status)
            content_type = response.headers.get("Content-Type", "")
            payload = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        content_type = exc.headers.get("Content-Type", "") if exc.headers else ""
        # Deliberately don't save response body (possibly security headers).
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
        return {"plant_id": str(plant), "request_url": url, "http_status": None,
                "result": "network_error", "error_type": type(exc).__name__,
                "admitted_monitoring_plan_rows": 0,
                "generator_mapping_verified": False}
    if len(payload) > MAX_BYTES:
        return {"plant_id": str(plant), "request_url": url, "http_status": status,
                "result": "oversize_not_admitted", "admitted_monitoring_plan_rows": 0,
                "generator_mapping_verified": False}
    result = "http_error"
    if status == 200:
        try:
            parsed = json.loads(payload)
            result = "json_source_received_schema_unreviewed" if isinstance(parsed, (dict, list)) else "unexpected_json_shape"
        except (ValueError, UnicodeError):
            result = "non_json_response_not_admitted"
    elif status in (401, 403):
        result = "authorization_blocker"
    elif status in (400, 422):
        result = "request_parameter_or_schema_blocker"
    elif status == 404:
        result = "endpoint_or_resource_not_found_unresolved"
    return {"plant_id": str(plant), "request_url": url,
            "http_status": status, "content_type": content_type,
            "result": result,
            "response_sha256": hashlib.sha256(payload).hexdigest() if status == 200 else None,
            "response_bytes": len(payload) if status == 200 else None,
            "admitted_monitoring_plan_rows": 0,
            "generator_mapping_verified": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    key = os.getenv("EPA_CAM_API_KEY") or None
    result = [request_status(plant, api_key=key) for plant in PLANTS]
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    report = {"endpoint": BASE, "environment": "production",
              "probed_sites": list(PLANTS), "api_key_supplied": bool(key),
              "responses": result,
              "original_plan_bytes_archived": False,
              "dated_monitoring_plan_relationships_admitted": False,
              "physical_eia_generator_identity_verified": False,
              "no_result_is_not_no_monitoring_plan": True}
    (out / "production_ecmps_access_probe.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
