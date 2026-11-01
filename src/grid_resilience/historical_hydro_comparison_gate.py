"""Run HY/PS historical comparison only when independently audited gates pass.

This is a strict orchestration layer. It does not itself certify the provenance
flags: their source and independent review must be recorded upstream.
"""
import argparse
import json
from pathlib import Path
from .hydro_calibration_readiness import assess
from .hydro_model_month_adapter import adapt
from .hydro_monthly_model_comparison import compare

def run(observed, modeled_monthly, observation_provenance, model_provenance, output):
    out=Path(output)
    out.mkdir(parents=True,exist_ok=True)
    readiness=assess(observation_provenance,model_provenance,out/"calibration_readiness.json")
    if not readiness["historical_generation_comparison_eligible"]:
        result={"status":"blocked_unverified_historical_inputs",
                "historical_generation_comparison_eligible":False,
                "missing_observation_checks":readiness["missing_observation_checks"],
                "missing_model_checks":readiness["missing_model_checks"],
                "comparison_performed":False,
                "historical_adequacy_validation_certified":False}
        (out/"historical_comparison_gate.json").write_text(json.dumps(result,indent=2)+"\n")
        return result
    converted=adapt(modeled_monthly,model_provenance,out/"adapted_model")
    if not converted["comparison_eligible"]:
        raise ValueError("Model adapter rejected historical comparability")
    comparison=compare(observed,out/"adapted_model"/"modeled_hy_ps_monthly_for_comparison.csv",
                       out/"comparison")
    result={"status":"generation_fit_diagnostic_computed",
            "historical_generation_comparison_eligible":True,
            "comparison_performed":True,
            "matched_observed_cells":comparison["matched_observed_cells"],
            "historical_adequacy_validation_certified":False,
            "warning":"These are generation-fit diagnostics, NOT independently validated weather-driven adequacy, flow ratings, or historical outage estimates."}
    (out/"historical_comparison_gate.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--observed",required=True)
    p.add_argument("--modeled-monthly",required=True)
    p.add_argument("--observation-provenance",required=True)
    p.add_argument("--model-provenance",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    print(json.dumps(run(args.observed,args.modeled_monthly,args.observation_provenance,
                         args.model_provenance,args.output),indent=2))
if __name__=="__main__":main()
