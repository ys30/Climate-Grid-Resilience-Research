"""Probe EPA production ECMPS official monitoring-plan configurations, fail closed.

Only official production public GET, never a dev/test/workspace endpoint.
HTTP 403/401 is an access blocker, not an empty unit inventory.
Returned configuration is NOT a dated 2024 physical EIA generator mapping.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ENDPOINT = "https://api.epa.gov/easey/monitor-plan-mgmt/configurations"
TARGET = {"141", "55129", "147"}
LIMIT = 15_000_000


def inspect_response(payload, source_url):
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise ValueError("Official monitoring-plan response lacks items list")
    plans = payload["items"]
    rows = []
    for plan in plans:
        if not isinstance(plan, dict):
            raise ValueError("Malformed official monitoring-plan record")
        oris = str(plan.get("orisCode", "")).strip()
        if oris not in TARGET:
            raise ValueError("Unexpected source plant in monitoring-plan response")
        pid = plan.get("id")
        if not pid:
            raise ValueError("Official monitoring-plan configuration missing ID")
        locations = plan.get("monitoringLocationData")
        configurations = plan.get("unitStackConfigurationData")
        rows.append({
            "oris": oris,
            "monitor_plan_id": str(pid),
            "monitor_plan_name": str(plan.get("name", "")),
            "begin_report_period_id": plan.get("beginReportPeriodId"),
            "end_report_period_id": plan.get("endReportPeriodId"),
            "active_source_flag": plan.get("active"),
            "reported_locations": len(locations) if isinstance(locations, list) else None,
            "reported_unit_stack_configurations": (
                len(configurations) if isinstance(configurations, list) else None),
            "source_url": source_url,
            "source_is_official_production_ecmps": True,
            "2024_effective_plan_validated": False,
            "2024_unit_stack_association_validated": False,
            "eia_generator_physical_identity_validated": False,
        })
    if len({(r["oris"], r["monitor_plan_id"]) for r in rows}) != len(rows):
        raise ValueError("Duplicate official monitoring-plan IDs")
    return rows


def acquire(fetch=None):
    url = ENDPOINT + "?" + urlencode({"orisCodes": "141|55129|147"})
    result = {
        "source_url": url,
        "official_production_endpoint": True,
        "source_api_documentation": "https://api.epa.gov/easey/monitor-plan-mgmt/swagger",
        "requested_oris_codes": ["141", "55129", "147"],
        "http_status": None,
        "data_admitted": False,
        "source_monitor_plan_count": 0,
        "http_access_blocked": False,
        "not_found_means_unit_does_not_exist": False,
        "2024_monitoring_plan_verified": False,
        "physical_eia_generator_mapping_verified": False,
        "weather_to_generator_derating_calibrated": False,
    }
    try:
        if fetch:
            status, body = fetch(url)
        else:
            request = Request(url, headers={"User-Agent": "ClimateGridResilienceResearch/1.0",
                                             "Accept": "application/json"})
            with urlopen(request, timeout=65) as stream:
                status, body = stream.status, stream.read(LIMIT + 1)
    except HTTPError as exc:
        status, body = exc.code, b""
    except (URLError, TimeoutError, ConnectionError) as exc:
        result["transport_error_type"] = type(exc).__name__
        return [], result, None
    result["http_status"] = status
    if status != 200:
        result["http_access_blocked"] = status in (401, 403)
        return [], result, None
    if not body or len(body) > LIMIT:
        raise ValueError("Official source payload empty or oversized")
    parsed = json.loads(body)
    rows = inspect_response(parsed, url)
    result["source_response_sha256"] = hashlib.sha256(body).hexdigest()
    result["source_monitor_plan_count"] = len(rows)
    result["source_facility_count"] = len({r["oris"] for r in rows})
    result["data_admitted"] = bool(rows)
    return rows, result, body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    directory = Path(args.output)
    directory.mkdir(parents=True, exist_ok=True)
    rows, manifest, body = acquire()
    (directory / "ecmps_public_configuration_access_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    (directory / "ecmps_public_monitor_plan_inventory.json").write_text(
        json.dumps(rows, indent=2) + "\n")
    if body is not None:
        (directory / "ecmps_original_public_configurations_response.json").write_bytes(body)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
