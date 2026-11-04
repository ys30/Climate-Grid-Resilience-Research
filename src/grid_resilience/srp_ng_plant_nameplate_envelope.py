"""Necessary monthly nameplate-energy ceiling for SRP Page1 NG plants.

Candidate generator union is counted once per plant (no MWh allocation).
Annual EIA-860 nameplate is not verified January availability or BA deliverability.
"""
import argparse
import calendar
import json
from pathlib import Path

import numpy as np
import pandas as pd


def audit(candidates, roster, *, year=2024, month=1, fuel="NG"):
    if not 1 <= month <= 12:
        raise ValueError("Invalid month")
    hours=24*calendar.monthrange(year,month)[1]
    p_required={"plant_id","period","reported_fuel","page1_signed_net_mwh",
                "fuel_candidate_units","fuel_candidate_generator_ids"}
    g_required={"plant_id","generator_id","nameplate_capacity_mw","plant_reported_ba"}
    if not p_required.issubset(candidates) or not g_required.issubset(roster):
        raise ValueError("Missing required identity, source generation or capacity")
    p=candidates.copy()
    g=roster.copy()
    for frame,cols in ((p,("plant_id","period","reported_fuel")),
                       (g,("plant_id","generator_id","plant_reported_ba"))):
        for key in cols:
            frame[key]=frame[key].astype("string").str.strip()
            if frame[key].isna().any() or frame[key].eq("").any():
                raise ValueError("Invalid source identity")
        frame["plant_id"]=frame.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
    p=p.loc[p.period.eq(f"{year}-{month:02d}") & p.reported_fuel.eq(fuel)].copy()
    g=g.loc[g.plant_reported_ba.eq("SRP")].copy()
    if p.empty or g.empty:
        raise ValueError("Empty source scope")
    if g.duplicated(["plant_id","generator_id"]).any():
        raise ValueError("Duplicate EIA860 generator identity")
    p["page1_signed_net_mwh"]=pd.to_numeric(p.page1_signed_net_mwh,errors="coerce")
    g["nameplate_capacity_mw"]=pd.to_numeric(g.nameplate_capacity_mw,errors="coerce")
    p["fuel_candidate_units"]=pd.to_numeric(p.fuel_candidate_units,errors="coerce")
    if not np.isfinite(p.page1_signed_net_mwh.to_numpy(float)).all():
        raise ValueError("Invalid Page1 MWh")
    if not np.isfinite(g.nameplate_capacity_mw.to_numpy(float)).all() or g.nameplate_capacity_mw.lt(0).any():
        raise ValueError("Invalid EIA860 capacity")
    if not np.isfinite(p.fuel_candidate_units.to_numpy(float)).all() or (
        p.fuel_candidate_units<0).any() or (
        p.fuel_candidate_units%1!=0).any():
        raise ValueError("Invalid candidate counts")
    rows=[]
    for plant,frame in p.groupby("plant_id",sort=True):
        ids=set()
        for _,r in frame.iterrows():
            current={x.strip() for x in str(r.fuel_candidate_generator_ids or "").split(";")
                     if x.strip() and x.strip().lower()!="nan"}
            if len(current)!=int(r.fuel_candidate_units):
                raise ValueError("Candidate IDs/count discrepancy")
            ids.update(current)
        subset=g.loc[g.plant_id.eq(plant) & g.generator_id.isin(ids)]
        if len(subset)!=len(ids):
            raise ValueError("Candidate identity absent from selected BA roster")
        capacity=float(subset.nameplate_capacity_mw.sum())
        mwh=float(frame.page1_signed_net_mwh.sum())
        maximum=capacity*hours
        rows.append({
            "plant_id":plant,"page1_ng_rows":int(len(frame)),
            "distinct_candidate_generators":int(len(ids)),
            "candidate_nameplate_mw":capacity,"month_hours":hours,
            "page1_signed_ng_mwh":mwh,
            "nameplate_24h_ceiling_mwh":maximum,
            "observed_to_nameplate_ceiling_fraction":mwh/maximum if maximum>0 else None,
            "exceeds_theoretical_nameplate_ceiling":bool(mwh>maximum+1e-6),
            "negative_source_net_mwh":bool(mwh<0),
            "hourly_dispatch_certified":False
        })
    result=pd.DataFrame(rows)
    summary={"source":"EIA923 Page1 signed NG net monthly and EIA860 annual Plant BA operable nameplate",
             "period":f"{year}-{month:02d}","hours":hours,
             "plants":len(result),"page1_ng_rows":len(p),
             "total_signed_ng_mwh":float(p.page1_signed_net_mwh.sum()),
             "plant_aggregate_signed_ng_mwh":float(result.page1_signed_ng_mwh.sum()),
             "plants_exceeding_theoretical_ceiling":int(result.exceeds_theoretical_nameplate_ceiling.sum()),
             "plants_with_no_candidate_capacity":int(result.candidate_nameplate_mw.eq(0).sum()),
             "capacity_deduplicated_by_generator_id":True,
             "historical_availability_calibrated":False,
             "historical_calibration_certified":False,
             "caution":"A nameplate upper bound is necessary, not sufficient: no hourly/seasonal availability, ownership, losses or dispatch rights are established."}
    if not np.isclose(summary["total_signed_ng_mwh"],summary["plant_aggregate_signed_ng_mwh"],atol=1e-6):
        raise AssertionError("Source generation not conserved")
    return result,summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidates",required=True)
    p.add_argument("--roster",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--month",type=int,default=1)
    args=p.parse_args()
    candidate=pd.read_csv(args.candidates,dtype={"plant_id":"string"},keep_default_na=False)
    roster=pd.read_csv(args.roster,dtype={"plant_id":"string","generator_id":"string"},keep_default_na=False)
    result,manifest=audit(candidate,roster,year=args.year,month=args.month)
    root=Path(args.output);root.mkdir(parents=True,exist_ok=True)
    result.to_csv(root/"ng_plant_nameplate_energy_envelope.csv",index=False)
    (root/"ng_plant_nameplate_energy_envelope_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
