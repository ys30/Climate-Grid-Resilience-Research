"""Auditable end-to-end observed data preparation and modeled comparison.

All input files are supplied by the researcher. Never infer EIA provenance or
label mechanical checks as verified historical calibration.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .observation_coverage import audit
from .year_scoped_plant_ba import aggregate
from .calibration_pipeline import run as compare_full_month

def run(observed, expected, crosswalk, modeled_hourly, output, allow_partial_fleet=False):
    out = Path(output)
    # Preflight before writing: avoid misleading partial success.
    audit_dir = out / "observed_coverage"
    coverage = audit(observed, expected, audit_dir)
    checked = pd.read_csv(audit_dir / "observed_coverage_checked.csv",
                          dtype={"plant_id": str, "technology": str, "period": str})
    plant = out / "checked_plant_generation.csv"
    checked[["plant_id", "technology", "period", "generation_mwh"]].to_csv(plant, index=False)
    mapped = aggregate(plant, crosswalk, out / "ba_mapping")
    compared = compare_full_month(
        modeled_hourly, out / "ba_mapping" / "observed_ba_technology_month.csv",
        out / "comparison", allow_partial_fleet=allow_partial_fleet
    )
    manifest = {
        "status": "mechanical_audit_only_not_historical_calibration",
        "observation_coverage": coverage,
        "year_scoped_mapping": mapped,
        "generation_comparison": compared,
        "historical_calibration_certified": False,
    }
    (out / "end_to_end_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest

def main():
    p = argparse.ArgumentParser()
    for arg in ("observed", "expected", "crosswalk", "modeled-hourly", "output"):
        p.add_argument("--" + arg, required=True)
    p.add_argument("--allow-partial-fleet", action="store_true")
    a = p.parse_args()
    print(json.dumps(run(a.observed, a.expected, a.crosswalk,
                         a.modeled_hourly, a.output, a.allow_partial_fleet), indent=2))

if __name__ == "__main__":
    main()
