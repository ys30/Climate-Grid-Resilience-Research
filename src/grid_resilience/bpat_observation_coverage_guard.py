"""Fail closed on data-quality changes in monthly EIA-930 comparison inputs."""
import argparse,json
from pathlib import Path

def check(coverage_path,observation_manifest_path,output):
    coverage=json.loads(Path(coverage_path).read_text())
    observed=json.loads(Path(observation_manifest_path).read_text())
    expected=int(coverage["expected_weather_hours"])
    actual=int(coverage["matched_observed_hours"])
    if actual!=int(observed["hours"]):raise ValueError("Coverage and observation count disagree")
    if expected-actual!=len(coverage["missing_timestamp_utc"]):
        raise ValueError("Coverage and missing timestamp list disagree")
    if actual/expected<0.95:raise ValueError("Observed coverage below minimum 95%")
    assumed=observed.get("blank_category_hours_assumed_zero",{})
    count=sum(int(v) for v in assumed.values())
    report={"observed_hours":actual,"expected_hours":expected,
            "observed_fraction":actual/expected,
            "missing_hours":expected-actual,
            "blank_split_wind_category_values_assumed_zero":count,
            "blank_category_assumption_present":count>0,
            "comparison_eligible_with_disclosure":True,
            "operational_forecast_accuracy_claim":False,
            "note":"Coverage gate alone does not validate EIA wind-category accounting or prove missingness is random."}
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    (out/"bpat_observation_coverage_guard.json").write_text(json.dumps(report,indent=2)+"\n")
    return report
def main():
    p=argparse.ArgumentParser()
    for k in ("coverage","observation-manifest","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    print(json.dumps(check(a.coverage,a.observation_manifest,a.output),indent=2))
if __name__=="__main__":main()
