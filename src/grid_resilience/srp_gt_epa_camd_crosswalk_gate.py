"""Audit EPA CAMD-to-EIA unit crosswalk for SRP 2024 EIA860 GT candidates.

Crosswalk may predate 2024, contain fuzzy/manual matches and one-to-many
combustion-unit to electricity-generator relationships. A matching CAMD UNIT
does NOT certify 2024 hourly net electrical generation, dispatch or derating.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

TARGETS=("141","55129","147")
REQUIRED_CROSSWALK={"CAMD_PLANT_ID","CAMD_UNIT_ID","CAMD_GENERATOR_ID",
                    "EIA_PLANT_ID","EIA_GENERATOR_ID","MATCH_TYPE_GEN",
                    "MATCH_TYPE_BOILER","EIA_UNIT_TYPE"}


def normalize_ids(series):
    return (series.astype("string").str.strip()
            .str.replace(r"^0+(?=[0-9])","",regex=True))


def analyze(inventory,crosswalk):
    req={"plant_id","generator_id","prime_mover","energy_source_1","nameplate_capacity_mw"}
    if not req.issubset(inventory) or not REQUIRED_CROSSWALK.issubset(crosswalk):
        raise ValueError("Missing EPA-EIA crosswalk or EIA860 source identity fields")
    inv=inventory.copy()
    cw=crosswalk.copy()
    for x,plant,generator in ((inv,"plant_id","generator_id"),
                               (cw,"EIA_PLANT_ID","EIA_GENERATOR_ID")):
        x[plant]=normalize_ids(x[plant])
        x[generator]=x[generator].astype("string").str.strip()
    inv=inv.loc[inv.plant_id.isin(TARGETS)&
                inv.prime_mover.astype("string").str.strip().eq("GT")].copy()
    if inv.empty or set(inv.plant_id)!=set(TARGETS):
        raise ValueError("Missing targeted annual 2024 GT inventory")
    if inv.duplicated(["plant_id","generator_id"]).any():
        raise ValueError("Duplicate annual GT generator identities")
    inv["nameplate_capacity_mw"]=pd.to_numeric(inv.nameplate_capacity_mw,errors="coerce")
    if inv.nameplate_capacity_mw.isna().any() or (inv.nameplate_capacity_mw<=0).any():
        raise ValueError("Invalid annual GT candidate capacity")
    cw=cw.loc[cw.EIA_PLANT_ID.isin(TARGETS)].copy()
    cw["CAMD_PLANT_ID"]=normalize_ids(cw.CAMD_PLANT_ID)
    for key in ("CAMD_UNIT_ID","CAMD_GENERATOR_ID","MATCH_TYPE_GEN",
                "MATCH_TYPE_BOILER","EIA_UNIT_TYPE"):
        cw[key]=cw[key].astype("string").str.strip()
    # A crosswalk may contain multiple EPA units and duplicate generator IDs.
    # Keep relationship multiplicity instead of selecting an arbitrary row.
    matching=cw.merge(inv[["plant_id","generator_id","prime_mover"]],
        left_on=["EIA_PLANT_ID","EIA_GENERATOR_ID"],
        right_on=["plant_id","generator_id"],how="inner",validate="many_to_one")
    all_eia=inv.merge(matching[["plant_id","generator_id",
                                "CAMD_PLANT_ID","CAMD_UNIT_ID",
                                "CAMD_GENERATOR_ID","MATCH_TYPE_GEN",
                                "MATCH_TYPE_BOILER"]],on=["plant_id","generator_id"],
                      how="left",validate="one_to_many")
    rows=[]
    for (plant,gen),group in all_eia.groupby(["plant_id","generator_id"]):
        mapped=group.loc[group.CAMD_UNIT_ID.notna() &
                         group.CAMD_UNIT_ID.ne("")]
        unique_units=sorted(set(zip(mapped.CAMD_PLANT_ID.astype(str),
                                    mapped.CAMD_UNIT_ID.astype(str))))
        rows.append({
            "plant_id":str(plant),"eia_generator_id":str(gen),
            "annual_prime_mover":"GT",
            "epa_camd_unit_relationship_count":len(unique_units),
            "epa_camd_unit_ids":";".join(f"{p}/{u}" for p,u in unique_units),
            "epa_camd_generator_ids":";".join(sorted(
                set(mapped.CAMD_GENERATOR_ID.dropna().astype(str)))),
            "match_types_gen":";".join(sorted(
                set(mapped.MATCH_TYPE_GEN.dropna().astype(str)))),
            "match_types_boiler":";".join(sorted(
                set(mapped.MATCH_TYPE_BOILER.dropna().astype(str)))),
            "epa_mapping_exists":bool(unique_units),
            "epa_mapping_one_to_one_proven":False,
            "epa_hourly_electrical_net_mw_validated":False})
    table=pd.DataFrame(rows).sort_values(["plant_id","eia_generator_id"])
    counts=table.groupby("plant_id",as_index=False).agg(
        annual_gt_generator_count=("eia_generator_id","size"),
        candidates_with_epa_unit_relationship=("epa_mapping_exists","sum"),
        annual_gt_ids_with_multiple_camd_units=("epa_camd_unit_relationship_count",
                                                 lambda x:int((x>1).sum())))
    # Distinguish crosswalk missingness from actual absence of emissions reports.
    manifest={
        "reference":"USEPA/camd-eia-crosswalk epa_eia_crosswalk.csv",
        "reference_csv_is_2024_specific_operational_monitoring":False,
        "matched_by":["EIA_PLANT_ID","EIA_GENERATOR_ID"],
        "manual_and_fuzzy_crosswalk_relationships_need_review":True,
        "many_to_many_emissions_and_electricity_units_possible":True,
        "unmapped_eia_gt_generator_is_not_outage_or_nonreporting_evidence":True,
        "epa_gross_load_if_reported_is_not_net_generator_mw":True,
        "epa_emissions_or_heat_input_is_not_electrical_net_generation":True,
        "hourly_operational_data_downloaded":False,
        "temperature_derating_calibrated":False,
        "observed_generator_outage_or_eens":False
    }
    return table,counts,all_eia,manifest


def main():
    p=argparse.ArgumentParser()
    for key in ("inventory","crosswalk","output"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    root=Path(a.output);root.mkdir(parents=True,exist_ok=True)
    table,counts,relationships,manifest=analyze(
        pd.read_csv(a.inventory,dtype={"plant_id":"string","generator_id":"string"}),
        pd.read_csv(a.crosswalk,dtype="string",low_memory=False))
    table.to_csv(root/"gt_candidate_epa_unit_relationships.csv",index=False)
    counts.to_csv(root/"gt_candidate_epa_coverage_summary.csv",index=False)
    relationships.to_csv(root/"gt_candidate_epa_raw_relationship_rows.csv",index=False)
    (root/"epa_crosswalk_data_admission_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print(counts.to_string(index=False))
    print(table.to_string(index=False))


if __name__=="__main__":
    main()
