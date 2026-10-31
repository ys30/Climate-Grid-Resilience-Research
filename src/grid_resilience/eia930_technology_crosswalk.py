"""Conservative EIA-930 fuel-to-PyPSA technology crosswalk.

Only exact source categories with a sufficiently clear modeled technology
are admitted. Hydro+pumped storage cannot be treated as hydro generation,
and Other/Unknown cannot be assigned to arbitrary generator technologies.
"""
import argparse,csv,json
from pathlib import Path

DIRECT={
 "Coal":"coal",
 "Natural Gas":"gas",
 "Nuclear":"nuclear",
 "All Petroleum Products":"oil",
 "Solar":"solar",
 "Wind":"wind",
}
REVIEW={
 "Hydropower and Pumped Storage":"mixed_hydro_and_pumped_storage",
 "Other Fuel Sources":"mixed_other_fuels",
 "Unknown Fuel Sources":"unclassified_fuel",
}
def map_candidates(eligible_csv,output):
    rows=list(csv.DictReader(open(eligible_csv,newline="",encoding="utf-8")))
    if not rows:raise ValueError("Empty eligible groups")
    seen=set();accepted=[];held=[]
    for row in rows:
        key=(row["ba"],row["fuel"])
        if key in seen:raise ValueError("Duplicate BA-fuel")
        seen.add(key)
        if row["status"]!="complete_observed_hours" or int(row["reported_hours"])!=696:
            raise ValueError("Candidate coverage not complete")
        if row["fuel"] in DIRECT:
            accepted.append({"ba":row["ba"],"eia930_fuel":row["fuel"],
                             "pypsa_technology":DIRECT[row["fuel"]],
                             "mapping_status":"direct_category_candidate"})
        elif row["fuel"] in REVIEW:
            held.append({"ba":row["ba"],"eia930_fuel":row["fuel"],
                         "reason":REVIEW[row["fuel"]]})
        else:raise ValueError("Unexpected EIA-930 fuel classification")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    with (out/"direct_technology_candidates.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["ba","eia930_fuel","pypsa_technology","mapping_status"]);w.writeheader();w.writerows(accepted)
    with (out/"held_technology_candidates.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["ba","eia930_fuel","reason"]);w.writeheader();w.writerows(held)
    m={"direct_candidates":len(accepted),"held_for_review":len(held),
       "technology_coverage_certified":False,"capacity_basis_certified":False,
       "historical_calibration_certified":False,
       "warning":"Direct category candidate does not certify same generators, net/gross capacity basis, or complete BA fleet."}
    (out/"technology_crosswalk_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    return m
def main():
    p=argparse.ArgumentParser();p.add_argument("--eligible",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(map_candidates(a.eligible,a.output),indent=2))
if __name__=="__main__":main()
