"""Signed Page 1 vs Page 4 shared-plant reporting differences, not calibration."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd


def differences(page1, page4, *, ba="SRP", period="2024-01"):
    required1={"plant_id","reported_ba","period","prime_mover","reported_fuel","net_generation_mwh"}
    required4={"plant_id","generator_id","reported_ba","period","generation_mwh"}
    if not required1.issubset(page1.columns) or not required4.issubset(page4.columns):
        raise ValueError("Missing source columns")
    frames=[]
    for raw, energy in ((page1,"net_generation_mwh"),(page4,"generation_mwh")):
        x=raw.copy()
        for key in ("plant_id","reported_ba","period"):
            x[key]=x[key].astype("string").str.strip()
            if x[key].isna().any() or x[key].eq("").any():
                raise ValueError("Missing plant or reporting identity")
        x["plant_id"]=x.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
        x[energy]=pd.to_numeric(x[energy],errors="coerce")
        if not np.isfinite(x[energy].to_numpy(dtype=float)).all():
            raise ValueError("Missing or nonfinite reported MWh")
        x=x.loc[x.reported_ba.eq(ba)&x.period.eq(period)].copy()
        if x.empty:raise ValueError("No matching reporting records")
        frames.append(x)
    a,b=frames
    if b.duplicated(["plant_id","generator_id","reported_ba","period"]).any():
        raise ValueError("Duplicate Page 4 generator-month records")
    # Page 1 coarse keys can legitimately repeat, e.g. nuclear units.
    s1=a.groupby("plant_id",as_index=False).agg(
        page1_mwh=("net_generation_mwh","sum"),
        page1_rows=("plant_id","size"))
    s4=b.groupby("plant_id",as_index=False).agg(
        page4_mwh=("generation_mwh","sum"),
        page4_rows=("plant_id","size"))
    joined=s1.merge(s4,on="plant_id",how="outer",validate="one_to_one",indicator=True)
    joined["source_scope"]=joined["_merge"].astype("string").map({
        "both":"shared_plant","left_only":"page1_only","right_only":"page4_only"})
    joined=joined.drop(columns=["_merge"])
    both=joined.source_scope.eq("shared_plant")
    joined["page1_minus_page4_mwh"]=np.nan
    joined.loc[both,"page1_minus_page4_mwh"]=(
        joined.loc[both,"page1_mwh"]-joined.loc[both,"page4_mwh"])
    joined=joined.sort_values("plant_id").reset_index(drop=True)
    shared=joined.loc[both].copy()
    summary={
        "ba":ba,"period":period,
        "shared_plant_count":len(shared),
        "page1_only_plant_count":int(joined.source_scope.eq("page1_only").sum()),
        "page4_only_plant_count":int(joined.source_scope.eq("page4_only").sum()),
        "shared_net_difference_mwh":float(shared.page1_minus_page4_mwh.sum()),
        "shared_absolute_difference_mwh":float(shared.page1_minus_page4_mwh.abs().sum()),
        "shared_plant_page1_mwh":float(shared.page1_mwh.sum()),
        "shared_plant_page4_mwh":float(shared.page4_mwh.sum()),
        "page1_total_mwh":float(a.net_generation_mwh.sum()),
        "page4_total_mwh":float(b.generation_mwh.sum()),
        "add_source_totals_permitted":False,
        "historical_calibration_certified":False,
        "caution":"Plant differences mix reporting grains, fuel/prime mover scope and precision. No physical interchange or outage inference."
    }
    # Expose original Page 1 fuel/mover rows for the shared plants, without allocating Page 4 to fuels.
    fuel=a.loc[a.plant_id.isin(set(shared.plant_id))].copy()
    return joined,fuel,summary


def main():
    p=argparse.ArgumentParser()
    for key in ("page1","page4","output"):p.add_argument("--"+key,required=True)
    p.add_argument("--ba",default="SRP")
    p.add_argument("--period",default="2024-01")
    args=p.parse_args()
    a=pd.read_csv(args.page1,dtype={"plant_id":"string"})
    b=pd.read_csv(args.page4,dtype={"plant_id":"string","generator_id":"string"})
    rows,fuel,manifest=differences(a,b,ba=args.ba,period=args.period)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    rows.to_csv(out/"page1_page4_plant_differences.csv",index=False)
    fuel.to_csv(out/"page1_shared_plant_fuel_evidence.csv",index=False)
    (out/"shared_plant_difference_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
