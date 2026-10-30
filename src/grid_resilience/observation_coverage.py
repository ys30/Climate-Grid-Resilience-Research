"""Fail-closed observation completeness and provenance audit for prepared EIA-923.

This does not authenticate EIA source files. It checks declared expected
plant/technology/month keys and reporting metadata before BA aggregation.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def audit(observed_csv, expected_csv, output_dir):
    obs = pd.read_csv(observed_csv, dtype={"plant_id":str,"technology":str,"period":str,
                                           "source_file":str,"reporting_basis":str})
    exp = pd.read_csv(expected_csv, dtype={"plant_id":str,"technology":str,"period":str})
    keys = ["plant_id","technology","period"]
    required = set(keys+["generation_mwh","source_file","reporting_basis"])
    if not required.issubset(obs) or not set(keys).issubset(exp):
        raise ValueError("Missing observation or expectation schema")
    if obs.empty or exp.empty or obs[list(required)].isna().any().any() or exp[keys].isna().any().any():
        raise ValueError("Empty/null coverage input")
    for frame, fields in ((obs,keys+["source_file","reporting_basis"]),(exp,keys)):
        for field in fields:
            frame[field] = frame[field].str.strip()
            if frame[field].eq("").any():
                raise ValueError(f"Blank {field}")
    if obs.duplicated(keys).any() or exp.duplicated(keys).any():
        raise ValueError("Duplicate plant/technology/month key")
    if not obs.period.str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])").all() or not exp.period.str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])").all():
        raise ValueError("Invalid YYYY-MM period")
    observed_keys = set(map(tuple,obs[keys].itertuples(index=False,name=None)))
    expected_keys = set(map(tuple,exp[keys].itertuples(index=False,name=None)))
    if observed_keys != expected_keys:
        raise ValueError(f"Observation coverage mismatch: missing={len(expected_keys-observed_keys)}, extra={len(observed_keys-expected_keys)}")
    obs["generation_mwh"] = pd.to_numeric(obs.generation_mwh,errors="raise")
    if not obs.generation_mwh.map(lambda x: -float("inf") < float(x) < float("inf")).all():
        raise ValueError("Nonfinite generation")
    if obs.reporting_basis.nunique() != 1:
        raise ValueError("Mixed reporting bases: reconcile gross/net conventions")
    out = Path(output_dir)
    out.mkdir(parents=True,exist_ok=True)
    obs.sort_values(keys).to_csv(out/"observed_coverage_checked.csv",index=False)
    manifest = {"status":"coverage_checked_not_source_authenticated",
                "rows":len(obs),"reporting_basis":obs.reporting_basis.iloc[0],
                "source_files":sorted(obs.source_file.unique().tolist()),
                "source_authenticated":False,
                "warning":"Expectation matrix and source files require independent EIA-923 verification; zero is distinct from missing."}
    (out/"observation_coverage_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    for name in ("observed","expected","output"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    print(json.dumps(audit(a.observed,a.expected,a.output),indent=2))
if __name__=="__main__":
    main()
