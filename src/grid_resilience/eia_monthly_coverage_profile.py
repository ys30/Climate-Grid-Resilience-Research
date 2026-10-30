"""Profile monthly observed candidate coverage without filling absent groups.

Absence of a BA/technology/month group is a data gap, not zero MWh.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def profile(source, output, year=2024):
    df=pd.read_csv(source,dtype={"ba":str,"technology":str,"period":str})
    required={"ba","technology","period","generation_mwh"}
    if df.empty or not required.issubset(df) or df[list(required)].isna().any().any():
        raise ValueError("Invalid candidate aggregation")
    if df.duplicated(["ba","technology","period"]).any():
        raise ValueError("Duplicate BA/technology/month totals")
    df["generation_mwh"]=pd.to_numeric(df.generation_mwh,errors="raise")
    if not df.generation_mwh.map(lambda x:-float("inf")<float(x)<float("inf")).all():
        raise ValueError("Nonfinite monthly generation")
    months=[f"{year}-{m:02d}" for m in range(1,13)]
    if not df.period.isin(months).all():
        raise ValueError("Candidate periods outside requested calendar year")
    grid=pd.MultiIndex.from_product([sorted(df.ba.unique()),sorted(df.technology.unique()),months],
                                     names=["ba","technology","period"]).to_frame(index=False)
    result=grid.merge(df,on=["ba","technology","period"],how="left",validate="one_to_one",indicator=True)
    result["record_present"]=result["_merge"].eq("both")
    result.drop(columns=["_merge"],inplace=True)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/"candidate_monthly_coverage_matrix.csv",index=False)
    coverage=(result.groupby(["ba","technology"],as_index=False)
              .record_present.agg(months_present="sum",months_expected="size"))
    coverage["complete_12_months"]=coverage.months_present.eq(12)
    coverage.to_csv(out/"candidate_monthly_coverage_by_technology.csv",index=False)
    manifest={"year":year,"observed_rows":len(df),"expected_ba_technology_month_cells":len(grid),
              "missing_cells":int((~result.record_present).sum()),
              "complete_ba_technology_groups":int(coverage.complete_12_months.sum()),
              "total_ba_technology_groups":len(coverage),
              "historical_calibration_certified":False,
              "warning":"No-record group is unknown, not zero; presence of records does not establish complete generator fleet coverage."}
    (out/"candidate_monthly_coverage_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    p.add_argument("--year",type=int,default=2024)
    a=p.parse_args()
    print(json.dumps(profile(a.input,a.output,a.year),indent=2))
if __name__=="__main__":main()
