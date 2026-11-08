"""Paper C: conservative BA x technology EIA-930A reporting-population nameplate screen.

EIA-860M denominators: monthly 2025 preliminary Operating inventory, using
monthly plant-assigned BA. Numerators: unique, source-verified EIA-930A Schedule
2 matched same BA/plant/generator identities, with finite monthly nameplate.
This is roster representation, NOT July 2023/2024 generation availability.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .paperc_eia860m_vintage_identity import inventory

BAS=("AZPS","BPAT","CISO","SRP")
CLASSES=("natural_gas","wind","solar","hydro_nonpumped","pumped_hydro",
         "nuclear","coal","battery_storage","other_storage","petroleum",
         "geothermal","other","unknown")
GOOD="matched_identity_same_plant_ba"
KEY=["plant_id","generator_id"]


def technology(tech, fuel):
    t=str(tech or "").strip().lower()
    f=str(fuel or "").strip().upper()
    if any(z in t for z in ("pumped storage","pumped hydro")):return "pumped_hydro"
    if any(z in t for z in ("battery","electrochemical storage")) or f=="MWH":return "battery_storage"
    if any(z in t for z in ("other storage","compressed air","flywheel")):return "other_storage"
    if "natural gas" in t or f=="NG":return "natural_gas"
    if "wind" in t or f=="WND":return "wind"
    if "solar" in t or f=="SUN":return "solar"
    if "hydroelectric" in t or f=="WAT":return "hydro_nonpumped"
    if "nuclear" in t or f=="NUC":return "nuclear"
    if "coal" in t or f in {"BIT","SUB","LIG","WC","RC","ANT"}:return "coal"
    if "geothermal" in t or f=="GEO":return "geothermal"
    if "petroleum" in t or "diesel" in t or f in {"DFO","RFO","JF","KER","PC"}:return "petroleum"
    if t or f:return "other"
    return "unknown"


def summarize(monthly, joined, year, month):
    if year not in (2023,2024) or month not in ("february","august"):
        raise ValueError("Cited EIA-930A month and year required")
    if set(joined.ba)!=set(BAS) or set(joined.year)!={year}:
        raise ValueError("EIA-930A four BA reporting cohort absent")
    needed={"ba","plant_id","generator_id","monthly_860m_match_class",
            "monthly_860m_nameplate_mw","eia860_technology",
            "eia860_energy_source_1","eia930a_row"}
    if not needed.issubset(joined):raise ValueError("Original generator identity audit columns missing")
    if joined.duplicated(["ba","eia930a_row"]).any():
        raise ValueError("Duplicated source record key")
    if monthly.duplicated(KEY).any():
        raise ValueError("Monthly operating inventory has duplicate plant+generator")
    m=monthly.copy()
    m["ba"]=m.eia860_plant_reported_ba.fillna("").astype(str).str.strip()
    m=m.loc[m.ba.isin(BAS)].copy()
    m["technology_class"]=[technology(a,b) for a,b in
                           zip(m.eia860_technology,m.eia860_energy_source_1)]
    m["source_nameplate_mw"]=pd.to_numeric(m.eia860_annual_operable_nameplate_mw,errors="coerce")
    if m.source_nameplate_mw.dropna().lt(0).any():
        raise ValueError("Negative original monthly nameplate")
    good=joined.loc[joined.monthly_860m_match_class.eq(GOOD)].copy()
    if good.duplicated(KEY).any():
        # Multiple EIA-930A rows cannot certify two physical capacities.
        raise ValueError("A purported unique same BA match repeats a plant/generator")
    good["plant_id"]=good.plant_id.astype(str)
    good["generator_id"]=good.generator_id.astype(str)
    reference=m[KEY+["ba","source_nameplate_mw","technology_class"]]
    verify=good.merge(reference,on=KEY,how="left",validate="one_to_one",
                      suffixes=("_joined","_source"),indicator=True)
    if not verify["_merge"].eq("both").all():
        raise ValueError("Claimed source match missing in exact-month EIA860M inventory")
    if not verify.ba_joined.eq(verify.ba_source).all():
        raise ValueError("Claimed same BA mismatch")
    offered=pd.to_numeric(verify.monthly_860m_nameplate_mw,errors="coerce")
    if not np.allclose(offered.fillna(-1),verify.source_nameplate_mw.fillna(-1),
                       atol=1e-5,rtol=0):
        raise ValueError("Unreconciled monthly source nameplate mismatch")
    valid=m.loc[m.source_nameplate_mw.notna()].copy()
    observed=verify.loc[verify.source_nameplate_mw.notna()].copy()
    # Explicit zero/positive annual monthly nameplate ratio only on a
    # documented, same-year-cited EIA860M Operating nameplate denominator.
    rows=[]
    for ba in BAS:
        for tech in CLASSES:
            denom=valid.loc[valid.ba.eq(ba)&valid.technology_class.eq(tech)]
            numerator=observed.loc[observed.ba_source.eq(ba)&
                                  observed.technology_class.eq(tech)]
            source_category=m.loc[m.ba.eq(ba)&m.technology_class.eq(tech)]
            total=float(denom.source_nameplate_mw.sum())
            selected=float(numerator.source_nameplate_mw.sum())
            if selected>total+1e-5:
                raise ValueError("Source-matched subset exceeds monthly BA tech denominator")
            rows.append({"eia930a_data_year":year,"monthly_inventory":month+" 2025",
                "ba":ba,"technology_class":tech,
                "monthly_operating_identity_rows":len(source_category),
                "monthly_operating_nonmissing_nameplate_rows":len(denom),
                "monthly_operating_nameplate_mw":total,
                "matched_930a_unique_same_ba_generator_rows":len(numerator),
                "matched_930a_monthly_nameplate_mw":selected,
                "monthly_roster_nameplate_fraction_matched":
                   selected/total if total>0 else np.nan,
                "fraction_defined_only_for_positive_monthly_denominator":total>0,
                "real_hourly_available_capacity_verified":False,
                "source_scope_monthly_2025_not_historical_2023_2024_peak":True})
    table=pd.DataFrame(rows)
    if not table.loc[table.monthly_roster_nameplate_fraction_matched.notna(),
                 "monthly_roster_nameplate_fraction_matched"].between(0,1.000001).all():
        raise ValueError("Invalid source roster nameplate fraction")
    summary=joined.groupby(["ba","monthly_860m_match_class"]).size().rename("eia930a_original_rows").reset_index()
    summary["eia930a_data_year"]=year
    cross=joined.loc[~joined.monthly_860m_match_class.eq(GOOD)].copy()
    cross["identity_status_only_not_attributable_to_technology_MW"]=True
    manifest={"year":year,"month":month,"annual_reported_930a_source_rows":len(joined),
        "matched_unique_same_ba_930a_rows":len(good),
        "monthly_ba_source_rows":len(m),
        "monthly_total_nameplate_mw":float(valid.source_nameplate_mw.sum()),
        "matched_nameplate_mw":float(observed.source_nameplate_mw.sum()),
        "unmatched_930a_rows_kept_without_MW_inference":len(cross),
        "denominator":"EIA860M February/August 2025 Operating BA+technology nameplate, not 2023/2024 system supply",
        "numerator":"Unique EIA930A Schedule2 exact Plant+Generator ID, same BA, cited EIA860M monthly MW",
        "unknown_technology_class_is_not_assumed_absent":True,
        "hourly_available_mw_calibrated":False,"historical_eens_estimated":False}
    return table,summary,cross,manifest


def main():
    p=argparse.ArgumentParser()
    for y in (2023,2024):
        p.add_argument("--monthly"+str(y),required=True)
        p.add_argument("--identity"+str(y),required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    manifests=[]
    for year,month in ((2023,"february"),(2024,"august")):
        source=inventory(getattr(a,"monthly"+str(year)),month)
        cohort=pd.read_csv(getattr(a,"identity"+str(year)),
                           dtype={"plant_id":str,"generator_id":str})
        tbl,counts,unmatched,meta=summarize(source,cohort,year,month)
        for label,df in (("ba_technology_nameplate",tbl),
                          ("identity_categories",counts),("unmatched_source_rows",unmatched)):
            df.to_csv(out/f"paperc_{year}_{label}.csv",index=False)
        manifests.append(meta)
        print("NAMEPLATE SCOPE",json.dumps(meta))
        print("TECHNOLOGY TOTAL BY BA:",tbl.groupby(["ba","technology_class"])[[
              "monthly_operating_nameplate_mw","matched_930a_monthly_nameplate_mw"]].sum().to_string())
    (out/"paperc_year_specific_monthly_nameplate_scope.json").write_text(
        json.dumps(manifests,indent=2)+"\n")

if __name__=="__main__":main()
