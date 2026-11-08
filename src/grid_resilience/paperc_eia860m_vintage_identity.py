"""Audit monthly EIA-860M inventory vintages against original EIA-930A.

The EIA-930A workbook cites February 2025 monthly preliminary generators
for 2023 and August 2025 for 2024. Matching IDs across these sources
does not imply online units in July, real available MW, or dispatch validation.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from .paperc_eia930a_declared_relationships import get_year
from .paperc_eia930a_eia860_generator_match import compare

BAS={"AZPS","BPAT","CISO","SRP"}
FIELDS={"Plant ID":"plant_id","Generator ID":"generator_id",
        "Balancing Authority Code":"eia860_plant_reported_ba",
        "Nameplate Capacity (MW)":"eia860_annual_operable_nameplate_mw",
        "Technology":"eia860_technology",
        "Energy Source Code":"eia860_energy_source_1",
        "Prime Mover Code":"eia860_prime_mover",
        "Status":"monthly_status"}


def inventory(path,month):
    if month not in ("february","august"):
        raise ValueError("Exact reviewed EIA860M February/August vintage required")
    w=load_workbook(path,read_only=True,data_only=True)
    try:
        ws=w["Operating"]
        iterator=ws.iter_rows(values_only=True)
        title=next(iterator)
        if month.capitalize()+" 2025" not in str(title[0]):
            raise ValueError("Monthly EIA860M title does not match required vintage")
        next(iterator)
        heads=[str(z).strip() if z is not None else "" for z in next(iterator)]
        if any(heads.count(name)!=1 for name in FIELDS):
            raise ValueError("Official EIA860M schema mismatch")
        keys={name:heads.index(name) for name in FIELDS}
        out=[]
        for r in iterator:
            if r[keys["Plant ID"]] is None:
                continue
            def label(name):
                v=r[keys[name]]
                return str(v).strip() if v is not None else ""
            plant=label("Plant ID")
            if plant.endswith(".0") and plant[:-2].isdigit():
                plant=plant[:-2]
            ident=label("Generator ID")
            if not plant or not ident:
                raise ValueError("Monthly EIA860M generator identity unavailable")
            row={"plant_id":plant,"generator_id":ident,
                 "eia860_plant_reported_ba":label("Balancing Authority Code"),
                 "eia860_technology":label("Technology"),
                 "eia860_energy_source_1":label("Energy Source Code"),
                 "eia860_prime_mover":label("Prime Mover Code"),
                 "eia860_annual_operable_nameplate_mw":
                      pd.to_numeric(r[keys["Nameplate Capacity (MW)"]],errors="coerce"),
                 "monthly_status":label("Status")}
            out.append(row)
        frame=pd.DataFrame(out)
        if frame.empty or frame.duplicated(["plant_id","generator_id"]).any():
            raise ValueError("Monthly Operating source repeated/empty generator keys")
        return frame
    finally:
        w.close()


def reconcile(roster, monthly, annual, year,month):
    # Reuse same conservative identity-and-BA comparison for identical source rows.
    raw_month,monthly_summary,monthly_scope=compare(roster,monthly,year)
    needed={"year","ba","eia930a_row","match_class"}
    if not needed.issubset(annual):
        raise ValueError("Annual audited identity record fields unavailable")
    if annual.duplicated(["year","ba","eia930a_row"]).any():
        raise ValueError("Annual audited row identity duplicated")
    # Classification method is the same; source is *different* monthly vs annual vintage.
    diag=raw_month.merge(annual[list(needed)].rename(
        columns={"match_class":"annual_860_operable_match_class"}),
        on=["year","ba","eia930a_row"],how="left",validate="one_to_one")
    if len(diag)!=len(roster) or diag.annual_860_operable_match_class.isna().any():
        raise ValueError("Annual row audit not fully aligned")
    diag=diag.rename(columns={"match_class":"monthly_860m_match_class",
        "eia860_annual_operable_nameplate_mw":"monthly_860m_nameplate_mw",
        "eia860_plant_reported_ba":"monthly_860m_ba_code",
        "annual_nameplate_delta_930a_minus_860_mw":"nameplate_delta_930a_minus_monthly_mw"})
    diag["match_category_changed_between_vintages"]=(
        diag.monthly_860m_match_class.ne(diag.annual_860_operable_match_class))
    diag["monthly_source_month"]=month
    diag["monthly_preliminary_inventory_not_2023_2024_hourly_availability"]=True
    summary=diag.groupby(["year","ba","annual_860_operable_match_class",
                          "monthly_860m_match_class"],as_index=False).size().rename(
        columns={"size":"source_generator_rows"})
    byba=diag.groupby(["year","ba"],as_index=False).agg(
        source_rows=("eia930a_row","size"),
        vintage_match_category_changes=("match_category_changed_between_vintages","sum"),
        monthly_same_ba_matches=("monthly_860m_match_class",
            lambda x:int(x.eq("matched_identity_same_plant_ba").sum())),
        monthly_ba_conflicts=("monthly_860m_match_class",
            lambda x:int(x.eq("matched_identity_ba_conflict").sum())),
        monthly_unmatched=("monthly_860m_match_class",
            lambda x:int(x.eq("unmatched_in_sameyear_eia860_operable").sum())),
        monthly_no_verified_identity=("monthly_860m_match_class",
            lambda x:int(x.eq("no_eia930a_source_identity").sum())),
        monthly_ambiguous=("monthly_860m_match_class",
            lambda x:int(x.eq("duplicate_same_ba_source_identity").sum())))
    if not byba[["monthly_same_ba_matches","monthly_ba_conflicts","monthly_unmatched",
                 "monthly_no_verified_identity","monthly_ambiguous"]].sum(axis=1).eq(byba.source_rows).all():
        raise ValueError("Monthly audit identity category counts incomplete")
    scope={"year":year,"monthly_source":month+" 2025 EIA860M Operating",
           "annual_comparison_source":str(year)+" EIA860 Operable",
           "source_rows":len(diag),
           "changed_identity_classifications":int(diag.match_category_changed_between_vintages.sum()),
           "uncertified_2023_2024_operational_capacity":True,
           "physical_ba_network_membership_verified":False,
           "actual_hourly_dispatch_or_EENS_calibrated":False}
    return diag,summary,byba,scope


def main():
    p=argparse.ArgumentParser()
    for name in ("monthly2023","monthly2024","eia930a2023","eia930a2024",
                 "annualmatch2023","annualmatch2024","output"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    manifests=[]
    for year,month in ((2023,"february"),(2024,"august")):
        roster,_,_,_=get_year(getattr(a,"eia930a"+str(year)),year)
        monthly=inventory(getattr(a,"monthly"+str(year)),month)
        annual=pd.read_csv(getattr(a,"annualmatch"+str(year)),dtype={
            "plant_id":str,"generator_id":str})
        d,t,b,s=reconcile(roster,monthly,annual,year,month)
        for label,frame in (("generator_row_transition",d),
                             ("class_transitions",t),("ba_summary",b)):
            frame.to_csv(out/f"paper_c_eia930a_{year}_annual_vs_{month}2025_{label}.csv",index=False)
        manifests.append(s)
        print("MONTHLY VINTAGE MATCH:",json.dumps(s))
        print(b.to_string(index=False))
    (out/"paper_c_monthly_source_version_scope.json").write_text(
        json.dumps(manifests,indent=2)+"\n")


if __name__=="__main__":
    main()
