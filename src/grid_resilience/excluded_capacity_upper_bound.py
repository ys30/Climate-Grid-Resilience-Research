"""Upper-bound test for screened-out EIA-860 capacity; NOT historical dispatch."""
import argparse,json,calendar
from pathlib import Path
import pandas as pd

def bound(review,modeled_unserved_mwh,year=2024,month=1):
    required={"plant_id","generator_id","nameplate_capacity_mw","screening_candidate"}
    if not required.issubset(review):raise ValueError("Missing inventory columns")
    d=review.copy()
    for k in ("plant_id","generator_id"):
        d[k]=d[k].astype("string").str.strip()
        if d[k].isna().any() or d[k].eq("").any():raise ValueError("Missing identity")
    if d.duplicated(["plant_id","generator_id"]).any():raise ValueError("Duplicate identity")
    flags=d.screening_candidate.astype(str).str.lower().map({"true":True,"false":False})
    if flags.isna().any():raise ValueError("Invalid eligibility flag")
    d["nameplate_capacity_mw"]=pd.to_numeric(d.nameplate_capacity_mw,errors="raise")
    if d.nameplate_capacity_mw.isna().any() or (d.nameplate_capacity_mw<0).any():raise ValueError("Invalid capacity")
    shortage=float(modeled_unserved_mwh)
    if not 0<=shortage<float("inf"):raise ValueError("Invalid shortage")
    hours=calendar.monthrange(year,month)[1]*24
    excluded=d.loc[~flags]
    excluded_mw=float(excluded.nameplate_capacity_mw.sum())
    maximum_extra_mwh=excluded_mw*hours
    return {"year":year,"month":month,"hours":hours,
      "excluded_generator_count":len(excluded),"excluded_nameplate_mw":excluded_mw,
      "physical_nameplate_full_output_upper_bound_mwh":maximum_extra_mwh,
      "baseline_counterfactual_unserved_mwh":shortage,
      "remaining_gap_lower_bound_mwh_given_only_these_additions":max(0.0,shortage-maximum_extra_mwh),
      "upper_bound_assumes":"Every excluded unit can contribute its entire nameplate capacity for every month hour; ignores fuel, forced outages, commitment, and transmission.",
      "not_a_validated_energy_yield":True,"historical_calibration_certified":False}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--review",required=True);a.add_argument("--baseline-manifest",required=True)
    a.add_argument("--year",type=int,default=2024);a.add_argument("--month",type=int,default=1)
    a.add_argument("--output",required=True)
    x=a.parse_args()
    baseline=json.loads(Path(x.baseline_manifest).read_text())
    result=bound(pd.read_csv(x.review),baseline["modeled_unserved_mwh"],x.year,x.month)
    out=Path(x.output);out.mkdir(parents=True,exist_ok=True)
    (out/"excluded_capacity_maximum_contribution.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
