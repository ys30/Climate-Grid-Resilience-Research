"""Original EIA-930A schedules 2/4: actual reported generator BA population and
declared pseudo-tie/dynamic BA relationships; NOT hourly meter or line ratings.
"""
import argparse
import json
import re
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook

TARGET={"AZPS","BPAT","CISO","SRP"}
REL_COL="BAs having a Pseudo-Tie or Dynamic Relationship"
MECHANISM_LABELS={"PSEUDO TIE","DYNAMIC IMPORT","DYNAMIC EXPORT","DYNAMIC SCHEDULE"}
GAS_CATEGORIES=("Natural Gas",)
WIND_CATEGORIES=("Wind",)


def records(book, sheet_name):
    w=book[sheet_name]
    iterator=w.iter_rows(values_only=True)
    header=list(next(iterator))
    columns=[str(v).strip() if v is not None else "" for v in header]
    if sheet_name=="SCH 2" and columns[0]=="":
        columns[0]="BA Code"
    if len(columns)!=len(set(columns)):
        raise ValueError("Non-unique official EIA930A column names")
    for raw in iterator:
        if not any(v is not None and str(v).strip() for v in raw):
            continue
        yield dict(zip(columns,raw))


def clean_ba(value):
    return str(value).strip().upper() if value is not None else ""


def get_year(path,year):
    book=load_workbook(path,read_only=True,data_only=True)
    try:
        if not all(x in book.sheetnames for x in ("SCH 2","SCH 4","SUMMARY","Layout Details")):
            raise ValueError("Incomplete original EIA930A schedules")
        layout=book["Layout Details"]
        if str(layout["B2"].value).strip()!=str(year):
            raise ValueError("Workbook does not match source calendar year")
        s2=[]
        for r in records(book,"SCH 2"):
            ba=clean_ba(r["BA Code"])
            if ba not in TARGET:
                continue
            cap=r.get("Nameplate Capacity (MW) (EIA-860)")
            alt=r.get("Nameplate Capacity (MW) (EIA-930A)")
            try:
                mw=float(cap if cap is not None and str(cap).strip() else alt)
            except (ValueError,TypeError):
                mw=float("nan")
            if pd.notna(mw) and mw<0:
                raise ValueError("Negative nameplate in EIA930A")
            tech=str(r.get("Electric Generator Technology") or "").strip()
            plant=str(r.get("EIA Plant ID") or r.get("Plant ID (EIA-930A)") or "").strip()
            gen=str(r.get("EIA Generator ID") or r.get("Generator ID (EIA-930A)") or "").strip()
            s2.append({"year":year,"ba":ba,"eia930a_schedule":2,
                       "plant_id_source":plant,"generator_id_source":gen,
                       "technology":tech,"reported_nameplate_mw":mw,
                       "eia860_generator_id_recognized":bool(r.get("EIA Plant ID") and r.get("EIA Generator ID")),
                       "is_hourly_meter_or_firm_capacity":False})
        sch2=pd.DataFrame(s2)
        if sch2.empty or set(sch2.ba)!=TARGET:
            raise ValueError("Missing expected four BA Schedule 2 sources")
        relations=[]
        for r in records(book,"SCH 4"):
            ba=clean_ba(r["BA Code"])
            partners=sorted(set(x.strip() for x in re.split(r"[,;/]+",clean_ba(r.get(REL_COL))) if x.strip()))
            if not partners:
                continue
            if ba not in TARGET and not TARGET.intersection(partners):
                continue
            plant=str(r.get("EIA Plant ID") or r.get("Plant ID (EIA-930A)") or "").strip()
            gen=str(r.get("EIA Generator ID") or r.get("Generator ID (EIA-930A)") or "").strip()
            mw=r.get("Nameplate Capacity (MW) (EIA-860)")
            if mw is None or str(mw).strip()=="":
                mw=r.get("Nameplate Capacity (MW) (EIA-930A)")
            try:
                mw=float(mw)
            except (ValueError,TypeError):
                mw=float("nan")
            for partner in partners:
                if ba==partner:
                    raise ValueError("Self pseudo-tie / dynamic BA relation")
                relations.append({"year":year,"schedule4_reporting_ba":ba,
                    "relationship_original_label":partner,
                    "relationship_label_kind":"mechanism_category" if partner in MECHANISM_LABELS else "ba_identifier",
                    "declared_partner_ba":None if partner in MECHANISM_LABELS else partner,
                    "source_declares_mechanism_category":partner in MECHANISM_LABELS,
                    "plant_name":str(r.get("Plant Name") or "").strip(),
                    "eia_plant_id_or_fallback":plant,
                    "eia_generator_id_or_fallback":gen,
                    "eia930a_sch2_reported":str(r.get("Generator Reported on EIA-930A Schedule 2?") or "").strip(),
                    "generator_technology":str(r.get("Electric Generator Technology") or "").strip(),
                    "reported_annual_nameplate_mw":mw,
                    "distinguishes_dynamic_schedule_vs_pseudotie":False,
                    "proves_caused_july_pair_reciprocity_discrepancy":False})
        sch4=pd.DataFrame(relations)
        if sch4.empty:
            raise ValueError("No relevant declared Schedule 4 relations")
        group=sch2.groupby(["ba","technology"],as_index=False).agg(
            reported_schedule2_generator_rows=("plant_id_source","size"),
            nonnull_nameplate_mw=("reported_nameplate_mw","sum"),
            recognized_eia860_identity_rows=("eia860_generator_id_recognized","sum"))
        group["year"]=year
        group["nameplate_is_available_generation_mw"]=False
        pair=sch4.groupby(["schedule4_reporting_ba","relationship_original_label","relationship_label_kind"],as_index=False).agg(
            declared_generator_relation_rows=("plant_name","size"),
            nonnull_annual_nameplate_mw=("reported_annual_nameplate_mw","sum"))
        pair["year"]=year
        pair["specific_pair_discrepancy_cause_verified"]=False
        return sch2,sch4,group,pair
    finally:
        book.close()


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source2023",required=True)
    p.add_argument("--source2024",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    reports=[]
    for year in (2023,2024):
        sch2,sch4,group,pairs=get_year(getattr(args,f"source{year}"),year)
        for label,df in (("schedule2_four_ba",sch2),("schedule4_relevant_relationships",sch4),
                         ("schedule2_four_ba_technology_summary",group),
                         ("schedule4_ba_pair_summary",pairs)):
            df.to_csv(out/f"eia930a_{year}_{label}.csv",index=False)
        reports.append({"year":year,"sch2_target_ba_generator_rows":len(sch2),
                       "sch4_relevant_relationship_rows":len(sch4),
                       "sch4_relation_label_groups":len(pairs),
                       "sch4_explicit_mechanism_category_rows":int(sch4.source_declares_mechanism_category.sum()),
                       "sch2_mapped_bas":sorted(sch2.ba.unique().tolist()),
                       "reporter_partner_not_verified_physical_tie":True,
                       "dynamic_vs_pseudotie_mechanism_not_separated":True,
                       "historical_hourly_generator_availability_reconstructed":False,
                       "relationship_is_annual_inventory_not_hourly_2024_july_discrepancy_cause":True})
        print("EIA930A SOURCE YEAR",year,json.dumps(reports[-1]))
        print("RELEVANT RELATIONS",pairs.to_string(index=False))
    (out/"eia930a_source_scope_manifest.json").write_text(json.dumps(reports,indent=2)+"\n")


if __name__=="__main__":main()
