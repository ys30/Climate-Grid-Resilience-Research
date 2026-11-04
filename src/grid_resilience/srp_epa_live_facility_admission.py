"""Probe documented EPA production CAM facilities records for three SRP ORIS IDs.

This admission check explicitly distinguishes HTTP/retrieval, payload shape,
facility identity, combustion-unit identifiers, and valid EIA electrical unit
matches. Do NOT infer 2024 monitoring status from current facility metadata.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ORIS=("141","55129","147")
BASE="https://api.epa.gov/easey/facilities-mgmt/facilities"


def assess_response(oris,status,raw):
    base={"requested_oris":str(oris),"http_status":int(status),
          "byte_length":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),
          "retrieval_success":False,"facility_identity_verified":False,
          "monitoring_units_verified":False,"hourly_electrical_net_output_verified":False,
          "observed_heat_derating_verified":False}
    if status!=200:
        base["reason"]="non_200_api_status"
        return base
    try:
        payload=json.loads(raw)
    except (ValueError,UnicodeDecodeError):
        base["reason"]="not_valid_json"
        return base
    if not isinstance(payload,(dict,list)):
        base["reason"]="unexpected_top_level_json"
        return base
    base["retrieval_success"]=True
    # An API resource path may use an internal facility ID rather than
    # EIA/ORIS. Admit identity only from an explicit field in the response.
    items=payload if isinstance(payload,list) else [payload]
    fields=("orisCode","orisPlCode","orisplCode","orisPlantCode")
    found=[]
    for item in items:
        if not isinstance(item,dict):continue
        for key in fields:
            val=item.get(key)
            if val is not None and str(val).strip().lstrip("0")==str(oris):
                found.append(item)
                break
    if not found:
        base["reason"]="oris_identity_not_verified_from_payload"
        base["top_level_fields"]=sorted(payload) if isinstance(payload,dict) else []
        return base
    base["facility_identity_verified"]=True
    base["reason"]="facility_identity_verified_monitoring_not_admitted"
    base["matching_facility_records"]=len(found)
    base["explicit_unit_fields"]={k:sum(1 for item in found if k in item)
                                  for k in ("units","unitData","monitoringLocations")}
    # Facility response may have nested units, but that is not a verified
    # unit-generator relationship nor 2024 monitoring plan.
    return base


def probe(output,transport=None):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    results=[]
    for oris in ORIS:
        url=f"{BASE}/{oris}"
        try:
            if transport is None:
                with urlopen(Request(url,headers={"User-Agent":"ClimateGridResilienceResearch/1.0",
                                                "Accept":"application/json"}),timeout=40) as resp:
                    status=resp.status
                    raw=resp.read(3_000_001)
            else:
                status,raw=transport(url)
        except HTTPError as exc:
            status=exc.code
            raw=exc.read(3_000_001)
        except (URLError,OSError,TimeoutError) as exc:
            results.append({"requested_oris":oris,"url":url,
                "retrieval_success":False,"facility_identity_verified":False,
                "error_class":type(exc).__name__,
                "hourly_electrical_net_output_verified":False,
                "observed_heat_derating_verified":False})
            continue
        if not isinstance(raw,bytes) or len(raw)>3_000_000:
            raise ValueError("Invalid response size or encoding")
        result=assess_response(oris,status,raw)
        result["url"]=url
        # Do not publish unreviewed raw API records.
        results.append(result)
    manifest={
        "endpoint":"EPA production facilities management: GET /facilities/{id}",
        "resource_id_may_not_equal_oris":True,
        "requested_oris":list(ORIS),
        "results":results,
        "all_three_facility_identities_verified":bool(len(results)==3 and
          all(z["facility_identity_verified"] for z in results)),
        "2024_ecmps_monitoring_plan_admitted":False,
        "epa_unit_to_eia_generator_crosswalk_certified":False,
        "measured_hourly_electric_net_mw_admitted":False,
        "high_temperature_derating_calibrated":False,
    }
    (out/"epa_live_facility_admission_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
    return manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    a=p.parse_args()
    probe(a.output)


if __name__=="__main__":
    main()
