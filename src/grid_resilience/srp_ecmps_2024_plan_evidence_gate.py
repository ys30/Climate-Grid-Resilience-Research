"""Admission of dated ECMPS monitoring-plan unit/stack evidence.

Input is a normalized extract of independently retrieved public monitoring plans,
NOT a generator-mapping table. Never infer a GT generator from a matching name.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

TARGET_UNITS = {
    "141": {"1", "2", "3", "7", "8"},
    "55129": {"DBG1", "DBG2", "DBG4", "DBG5"},
    "147": {"K-7"},
}
START = pd.Timestamp("2024-07-01")
END = pd.Timestamp("2024-08-01")  # exclusive


def audit(rows):
    required = {"facility_id", "epa_unit_id", "stack_pipe_id",
                "begin_date", "end_date", "source_plan_id",
                "source_url", "source_sha256"}
    if not required.issubset(rows.columns):
        raise ValueError("Missing monitoring-plan source evidence columns")
    x = rows.copy()
    for col in ("facility_id", "epa_unit_id", "stack_pipe_id",
                "source_plan_id", "source_url", "source_sha256"):
        x[col] = x[col].astype("string").str.strip()
    x["facility_id"] = x.facility_id.str.replace(r"^0+(?=[0-9])", "", regex=True)
    if x[list(required - {"begin_date", "end_date"})].isna().any().any():
        raise ValueError("Missing plan identity or provenance")
    if (x[["facility_id", "epa_unit_id", "stack_pipe_id", "source_plan_id", "source_url", "source_sha256"]] == "").any().any():
        raise ValueError("Empty plan identity or provenance")
    if not x.source_sha256.str.fullmatch(r"[0-9a-fA-F]{64}").all():
        raise ValueError("Invalid original plan source SHA256")
    if not x.source_url.str.startswith("https://").all():
        raise ValueError("Monitoring plan source must be HTTPS")
    if not x.facility_id.isin(TARGET_UNITS).all():
        raise ValueError("Unexpected target facility")
    if any(unit not in TARGET_UNITS[plant] for plant, unit in zip(x.facility_id, x.epa_unit_id)):
        raise ValueError("Unexpected EPA unit identity")
    x["begin_date"] = pd.to_datetime(x.begin_date, errors="raise")
    x["end_date"] = pd.to_datetime(x.end_date, errors="coerce")
    if x.begin_date.isna().any() or x.end_date.lt(x.begin_date).fillna(False).any():
        raise ValueError("Invalid plan effective dates")
    if x.duplicated(["facility_id", "epa_unit_id", "stack_pipe_id",
                     "begin_date", "end_date", "source_plan_id"]).any():
        raise ValueError("Duplicated monitoring-plan relationship")
    # End date represents the last effective day; blank means no recorded end.
    x["july_2024_overlap"] = (x.begin_date < END) & (
        x.end_date.isna() | x.end_date.ge(START)
    )
    admitted = x.loc[x.july_2024_overlap].copy()
    output = []
    for plant, units in TARGET_UNITS.items():
        for unit in sorted(units):
            g = admitted.loc[admitted.facility_id.eq(plant) & admitted.epa_unit_id.eq(unit)]
            output.append({
                "facility_id": plant, "epa_unit_id": unit,
                "dated_ecmps_relationship_rows": len(g),
                "distinct_monitored_stack_pipe_ids": g.stack_pipe_id.nunique(),
                "monitoring_plan_location_evidence_admitted": bool(len(g)),
                "unique_eia_generator_identity_confirmed": False,
                "eia_generator_net_mw_calibrated": False,
                "thermal_derating_calibrated": False,
            })
    summary = pd.DataFrame(output).sort_values(["facility_id", "epa_unit_id"])
    manifest = {
        "evidence_type": "dated ECMPS monitoring-plan unit/stack relationship",
        "target_period_local_start": "2024-07-01",
        "target_period_local_end_exclusive": "2024-08-01",
        "target_epa_units": 10,
        "ecmps_relationship_is_eia_generator_mapping": False,
        "gross_load_is_eia_generator_net_mw": False,
        "inferred_unmatched_units_from_name": False,
        "temperature_derating_or_outage_identified": False,
    }
    return admitted, summary, manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--normalized-plan", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    detail, summary, manifest = audit(pd.read_csv(a.normalized_plan, dtype="string"))
    root = Path(a.output)
    root.mkdir(parents=True, exist_ok=True)
    detail.to_csv(root / "ecmps_2024_july_unit_stack_evidence.csv", index=False)
    summary.to_csv(root / "ecmps_2024_july_source_unit_coverage.csv", index=False)
    (root / "ecmps_2024_july_evidence_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
