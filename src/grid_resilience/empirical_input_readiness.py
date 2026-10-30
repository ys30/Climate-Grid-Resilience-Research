"""Readiness gate for empirical BA/technology/month dispatch comparisons.

The gate checks the declared provenance of model inputs. It cannot authenticate
source claims, and it never certifies historical calibration.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

REQUIRED_FIELDS={"dataset","source_url","source_year","measurement_basis","status"}
REQUIRED_DATASETS={"demand_hourly","capacity_technology","availability_hourly",
                   "observed_generation_monthly","ba_transfer_capacity"}
ALLOWED_STATUS={"official_observed","independently_audited","assumed","synthetic","missing"}

def assess(provenance_csv, output):
    frame=pd.read_csv(provenance_csv,dtype=str,keep_default_na=False)
    if not REQUIRED_FIELDS.issubset(frame) or frame.empty:
        raise ValueError("Missing provenance schema")
    if frame.dataset.duplicated().any() or frame.dataset.eq("").any():
        raise ValueError("Duplicate or blank dataset name")
    if not REQUIRED_DATASETS.issubset(set(frame.dataset)):
        raise ValueError("Missing required model input datasets")
    if not set(frame.status).issubset(ALLOWED_STATUS):
        raise ValueError("Unsupported evidence status")
    if frame[list(REQUIRED_FIELDS)].apply(lambda col: col.str.strip().eq("")).any().any():
        raise ValueError("Empty provenance field")
    selected=frame.set_index("dataset").loc[sorted(REQUIRED_DATASETS)]
    unverified=selected[~selected.status.isin({"official_observed","independently_audited"})]
    result={
        "inputs_declared":sorted(REQUIRED_DATASETS),
        "unverified_datasets":sorted(unverified.index.tolist()),
        "empirical_input_readiness":len(unverified)==0,
        "provenance_authenticated":False,
        "historical_calibration_certified":False,
        "warning":"Declared status is not independently checked. Full-fleet coverage, BA topology, units, hourly timelines and held-out evaluation require separate verification."
    }
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    (out/"empirical_input_readiness.json").write_text(json.dumps(result,indent=2)+"\n")
    if unverified.empty:
        return result
    # Diagnostics are written, but no positive readiness claim is made.
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--provenance",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(assess(a.provenance,a.output),indent=2))
if __name__=="__main__":
    main()
