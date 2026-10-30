"""Audit-gated plant-to-BA crosswalk aggregation for prepared EIA-923 rows.

Requires upstream plant ID, calendar period, technology and generation MWh.
Crosswalk source references are mandatory; does not verify agencies or download EIA.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def aggregate(generation_csv, crosswalk_csv, output_dir):
    g = pd.read_csv(generation_csv, dtype={"plant_id":str,"period":str,"technology":str})
    x = pd.read_csv(crosswalk_csv, dtype={"plant_id":str,"ba":str,"technology":str,"mapping_source":str})
    need_g = {"plant_id","period","technology","generation_mwh"}
    need_x = {"plant_id","ba","technology","mapping_source"}
    if not need_g.issubset(g) or not need_x.issubset(x):
        raise ValueError("Missing plant-generation or crosswalk fields")
    if g.empty or x.empty or g[list(need_g)].isna().any().any() or x[list(need_x)].isna().any().any():
        raise ValueError("Empty or null source data")
    for frame, cols in ((g,("plant_id","period","technology")),
                        (x,("plant_id","ba","technology","mapping_source"))):
        for col in cols:
            frame[col] = frame[col].str.strip()
            if frame[col].eq("").any():
                raise ValueError(f"Blank {col}")
    if g.duplicated(["plant_id","period","technology"]).any():
        raise ValueError("Duplicate plant/period/technology; aggregate generators upstream explicitly")
    if x.duplicated(["plant_id","technology"]).any():
        raise ValueError("Ambiguous duplicate plant/technology BA crosswalk")
    if not g.period.str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])").all():
        raise ValueError("Period must be YYYY-MM")
    g["generation_mwh"] = pd.to_numeric(g.generation_mwh, errors="raise")
    if not g.generation_mwh.map(lambda v: -float("inf") < float(v) < float("inf")).all():
        raise ValueError("Nonfinite observed generation")
    joined = g.merge(x, on=["plant_id","technology"], how="left", validate="many_to_one",
                     indicator=True)
    if not joined._merge.eq("both").all():
        raise ValueError("Missing plant/technology BA crosswalk; refusing partial aggregation")
    # No assertion that source references are independently authenticated.
    totals = joined.groupby(["ba","technology","period"],as_index=False).generation_mwh.sum()
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    totals.to_csv(out/"observed_ba_technology_month.csv",index=False)
    manifest={"status":"crosswalk_labeled_not_independently_audited",
              "plant_technology_rows":len(g),"mapped_plant_technology_rows":len(joined),
              "bas":sorted(totals.ba.unique().tolist()),
              "mapping_sources":sorted(x.mapping_source.unique().tolist()),
              "source_validation_certified":False,
              "warning":"Plant-to-BA crosswalk, ownership/year changes, gross/net and units require independent source audit. No observed EIA-923 values are provided."}
    (out/"plant_ba_mapping_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--generation",required=True)
    p.add_argument("--crosswalk",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(aggregate(a.generation,a.crosswalk,a.output),indent=2))
if __name__=="__main__":
    main()
