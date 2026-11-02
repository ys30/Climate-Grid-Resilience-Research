"""Crosswalk SRP Page1 HY/PS plant identities to EIA-860 Operable generators.

A plant-level match cannot prove generator-level attribution or BA membership.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def build(page1,operable,ba="SRP",month="2024-01"):
    required={"plant_id","ba","prime_mover","period","net_generation_mwh"}
    if not required.issubset(page1):raise ValueError("Page1 columns missing")
    required860={"plant_id","generator_id","prime_mover","energy_source_1","nameplate_capacity_mw"}
    if not required860.issubset(operable):raise ValueError("EIA860 columns missing")
    p=page1.loc[page1.ba.eq(ba)&page1.period.eq(month)&page1.prime_mover.isin(["HY","PS"])].copy()
    e=operable.copy()
    for d in (p,e):
        d["plant_id"]=d.plant_id.astype("string").str.strip().str.replace(r"^0+(?=[0-9])","",regex=True)
    if p.empty or p.plant_id.isna().any():raise ValueError("Missing Page1 hydro/PS plant keys")
    if e.duplicated(["plant_id","generator_id"]).any():raise ValueError("Duplicate EIA860 generator identity")
    e["nameplate_capacity_mw"]=pd.to_numeric(e.nameplate_capacity_mw,errors="coerce")
    if e.nameplate_capacity_mw.isna().any() or (e.nameplate_capacity_mw<0).any():raise ValueError("Bad EIA860 nameplate capacity")
    e["prime_mover"]=e.prime_mover.astype("string").str.upper().str.strip()
    plants=p[["plant_id","prime_mover"]].drop_duplicates()
    joined=plants.merge(e,on="plant_id",how="left",suffixes=("_page1","_eia860"),indicator=True)
    joined["matching_prime_mover"]=joined.prime_mover_page1.eq(joined.prime_mover_eia860).fillna(False)
    joined["identity_class"]="no_eia860_operable_at_plant"
    joined.loc[joined["_merge"].eq("both"),"identity_class"]="same_plant_different_or_unverified_mover"
    joined.loc[joined.matching_prime_mover,"identity_class"]="plant_and_prime_mover_match_generator_unverified"
    result=joined.drop(columns=["_merge"])
    counts=result.groupby(["plant_id","prime_mover_page1","identity_class"],dropna=False).agg(
        eia860_generator_rows=("generator_id","count"),nameplate_mw=("nameplate_capacity_mw","sum")).reset_index()
    manifest={"ba":ba,"month":month,"source_page1_plant_count":int(p.plant_id.nunique()),
      "candidate_generator_rows_with_matching_plant_and_prime_mover":int(result.matching_prime_mover.sum()),
      "all_page1_plants_with_any_matching_generator":bool(result.groupby("plant_id").matching_prime_mover.any().all()),
      "generator_attribution_certified":False,"ba_fleet_completeness_certified":False,
      "notes":"Page1 plant/mover source matched to 2024 EIA860 operable identities; no direct Page1-to-generator attribution; storage must not be modeled as ordinary generator."}
    return result,counts,manifest

def main():
    a=argparse.ArgumentParser()
    for x in ("page1","operable","output"):a.add_argument("--"+x,required=True)
    z=a.parse_args()
    joined,summary,meta=build(pd.read_csv(z.page1,dtype={"plant_id":"string"}),
      pd.read_csv(z.operable,dtype={"plant_id":"string","generator_id":"string"}))
    out=Path(z.output);out.mkdir(parents=True,exist_ok=True)
    joined.to_csv(out/"page1_hy_ps_eia860_generator_candidates.csv",index=False)
    summary.to_csv(out/"page1_hy_ps_eia860_plant_summary.csv",index=False)
    (out/"page1_hy_ps_eia860_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(summary.to_string(index=False));print(json.dumps(meta,indent=2))
if __name__=="__main__":main()
