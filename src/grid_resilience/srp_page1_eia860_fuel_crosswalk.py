"""Plant-level EIA-923 Page 1 to EIA-860 generator fuel-code candidate audit.

An exact plant/prime-mover/fuel-code match is only candidate evidence:
Page 1 records are not generator IDs, may repeat coarse keys, and generator
BA attribution does not prove dispatch entitlement or hourly availability.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def audit(page1, roster, *, ba="SRP", period="2024-01"):
    p_required={"plant_id","reported_ba","period","prime_mover","reported_fuel","net_generation_mwh"}
    g_required={"plant_id","generator_id","prime_mover","energy_source_1",
                "energy_source_2","plant_reported_ba","nameplate_capacity_mw"}
    if not p_required.issubset(page1):
        raise ValueError("Missing Page1 source fields")
    if not g_required.issubset(roster):
        raise ValueError("Missing EIA860 roster fields")
    p=page1.copy().reset_index(drop=True)
    g=roster.copy()
    for frame,keys in ((p,("plant_id","reported_ba","period","prime_mover","reported_fuel")),
                       (g,("plant_id","generator_id","prime_mover","plant_reported_ba"))):
        for k in keys:
            frame[k]=frame[k].astype("string").str.strip()
            if frame[k].isna().any() or frame[k].eq("").any():
                raise ValueError("Missing source ID or classification")
        frame["plant_id"]=frame.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
    p=p.loc[p.reported_ba.eq(ba)&p.period.eq(period)].copy()
    g=g.loc[g.plant_reported_ba.eq(ba)].copy()
    if p.empty or g.empty:
        raise ValueError("Empty BA/month source or BA roster")
    if g.duplicated(["plant_id","generator_id"]).any():
        raise ValueError("Duplicate EIA860 generator identities")
    p["net_generation_mwh"]=pd.to_numeric(p.net_generation_mwh,errors="coerce")
    if not np.isfinite(p.net_generation_mwh.to_numpy(dtype=float)).all():
        raise ValueError("Missing or nonfinite Page1 generation")
    g["nameplate_capacity_mw"]=pd.to_numeric(g.nameplate_capacity_mw,errors="coerce")
    if not np.isfinite(g.nameplate_capacity_mw.to_numpy(dtype=float)).all() or (g.nameplate_capacity_mw<0).any():
        raise ValueError("Invalid EIA860 generator capacity")
    for k in ("energy_source_1","energy_source_2"):
        g[k]=g[k].astype("string").fillna("").str.strip()
    rows=[]
    # Preserve original repeated Page1 rows and their signed net MWh.
    for _,r in p.iterrows():
        plant=g.loc[g.plant_id.eq(r.plant_id)]
        mover=plant.loc[plant.prime_mover.eq(r.prime_mover)]
        same=mover.loc[mover.energy_source_1.eq(r.reported_fuel)|
                       mover.energy_source_2.eq(r.reported_fuel)]
        if not len(plant):
            label="plant_absent_in_annual_roster"
        elif not len(mover):
            label="plant_present_prime_mover_unmatched"
        elif not len(same):
            label="plant_mover_present_fuel_code_unmatched"
        else:
            label="plant_mover_fuel_candidate"
        rows.append({
            "plant_id":str(r.plant_id),"period":str(r.period),
            "prime_mover":str(r.prime_mover),"reported_fuel":str(r.reported_fuel),
            "page1_signed_net_mwh":float(r.net_generation_mwh),
            "candidate_status":label,"plant_roster_units":len(plant),
            "prime_mover_candidate_units":len(mover),
            "fuel_candidate_units":len(same),
            "fuel_candidate_generator_ids":";".join(sorted(same.generator_id.astype(str))),
        })
    out=pd.DataFrame(rows)
    classes=out.groupby("candidate_status",dropna=False).agg(
        source_rows=("plant_id","size"),
        signed_page1_mwh=("page1_signed_net_mwh","sum"),
        abs_page1_mwh=("page1_signed_net_mwh",lambda s:float(s.abs().sum()))
    ).reset_index()
    manifest={
        "ba":ba,"period":period,"page1_source_rows":int(len(out)),
        "page1_distinct_plants":int(out.plant_id.nunique()),
        "eia860_plant_ba_generator_count":int(len(g)),
        "plant_absent_source_rows":int(out.candidate_status.eq("plant_absent_in_annual_roster").sum()),
        "plant_mover_fuel_candidate_rows":int(out.candidate_status.eq("plant_mover_fuel_candidate").sum()),
        "fuel_code_unmatched_rows":int(out.candidate_status.eq("plant_mover_present_fuel_code_unmatched").sum()),
        "source_total_signed_net_mwh":float(out.page1_signed_net_mwh.sum()),
        "unique_generator_assignment_certified":False,
        "physical_ba_entitlement_certified":False,
        "historical_calibration_certified":False,
        "warning":"A source fuel-code candidate is not a generator-level generation allocation. "
                  "A zero monthly net MWh value does not establish availability."
    }
    return out,classes,manifest


def main():
    p=argparse.ArgumentParser()
    for k in ("page1","roster","output"):p.add_argument("--"+k,required=True)
    p.add_argument("--ba",default="SRP");p.add_argument("--period",default="2024-01")
    args=p.parse_args()
    a=pd.read_csv(args.page1,dtype={"plant_id":"string"},keep_default_na=False)
    b=pd.read_csv(args.roster,dtype={"plant_id":"string","generator_id":"string"},keep_default_na=False)
    rows,summary,manifest=audit(a,b,ba=args.ba,period=args.period)
    target=Path(args.output);target.mkdir(parents=True,exist_ok=True)
    rows.to_csv(target/"page1_eia860_fuel_candidate_rows.csv",index=False)
    summary.to_csv(target/"page1_eia860_fuel_candidate_classes.csv",index=False)
    (target/"page1_eia860_fuel_candidate_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
