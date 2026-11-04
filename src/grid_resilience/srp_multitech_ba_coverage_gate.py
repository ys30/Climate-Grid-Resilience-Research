"""Source-grain BA coverage gate for synthetic SRP multi-tech capacity.

Annual EIA-860 Plant BA is not dispatch ownership. EIA-923 Page4 reported BA
and generator-month MWh are a distinct population; absence of a generator
in Page4 cannot be interpreted as an outage or zero production.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from .srp_assumed_multitech_factorial import PRIMARY_FUEL

MOVERS={"gas":{"GT","CT","CA","CS","ST"},"coal":{"ST"},
        "nuclear":{"ST"},"hydro":{"HY"},"solar":{"PV"},"wind":{"WT"}}


def normalize_identity(df, columns):
    result=df.copy()
    for k in columns:
        if k not in result:raise ValueError("Missing field: "+k)
        result[k]=result[k].astype("string").str.strip()
        if result[k].isna().any() or result[k].eq("").any():
            raise ValueError("Empty official identity: "+k)
    result["plant_id"]=result.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
    return result


def audit(annual, page4, *, ba="SRP", period="2024-01"):
    r=normalize_identity(annual,["plant_id","generator_id","plant_reported_ba",
                                 "prime_mover","energy_source_1"])
    r=r.loc[r.plant_reported_ba.eq(ba)].copy()
    p=normalize_identity(page4,["plant_id","generator_id","reported_ba","period"])
    p=p.loc[p.reported_ba.eq(ba)&p.period.eq(period)].copy()
    for data,label in ((r,"annual Plant BA"),(p,"Page4 BA/month")):
        if data.duplicated(["plant_id","generator_id"]).any():
            raise ValueError("Duplicate "+label+" generator identity")
    if r.empty or p.empty:raise ValueError("Missing target BA population")
    r["nameplate_capacity_mw"]=pd.to_numeric(r.nameplate_capacity_mw,errors="coerce")
    p["generation_mwh"]=pd.to_numeric(p.generation_mwh,errors="coerce")
    if not np.isfinite(r.nameplate_capacity_mw.to_numpy(float)).all() or (
        r.nameplate_capacity_mw<0).any():
        raise ValueError("Invalid annual nameplate")
    if not np.isfinite(p.generation_mwh.to_numpy(float)).all():
        raise ValueError("Invalid Page4 signed generation")
    r["technology"]=r.energy_source_1.map(PRIMARY_FUEL)
    valid=r.apply(lambda x: x.technology in MOVERS and x.prime_mover in MOVERS[x.technology],axis=1)
    r.loc[~valid,"technology"]="excluded_unmodeled"
    merged=r.merge(p[["plant_id","generator_id","generation_mwh"]],
                   on=["plant_id","generator_id"],how="left",
                   indicator=True,validate="one_to_one")
    merged["in_page4_reported_ba_month"]=merged["_merge"].eq("both")
    summary=merged.groupby("technology",dropna=False).agg(
        eia860_generator_count=("generator_id","size"),
        annual_nameplate_mw=("nameplate_capacity_mw","sum"),
        page4_matched_generator_count=("in_page4_reported_ba_month","sum"),
        page4_matched_nameplate_mw=("nameplate_capacity_mw",
            lambda s:float(s[merged.loc[s.index,"in_page4_reported_ba_month"]].sum())),
        page4_matching_signed_mwh=("generation_mwh","sum")
    ).reset_index()
    summary["not_in_page4_generator_count"]=(
        summary.eia860_generator_count-summary.page4_matched_generator_count)
    summary["not_in_page4_nameplate_mw"]=(
        summary.annual_nameplate_mw-summary.page4_matched_nameplate_mw)
    reversed_scope=p.merge(r[["plant_id","generator_id"]],
                           on=["plant_id","generator_id"],how="left",
                           indicator=True,validate="one_to_one")
    outside=reversed_scope.loc[reversed_scope["_merge"].eq("left_only"),
                               ["plant_id","generator_id","generation_mwh"]].copy()
    manifest={
        "plant_ba":ba,"month":period,
        "annual_plant_ba_operable_generator_count":int(len(r)),
        "annual_plant_ba_nameplate_mw":float(r.nameplate_capacity_mw.sum()),
        "page4_reported_ba_generators":int(len(p)),
        "annual_and_page4_matched_generators":int(merged.in_page4_reported_ba_month.sum()),
        "annual_not_in_page4_generators":int((~merged.in_page4_reported_ba_month).sum()),
        "page4_outside_annual_plant_ba_generator_count":int(len(outside)),
        "page4_outside_annual_plant_ba_signed_mwh":float(outside.generation_mwh.sum()),
        "page4_total_reported_ba_signed_mwh":float(p.generation_mwh.sum()),
        "page4_matched_annual_signed_mwh":float(
            merged.loc[merged.in_page4_reported_ba_month,"generation_mwh"].sum()),
        "model_supply_technology_assigned_mw":float(
            merged.loc[merged.technology.ne("excluded_unmodeled"),"nameplate_capacity_mw"].sum()),
        "generation_month_missing_must_not_be_imputed_zero":True,
        "annual_plant_ba_is_dispatch_right_certification":False,
        "page4_absence_is_evidence_of_shutdown":False,
        "ba_ownership_calibrated":False,
        "historical_reliability_calibrated":False,
        "warning":"EIA860 Plant BA, EIA923 Page4 reported BA, and real dispatch rights are different scopes. Page4 monthly records do not certify hourly generator availability."
    }
    if abs(manifest["page4_total_reported_ba_signed_mwh"]-(
        manifest["page4_matched_annual_signed_mwh"]+
        manifest["page4_outside_annual_plant_ba_signed_mwh"]))>1e-5:
        raise AssertionError("Page4 signed source conservation")
    return merged.drop(columns="_merge"),summary,outside,manifest


def main():
    parser=argparse.ArgumentParser()
    for key in ("annual","page4","output"):parser.add_argument("--"+key,required=True)
    a=parser.parse_args()
    dtype={"plant_id":"string","generator_id":"string"}
    rows,summary,outside,manifest=audit(
        pd.read_csv(a.annual,dtype=dtype),pd.read_csv(a.page4,dtype=dtype))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    rows.to_csv(out/"plant_ba_generator_coverage_rows.csv",index=False)
    summary.to_csv(out/"plant_ba_technology_coverage.csv",index=False)
    outside.to_csv(out/"page4_outside_annual_plant_ba.csv",index=False)
    (out/"plant_ba_coverage_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(summary.to_string(index=False))
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
