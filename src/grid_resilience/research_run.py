"""End-to-end input-validation -> matched four-scenario PyPSA run.

Explicitly reject missing source provenance and unverified intertie ratings.
Passing this workflow does not certify original EIA/ERA5 reports or calibration.
"""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
from .historical_inputs import prepare
from .factorial_dispatch import solve

def fingerprint(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(demand,weather,capacity,links,output,event_id,network_variant,
        link_evidence,heat_load_coefficient=.012):
    if link_evidence not in {"hypothetical","verified_ratings"}:
        raise ValueError("Explicit link evidence classification is required")
    frame=pd.read_csv(links)
    if not {"from_ba","to_ba","capacity_mw"}.issubset(frame.columns):
        raise ValueError("Invalid link schema")
    # Self-described 'verified' status is not proof: require traceable source references
    # and manual assessment separately; no implied independent verification.
    if link_evidence=="verified_ratings":
        if not {"rating_source","rating_year"}.issubset(frame.columns):
            raise ValueError("Verified-rating claim requires per-link provenance")
        if frame[["rating_source","rating_year"]].isna().any().any() or frame.rating_source.astype(str).str.strip().eq("").any():
            raise ValueError("Incomplete per-link rating provenance")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    prepared=out/"prepared"
    provenance=prepare(demand,weather,capacity,prepared,event_id)
    result=solve(prepared/"demand.csv",prepared/"weather.csv",
                 prepared/"capacity.csv",links,out/"solved",event_id,
                 network_variant=network_variant,
                 heat_load_coefficient=heat_load_coefficient)
    report={
        "event_id":event_id,"network_variant":network_variant,
        "source_classification":"upstream-supplied; NOT independently certified",
        "intertie_evidence_classification":link_evidence,
        "warning":"Verified-rating provenance fields are not proof of actual physical BA intertie ratings.",
        "weather_response_assumption":{"temperature_increment_c":4,
                                       "wind_derating_fraction":0.30,
                                       "heat_load_coefficient":heat_load_coefficient},
        "input_sha256":{key:fingerprint(value) for key,value in {
            "demand":demand,"weather":weather,"capacity":capacity,"links":links}.items()},
        "input_validation":provenance,
        "model_result_rows":len(result),
        "status":"four scenario solves completed; historical calibration not performed"
    }
    (out/"run_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    parser=argparse.ArgumentParser()
    for x in ("demand","weather","capacity","links","output","event-id","link-evidence"):
        parser.add_argument("--"+x,required=True)
    parser.add_argument("--network-variant",default="hypothetical")
    parser.add_argument("--heat-load-coefficient",type=float,default=.012)
    a=parser.parse_args()
    if a.heat_load_coefficient<0:
        parser.error("--heat-load-coefficient cannot be negative")
    print(json.dumps(run(a.demand,a.weather,a.capacity,a.links,a.output,
                         a.event_id,a.network_variant,a.link_evidence,
                         a.heat_load_coefficient),indent=2))
if __name__=="__main__":main()
