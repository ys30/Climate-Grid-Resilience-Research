"""Exact identity-level audit: annual EIA-930A Schedule 2 versus EIA-860 Operable.

Compare plant code + generator ID, preserving BA attribution conflicts and
original source-vintage differences. Never assert annual roster implies hourly
dispatch, online availability, or physical system adequacy.
"""
import argparse
import io
import json
import zipfile
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from .eia860_generator_extract import HEADERS
from .paperc_year_specific_eia860_inventory import _worksheet
from .paperc_eia930a_declared_relationships import get_year

BAS={"AZPS","BPAT","CISO","SRP"}
KEYS=["plant_id","generator_id"]


def _identity(v, is_plant=False):
    if v is None or pd.isna(v):
        return ""
    s=str(v).strip()
    if is_plant and s.endswith(".0") and s[:-2].isdigit():
        s=s[:-2]
    return s


def eia860_operable(archive):
    h,rr=_worksheet(archive,"3_1_Generator","Operable")
    hp,plants=_worksheet(archive,"2___Plant","Plant")
    if any(h.count(col)!=1 for col in HEADERS):
        raise ValueError("Official annual EIA860 Operable generator schema incomplete")
    if any(hp.count(c)!=1 for c in ("Plant Code","Balancing Authority Code")):
        raise ValueError("Official EIA860 Plant BA schema incomplete")
    rows=[dict(zip(h,r)) for r in rr if r and r[h.index("Plant Code")] is not None]
    entries=[]
    for raw in rows:
        plant=_identity(raw.get("Plant Code"),True)
        generator=_identity(raw.get("Generator ID"))
        if not plant or not generator:raise ValueError("EIA860 missing join key")
        entries.append({"plant_id":plant,"generator_id":generator,
                        "eia860_technology":str(raw.get("Technology") or "").strip(),
                        "eia860_energy_source_1":str(raw.get("Energy Source 1") or "").strip(),
                        "eia860_prime_mover":str(raw.get("Prime Mover") or "").strip(),
                        "eia860_annual_operable_nameplate_mw":
                            pd.to_numeric(raw.get("Nameplate Capacity (MW)"),errors="coerce")})
    fleet=pd.DataFrame(entries)
    if fleet.duplicated(KEYS).any():raise ValueError("Duplicate exact EIA860 Operable identity")
    p=[{"plant_id":_identity(r[hp.index("Plant Code")],True),
        "eia860_plant_reported_ba":str(r[hp.index("Balancing Authority Code")] or "").strip()}
       for r in plants if r and r[hp.index("Plant Code")] is not None]
    plant=pd.DataFrame(p)
    if plant.duplicated("plant_id").any():raise ValueError("Duplicate official EIA860 plant")
    return fleet.merge(plant,on="plant_id",how="left",validate="many_to_one")


def compare(annual_roster,operable,year):
    if year not in (2023,2024):raise ValueError("Source-year identity audit only 2023/2024")
    a=annual_roster.copy()
    needed={"year","ba","plant_id_source","generator_id_source","technology",
            "reported_nameplate_mw","eia860_generator_id_recognized"}
    if not needed.issubset(a):raise ValueError("EIA930A source fields incomplete")
    if set(a.year)!={year} or set(a.ba)!=BAS:
        raise ValueError("Wrong annual EIA930A four-BA cohort")
    a["plant_id"]=a.plant_id_source.map(lambda v:_identity(v,True))
    a["generator_id"]=a.generator_id_source.map(_identity)
    a["has_source_identity"]=a.plant_id.ne("")&a.generator_id.ne("")&a.eia860_generator_id_recognized.eq(True)
    a["eia930a_row"]=range(len(a))
    source_keys=a.loc[a.has_source_identity]
    # Keep duplicate raw source rows; never treat them as independently identified generators.
    duplicate_keys=source_keys.loc[source_keys.duplicated(["ba"]+KEYS,keep=False),["ba"]+KEYS]
    duplicate_key_set=set(duplicate_keys.itertuples(index=False,name=None))
    a["duplicate_same_ba_source_identity"]=a[["ba"]+KEYS].apply(
        lambda row:tuple(row) in duplicate_key_set,axis=1)
    b=operable.copy()
    if not set(KEYS).issubset(b) or b.duplicated(KEYS).any():
        raise ValueError("Ambiguous official EIA860 reference roster")
    match=a.merge(b,on=KEYS,how="left",validate="many_to_one",indicator=True)
    match["match_class"]="unmatched_in_sameyear_eia860_operable"
    match.loc[~match.has_source_identity,"match_class"]="no_eia930a_source_identity"
    exact=match.has_source_identity&match["_merge"].eq("both")
    match.loc[exact,"match_class"]="matched_identity_ba_conflict"
    match.loc[exact & match.ba.eq(match.eia860_plant_reported_ba),
              "match_class"]="matched_identity_same_plant_ba"
    match.loc[match.duplicate_same_ba_source_identity,
              "match_class"]="duplicate_same_ba_source_identity"
    match["eia930a_annual_nameplate_mw"]=pd.to_numeric(
        match.reported_nameplate_mw,errors="coerce")
    both=(match.eia930a_annual_nameplate_mw.notna()&
          match.eia860_annual_operable_nameplate_mw.notna()&exact&
          ~match.duplicate_same_ba_source_identity)
    match["annual_nameplate_delta_930a_minus_860_mw"]=(
        match.eia930a_annual_nameplate_mw-match.eia860_annual_operable_nameplate_mw
    ).where(both)
    match["annual_nameplate_comparison_available"]=both
    match["generator_online_hourly_or_available_mw_inferred"]=False
    match["ba_membership_physical_connectivity_verified"]=False
    match["eia930a_schedule2_source_vintage_matches_eia860_annual_vintage_certified"]=False
    columns=["year","ba","eia930a_row","plant_id","generator_id","has_source_identity",
             "eia860_generator_id_recognized","match_class","duplicate_same_ba_source_identity","eia860_plant_reported_ba",
             "technology","eia860_technology","eia860_energy_source_1","eia860_prime_mover",
             "eia930a_annual_nameplate_mw","eia860_annual_operable_nameplate_mw",
             "annual_nameplate_delta_930a_minus_860_mw",
             "annual_nameplate_comparison_available",
             "generator_online_hourly_or_available_mw_inferred",
             "ba_membership_physical_connectivity_verified",
             "eia930a_schedule2_source_vintage_matches_eia860_annual_vintage_certified"]
    match=match[columns]
    reports=[]
    for ba,g in match.groupby("ba",sort=True):
        reports.append({"year":year,"ba":ba,"eia930a_schedule2_rows":len(g),
            "exact_identity_and_same_ba_rows":int(g.match_class.eq("matched_identity_same_plant_ba").sum()),
            "exact_identity_ba_conflict_rows":int(g.match_class.eq("matched_identity_ba_conflict").sum()),
            "sameyear_operable_unmatched_rows":int(g.match_class.eq("unmatched_in_sameyear_eia860_operable").sum()),
            "source_identity_missing_rows":int(g.match_class.eq("no_eia930a_source_identity").sum()),
            "duplicate_same_ba_source_identity_rows":int(g.match_class.eq("duplicate_same_ba_source_identity").sum()),
            "cross_ba_duplicate_plant_generator_keys":int(g.loc[g.has_source_identity,
                ["plant_id","generator_id"]].apply(tuple,axis=1).isin(
                match.loc[match.ba.ne(ba)&match.has_source_identity,
                          ["plant_id","generator_id"]].apply(tuple,axis=1)).sum()),
            "annual_capacity_both_sources_rows":int(g.annual_nameplate_comparison_available.sum()),
            "sum_absolute_annual_nameplate_difference_mw":
                float(g.annual_nameplate_delta_930a_minus_860_mw.abs().sum()),
            "complete_generator_coverage_certified":False,
            "hourly_firm_capacity_or_EENS_calibrated":False})
    summary=pd.DataFrame(reports)
    if not (summary[["exact_identity_and_same_ba_rows","exact_identity_ba_conflict_rows",
                       "sameyear_operable_unmatched_rows","source_identity_missing_rows",
                       "duplicate_same_ba_source_identity_rows"]]
            .sum(axis=1).eq(summary.eia930a_schedule2_rows).all()):
        raise ValueError("Identity accounting does not reconcile")
    cross=match.loc[match.has_source_identity].groupby(KEYS).ba.nunique()
    manifest={"year":year,"eia930a_rows":len(match),"matched_identity_rows":int(exact.sum()),
              "cross_ba_duplicate_generator_identity_keys":int(cross.gt(1).sum()),
              "same_ba_ambiguous_identity_source_rows":int(a.duplicate_same_ba_source_identity.sum()),
              "identity_join_key":"exact plant_id + generator_id, no name/fuel guessing",
              "source_year_860_operable_not_same_as_eia930a_underlying_workbook_860_vintage":True,
              "annual_nameplate_not_hourly_available_power":True,
              "historical_shortage_calibrated":False}
    return match,summary,manifest


def main():
    p=argparse.ArgumentParser()
    for k in ("archive2023","archive2024","roster2023","roster2024","output"):
        p.add_argument("--"+k,required=True)
    a=p.parse_args()
    dest=Path(a.output);dest.mkdir(parents=True,exist_ok=True)
    metadata=[]
    for year in (2023,2024):
        roster,_,_,_=get_year(getattr(a,f"roster{year}"),year)
        gen=eia860_operable(getattr(a,f"archive{year}"))
        full,summary,manifest=compare(roster,gen,year)
        full.to_csv(dest/f"eia930a_eia860_exact_generator_join_{year}.csv",index=False)
        summary.to_csv(dest/f"eia930a_eia860_fourba_match_summary_{year}.csv",index=False)
        metadata.append(manifest)
        print("YEAR",year,json.dumps(manifest))
        print(summary.to_string(index=False))
    (dest/"eia930a_860_generator_identity_scope.json").write_text(json.dumps(metadata,indent=2)+"\n")


if __name__=="__main__":main()
