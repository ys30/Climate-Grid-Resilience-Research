"""Paper C E1 final bounded 2024 EIA-860 Operable generator-key census.

Exclusion precedence is deterministic, disjoint and consistent with annual
candidate admission (valid MW, single fuel, nonstorage, supported fuel).
This inventory does NOT establish physical hourly BA deliverability.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .paperc_year_specific_eia860_inventory import _worksheet, BAS
from .eia860_generator_extract import HEADERS
from .eia860_generator_join import FUEL_TO_TECH

REASONS=("admitted_single_fuel_nonstorage_candidate",
         "invalid_or_missing_nameplate",
         "multifuel_or_secondary_fuel",
         "storage_excluded",
         "unmapped_primary_fuel")

def census(archive):
    gh, rows=_worksheet(archive,"3_1_Generator","Operable")
    ph, plants=_worksheet(archive,"2___Plant","Plant")
    if any(gh.count(col)!=1 for col in HEADERS):
        raise ValueError("Original EIA-860 Operable column contract invalid")
    if any(ph.count(col)!=1 for col in ("Plant Code","Balancing Authority Code")):
        raise ValueError("Original EIA-860 Plant-BA column contract invalid")
    gi={dest:gh.index(src) for src,dest in HEADERS.items()}
    pi=ph.index("Plant Code");bi=ph.index("Balancing Authority Code")
    p=pd.DataFrame([
       {"plant_id":str(r[pi]).strip(),
        "ba":str(r[bi]).strip() if r[bi] is not None else ""}
       for r in plants if r[pi] is not None
    ])
    if p.plant_id.duplicated().any():
        raise ValueError("Repeated official plant identity")
    data=[]
    for r in rows:
        if r[gi["plant_id"]] is None:
            continue
        data.append({key: str(r[index]).strip() if r[index] is not None else ""
                     for key,index in gi.items()})
    g=pd.DataFrame(data)
    if g.empty or g.duplicated(["plant_id","generator_id"]).any():
        raise ValueError("Official generator-key uniqueness failed")
    x=g.merge(p,on="plant_id",how="left",validate="many_to_one",indicator=True)
    x=x.loc[x.ba.isin(BAS)].copy()
    if len(x)!=3268 or set(x.ba)!=BAS:
        raise ValueError(f"Original official four BA denominator changed: {len(x)}")
    for field in ("energy_source_1","energy_source_2","multiple_fuels","prime_mover","reported_technology","status"):
        x[field]=x[field].fillna("").astype(str).str.strip()
    fuel=x.energy_source_1.str.upper()
    second=x.energy_source_2.str.upper()
    multi=x.multiple_fuels.str.upper().isin(("Y","YES","1","TRUE"))|second.ne("")
    storage=x.reported_technology.str.contains("Storage|Battery|Pumped",case=False,regex=True)
    power=pd.to_numeric(x.nameplate_capacity_mw,errors="coerce")
    valid=power.notna() & power.gt(0)
    supported=fuel.isin(FUEL_TO_TECH)
    admitted=valid & ~multi & ~storage & supported
    x["audit_technology"]=fuel.map(FUEL_TO_TECH)
    x["nameplate_mw_numeric"]=power
    x["admitted"]=admitted
    x["classification_reason"]=np.select(
        [~valid,multi,storage,~supported],
        list(REASONS)[1:],
        default=REASONS[0])
    if x.admitted.sum()!=2625 or (~x.admitted).sum()!=643:
        raise ValueError("2024 2625 admitted/643 excluded annual archived population changed")
    if x.duplicated(["plant_id","generator_id"]).any() or x.classification_reason.isna().any():
        raise ValueError("Duplicate/missing classification")
    if (x.admitted!=(x.classification_reason==REASONS[0])).any():
        raise ValueError("Nonexclusive original annual-source admission")
    retained=["plant_id","generator_id","ba","status","energy_source_1","energy_source_2",
              "multiple_fuels","prime_mover","reported_technology",
              "nameplate_capacity_mw","summer_capacity_mw","winter_capacity_mw",
              "nameplate_mw_numeric","audit_technology","admitted","classification_reason"]
    x=x[retained].sort_values(["ba","plant_id","generator_id"]).reset_index(drop=True)
    group=x.groupby(["ba","classification_reason"],as_index=False).agg(
        generator_rows=("generator_id","size"),
        positive_reported_nameplate_mw=("nameplate_mw_numeric",lambda v:float(v[v.gt(0)].sum())),
        missing_or_invalid_nameplate_rows=("nameplate_mw_numeric",lambda v:int((~(v.gt(0)&v.notna())).sum())))
    if len(x)!=int(group.generator_rows.sum()) or int(group.loc[group.classification_reason!=REASONS[0],"generator_rows"].sum())!=643:
        raise ValueError("Four-BA exclusion-coverage reconciliation failed")
    tech=x.loc[x.admitted].groupby(["ba","audit_technology"],as_index=False).agg(
        generator_rows=("generator_id","size"),nameplate_capacity_mw=("nameplate_mw_numeric","sum"))
    if int(tech.generator_rows.sum())!=2625:
        raise ValueError("Technology subset missing rows")
    manifest={
        "official_source_year":2024,"source_archive_sha256":hashlib.sha256(Path(archive).read_bytes()).hexdigest(),
        "four_ba_operable_generator_rows":3268,
        "admitted_single_fuel_nonstorage_candidate_rows":2625,
        "excluded_rows":643,
        "audit_reasons_are_disjoint":True,
        "generator_key_is_plant_id_plus_generator_id":True,
        "plant_ba_mapping_is_annual_reported_not_grid_topology":True,
        "annual_nameplate_is_hourly_firm_available_capacity":False,
        "all_operable_rows_assumed_usable_in_july":False,
        "unresolved_original_eia930a_generator_identifiers_fabricated":False,
        "physical_grid_calibration_completed":False,
        "ready_for_physical_capacity_replacement":False,
        "no_new_pypsa_solves_performed":True}
    return x,group,tech,manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    x,group,tech,m=census(args.archive)
    root=Path(args.output);root.mkdir(parents=True,exist_ok=True)
    x.to_csv(root/"e1_eia860_2024_fourba_3268_generator_keyed_classification.csv",index=False)
    group.to_csv(root/"e1_eia860_2024_excluded_643_by_ba_reason.csv",index=False)
    tech.to_csv(root/"e1_eia860_2024_2625_admitted_by_ba_technology.csv",index=False)
    (root/"e1_eia860_2024_generator_keyed_census_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print(group.to_string(index=False))
    print(json.dumps(m,indent=2))

if __name__=="__main__":
    main()
