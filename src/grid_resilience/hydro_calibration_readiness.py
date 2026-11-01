"""Fail-closed eligibility gate for reporting historical HY/PS model-fit metrics.

The gate is independent of the numerical comparison itself. Synthetic or
unverified model outputs may be tested, but not presented as historical fit.
"""
import argparse
import json
from pathlib import Path

REQUIRED_OBS=("historical_ba_crosswalk_verified","hydro_fleet_coverage_verified",
              "ps_reporting_basis_reconciled")
REQUIRED_MODEL=("full_month_utc_coverage","historical_inputs_verified",
                "modeled_generation_is_net_mwh","capacity_and_dispatch_basis_verified")

def assess(observation_provenance, model_provenance, output):
    obs=json.loads(Path(observation_provenance).read_text())
    model=json.loads(Path(model_provenance).read_text())
    missing_observation=[name for name in REQUIRED_OBS if obs.get(name) is not True]
    missing_model=[name for name in REQUIRED_MODEL if model.get(name) is not True]
    eligible=not missing_observation and not missing_model
    report={"historical_generation_comparison_eligible":eligible,
            "missing_observation_checks":missing_observation,
            "missing_model_checks":missing_model,
            "historical_adequacy_validation_certified":False,
            "note":"Even passing generation-fit eligibility does not certify topology, intertie capacity, weather-to-availability mapping or reliability outcomes."}
    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--observation-provenance",required=True)
    p.add_argument("--model-provenance",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(assess(a.observation_provenance,a.model_provenance,a.output),indent=2))
if __name__=="__main__":main()
