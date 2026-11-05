"""Admission audit of source EPA -> EIA associations without invented physical mappings.

A pinned static crosswalk is not a dated 2024 ECMPS monitoring plan.
Even an ECMPS unit-to-stack relationship is not an EIA electric generator
mapping. Emit a review queue and fail closed for physical-calibration use.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

PLANTS = {"141": {"1", "2", "3", "7", "8"},
          "55129": {"DBG1", "DBG2", "DBG4", "DBG5"},
          "147": {"K-7"}}
MISSING_STATIC = {("141", "7"), ("141", "8"),
                  ("55129", "DBG4"), ("55129", "DBG5")}


def review_queue(summary):
    required = {"oris", "epa_unit_id", "source_calendar_hour_rows",
                "direct_static_crosswalk_relationship_count",
                "linked_eia_generator_ids", "linked_eia_prime_mover_classes",
                "static_crosswalk_unit_found", "eia860_gt_generator_directly_linked",
                "2024_ecmps_monitoring_plan_verified",
                "actual_eia_generator_net_mw_validated"}
    if not required.issubset(summary.columns):
        raise ValueError("Missing required EPA/EIA source bridge fields")
    x = summary.copy()
    x["oris"] = x.oris.astype("string").str.strip()
    x["epa_unit_id"] = x.epa_unit_id.astype("string").str.strip()
    if x.duplicated(["oris", "epa_unit_id"]).any():
        raise ValueError("Duplicated EPA identity")
    actual = {(str(p), str(u)) for p, u in zip(x.oris, x.epa_unit_id)}
    expected = {(p, u) for p, units in PLANTS.items() for u in units}
    if actual != expected:
        raise ValueError("Unexpected or incomplete 10 EPA unit identity inventory")
    if not pd.to_numeric(x.source_calendar_hour_rows).eq(8784).all():
        raise ValueError("EPA annual source calendar is not complete")
    for field in ("static_crosswalk_unit_found", "eia860_gt_generator_directly_linked",
                  "2024_ecmps_monitoring_plan_verified",
                  "actual_eia_generator_net_mw_validated"):
        if x[field].isna().any() or not x[field].isin([True, False]).all():
            raise ValueError("Source evidence flags must be explicit booleans")
    n = pd.to_numeric(x.direct_static_crosswalk_relationship_count, errors="raise")
    if (n < 0).any() or not (x.static_crosswalk_unit_found == n.gt(0)).all():
        raise ValueError("Static source crosswalk counts inconsistent")
    if x["2024_ecmps_monitoring_plan_verified"].any():
        raise ValueError("Historical static crosswalk cannot certify 2024 ECMPS plans")
    if x["actual_eia_generator_net_mw_validated"].any():
        raise ValueError("Historical crosswalk cannot certify net electrical MW")
    if x["eia860_gt_generator_directly_linked"].any():
        raise ValueError("Unexpected certified GT identity: manual gate required")
    if {tuple(t) for t in x.loc[~x.static_crosswalk_unit_found,
                               ["oris", "epa_unit_id"]].itertuples(index=False, name=None)} != MISSING_STATIC:
        raise ValueError("Pinned static crosswalk discrepancy: stop and investigate")
    x["static_relationships"] = n.astype(int)
    x["priority"] = x.static_crosswalk_unit_found.map({False: "P0_missing_static_link",
                                                       True: "P1_verify_many_to_one_or_one_to_many"})
    x["source_document_to_acquire"] = "2024-effective ECMPS Monitoring Plan; unit-stack configuration; dated facility documentation"
    x["independent_eia_generator_evidence_required"] = True
    x["2024_ecmps_plan_evidence_admitted"] = False
    x["verified_physical_eia_generator_mapping"] = False
    x["generator_level_gross_to_net_conversion_allowed"] = False
    x["temperature_derating_calibration_allowed"] = False
    x = x.sort_values(["priority", "oris", "epa_unit_id"]).reset_index(drop=True)
    report = {
        "observed_epa_unit_count": len(x),
        "epa_units_with_static_crosswalk": int(x.static_crosswalk_unit_found.sum()),
        "epa_units_without_static_crosswalk": int((~x.static_crosswalk_unit_found).sum()),
        "epa_units_with_verified_2024_ecmps_plan": 0,
        "epa_units_with_verified_physical_eia_generator_mapping": 0,
        "eligible_generator_level_net_mw_calibrations": 0,
        "static_relationship_is_not_contemporaneous_ecmps_plan": True,
        "ecmps_unit_stack_is_not_eia_generator_map": True,
        "do_not_use_name_similarity_as_unit_identity": True,
        "source_basis": "Previously CI-verified 2024 EPA source + pinned EPA/EIA crosswalk",
    }
    return x, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-bridge", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    x, meta = review_queue(pd.read_csv(args.source_bridge, dtype={
        "oris": "string", "epa_unit_id": "string"}))
    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)
    x.to_csv(root / "epa_eia_2024_unit_identity_evidence_review_queue.csv", index=False)
    (root / "epa_eia_2024_identity_admission_manifest.json").write_text(
        json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))
    print(x[["oris", "epa_unit_id", "priority",
             "linked_eia_generator_ids"]].to_string(index=False))


if __name__ == "__main__":
    main()
