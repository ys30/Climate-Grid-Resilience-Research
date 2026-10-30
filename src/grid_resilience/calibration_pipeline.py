"""Fail-closed full-month generation comparison pipeline.

Hourly modeled generation -> verified calendar coverage -> matched observed
generation diagnostics. Input observational provenance remains upstream.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .monthly_generation_gate import monthly_generation
from .generation_calibration import compare

def run(hourly, observed, output, *, allow_partial_fleet=False):
    out = Path(output)
    # Verify observed input labels before creating any comparability claims.
    obs = pd.read_csv(observed)
    needed = {"ba", "technology", "period", "generation_mwh"}
    if obs.empty or not needed.issubset(obs):
        raise ValueError("Observed input missing BA/technology/period/generation")
    # Technical comparability is not established by string equality alone.
    # These model proxy categories are prohibited from observed comparisons.
    proxy = {"generic_thermal_proxy", "other", "thermal"}
    if set(obs.technology.astype(str)) & proxy:
        raise ValueError("Observed inventory contains non-comparable proxy technology")
    out.mkdir(parents=True, exist_ok=True)
    monthly_generation(hourly, out / "coverage")
    modeled = out / "coverage" / "modeled_generation_full_months.csv"
    mod = pd.read_csv(modeled)
    if set(mod.technology.astype(str)) & proxy:
        raise ValueError("Model contains generic thermal/other proxy; EIA-923 comparison prohibited")
    if not allow_partial_fleet:
        # A narrow overlap (e.g., wind-only) can be diagnostically evaluated,
        # but it must be explicitly requested to avoid whole-system claims.
        required = {"gas", "coal", "nuclear", "hydro", "solar", "wind"}
        if not required.issubset(set(mod.technology)):
            raise ValueError("Full fleet gate: missing major modeled technologies; explicitly enable partial-fleet diagnostics")
    diagnostics = compare(observed, modeled, out / "comparison")
    manifest = {
        "status": "diagnostic_only_not_calibrated",
        "full_fleet_assumption": not allow_partial_fleet,
        "partial_fleet_override": allow_partial_fleet,
        "comparison_rows": diagnostics["comparison_rows"],
        "historical_calibration_certified": False,
        "limitations": [
            "No independent EIA-923 source, BA plant crosswalk or net/gross convention validation",
            "Calendar-complete and label-matched does not prove modeled fleet completeness",
            "Transmission ratings, outages and holdout validation not certified"
        ]
    }
    (out / "calibration_pipeline_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    return manifest

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hourly", required=True)
    p.add_argument("--observed", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--allow-partial-fleet", action="store_true")
    a = p.parse_args()
    print(json.dumps(run(a.hourly, a.observed, a.output, allow_partial_fleet=a.allow_partial_fleet), indent=2))

if __name__ == "__main__":
    main()
