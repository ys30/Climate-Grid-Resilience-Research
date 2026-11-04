"""Audit generator identifiability of Page1 natural-gas rows.

Fuel/mover candidate counts are identity evidence, not a certified mapping
from plant/fuel monthly generation to individual EIA-860 generators.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def audit(candidates, *, fuel="NG"):
    need={"plant_id","prime_mover","reported_fuel","page1_signed_net_mwh",
          "fuel_candidate_units","fuel_candidate_generator_ids"}
    if not need.issubset(candidates.columns):
        raise ValueError("Missing candidate evidence fields")
    data=candidates.loc[candidates.reported_fuel.astype("string").str.strip().eq(fuel)].copy()
    if data.empty:raise ValueError("No source rows for target fuel")
    data["page1_signed_net_mwh"]=pd.to_numeric(data.page1_signed_net_mwh,errors="coerce")
    data["fuel_candidate_units"]=pd.to_numeric(data.fuel_candidate_units,errors="coerce")
    if not np.isfinite(data.page1_signed_net_mwh.to_numpy(dtype=float)).all():
        raise ValueError("Missing or nonfinite observed MWh")
    c=data.fuel_candidate_units.to_numpy(dtype=float)
    if not np.isfinite(c).all() or (c<0).any() or (c!=np.floor(c)).any():
        raise ValueError("Invalid generator candidate counts")
    data["identity_bucket"]=np.select(
        [data.fuel_candidate_units.eq(0),data.fuel_candidate_units.eq(1)],
        ["no_candidate","single_candidate"],default="multiple_candidates")
    totals=data.groupby("identity_bucket").agg(
        source_rows=("plant_id","size"),
        source_signed_mwh=("page1_signed_net_mwh","sum"),
        source_absolute_mwh=("page1_signed_net_mwh",lambda s:float(s.abs().sum()))
    ).reset_index()
    plants=data.groupby(["plant_id","identity_bucket"]).agg(
        rows=("plant_id","size"),
        signed_mwh=("page1_signed_net_mwh","sum"),
        candidate_count_max=("fuel_candidate_units","max")
    ).reset_index()
    total=float(data.page1_signed_net_mwh.sum())
    multiple=float(data.loc[data.identity_bucket.eq("multiple_candidates"),
                            "page1_signed_net_mwh"].sum())
    summary={"source_fuel":fuel,"source_rows":int(len(data)),
             "source_plants":int(data.plant_id.nunique()),
             "total_page1_signed_mwh":total,
             "multiple_candidate_rows":int(data.identity_bucket.eq("multiple_candidates").sum()),
             "multiple_candidate_signed_mwh":multiple,
             "multiple_candidate_fraction_of_signed_total":multiple/total if abs(total)>1e-12 else None,
             "single_candidate_rows":int(data.identity_bucket.eq("single_candidate").sum()),
             "no_candidate_rows":int(data.identity_bucket.eq("no_candidate").sum()),
             "candidate_identity_is_generator_dispatch_attribution":False,
             "historical_calibration_certified":False,
             "caution":"Single candidate is not a certified generator allocation; multi-candidate MWh must not be evenly split without supporting data."}
    if int(totals.source_rows.sum())!=len(data):
        raise AssertionError("Source row conservation failed")
    if not np.isclose(totals.source_signed_mwh.sum(),total,atol=1e-6):
        raise AssertionError("Source signed generation conservation failed")
    return data,totals,plants,summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidates",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--fuel",default="NG")
    args=p.parse_args()
    data,buckets,plants,manifest=audit(pd.read_csv(args.candidates),fuel=args.fuel)
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    data.to_csv(output/"ng_identifiability_source_rows.csv",index=False)
    buckets.to_csv(output/"ng_identifiability_buckets.csv",index=False)
    plants.to_csv(output/"ng_identifiability_plant_buckets.csv",index=False)
    (output/"ng_identifiability_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
