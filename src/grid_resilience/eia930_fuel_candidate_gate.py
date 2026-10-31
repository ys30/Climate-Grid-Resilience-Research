"""Fail-closed EIA-930 observed generation candidate selection from coverage audit."""
import argparse,csv,json
from pathlib import Path

def select(coverage,out,expected_hours=696):
    rows=list(csv.DictReader(open(coverage,newline="",encoding="utf-8")))
    if len(rows)!=36:raise ValueError("Expected exactly 4 BAs x 9 fuel categories")
    seen=set();eligible=[];excluded=[]
    for row in rows:
        key=(row["ba"],row["fuel"])
        if key in seen:raise ValueError("Duplicate BA fuel")
        seen.add(key)
        reported=int(row["reported_hours"]);blank=int(row["blank_hours"])
        if reported+blank!=expected_hours:raise ValueError("Invalid hourly coverage")
        if not 0<=int(row["reported_zero_hours"])<=reported:raise ValueError("Invalid zero count")
        if reported==expected_hours:
            eligible.append({"ba":row["ba"],"fuel":row["fuel"],"status":"complete_observed_hours",
                             "reported_hours":reported})
        else:
            excluded.append({"ba":row["ba"],"fuel":row["fuel"],"status":"incomplete_or_blank",
                             "reported_hours":reported})
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with (out/"eligible_fuel_groups.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["ba","fuel","status","reported_hours"]);w.writeheader();w.writerows(eligible)
    with (out/"excluded_fuel_groups.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["ba","fuel","status","reported_hours"]);w.writeheader();w.writerows(excluded)
    report={"candidate_groups":len(eligible),"excluded_groups":len(excluded),
            "observed_hourly_coverage_only":True,"technology_crosswalk_verified":False,
            "historical_calibration_certified":False,
            "caution":"Complete fuel records are not proof of plant-fleet completeness, category equivalence or historical simulation accuracy."}
    (out/"eligible_fuel_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report
def main():
    p=argparse.ArgumentParser();p.add_argument("--coverage",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(select(a.coverage,a.output),indent=2))
if __name__=="__main__":main()
