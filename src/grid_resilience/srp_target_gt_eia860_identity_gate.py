"""EIA860 Operable generator identities vs EIA923 Page4 rows and Page1 GT fuel rows.

A matching plant and GT prime mover is NOT evidence that Page1 monthly GT
generation belongs to any specific 2024 Operable generator. Generator ID
exactness is evaluated only where both EIA860 and EIA923 Page4 supply IDs.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

TARGETS=("141","55129","147")
PERIODS=("2024-01","2024-07")


def gate(eia860,page1,page4):
    needed={
        "eia860":{"plant_id","generator_id","prime_mover","energy_source_1","nameplate_capacity_mw"},
        "page1":{"plant_id","period","prime_mover","fuel","reported_signed_net_mwh","source_value_reported"},
        "page4":{"plant_id","period","generator_id","prime_mover","reported_signed_net_mwh","source_value_reported"}}
    for name,data in (("eia860",eia860),("page1",page1),("page4",page4)):
        if not needed[name].issubset(data):
            raise ValueError(f"Missing source {name} columns")
    a,b,c=(z.copy() for z in (eia860,page1,page4))
    for z in (a,b,c):
        z["plant_id"]=z.plant_id.astype("string").str.strip().str.replace(
            r"^0+(?=[0-9])","",regex=True)
        if z.plant_id.isna().any() or z.plant_id.eq("").any():
            raise ValueError("Invalid plant ID")
        z["prime_mover"]=z.prime_mover.astype("string").str.strip().str.upper()
    for z in (a,c):
        z["generator_id"]=z.generator_id.astype("string").str.strip()
        if z.generator_id.isna().any() or z.generator_id.eq("").any():
            raise ValueError("Invalid generator ID")
    if a.duplicated(["plant_id","generator_id"]).any():
        raise ValueError("Duplicate EIA860 generator identity")
    if c.duplicated(["plant_id","generator_id","period"]).any():
        raise ValueError("Duplicate EIA923 Page4 generator month")
    a=a.loc[a.plant_id.isin(TARGETS)].copy()
    b=b.loc[b.plant_id.isin(TARGETS)&b.period.isin(PERIODS)].copy()
    c=c.loc[c.plant_id.isin(TARGETS)&c.period.isin(PERIODS)].copy()
    a["nameplate_capacity_mw"]=pd.to_numeric(a.nameplate_capacity_mw,errors="coerce")
    if not np.isfinite(a.nameplate_capacity_mw.to_numpy(float)).all() or a.nameplate_capacity_mw.le(0).any():
        raise ValueError("Invalid EIA860 nameplate")
    if set(a.plant_id)!=set(TARGETS):
        raise ValueError("Missing annual generator inventory for target plants")
    if not (set(b.plant_id)==set(c.plant_id)==set(TARGETS)):
        raise ValueError("Missing target original EIA923 source rows")
    for z in (b,c):
        if z.source_value_reported.isna().any() or not z.source_value_reported.isin([True,False]).all():
            raise ValueError("Bad original reporting indicator")
        z["reported_signed_net_mwh"]=pd.to_numeric(z.reported_signed_net_mwh,errors="coerce")
        if not np.isfinite(z.loc[z.source_value_reported,"reported_signed_net_mwh"].to_numpy(float)).all():
            raise ValueError("Missing reported monthly value")
        if z.loc[~z.source_value_reported,"reported_signed_net_mwh"].notna().any():
            raise ValueError("Unreported generation is not zero")
    c=c.merge(a[["plant_id","generator_id","prime_mover","energy_source_1",
                 "nameplate_capacity_mw"]],
              on=["plant_id","generator_id"],how="left",
              suffixes=("_page4","_eia860"),validate="many_to_one",indicator=True)
    c["exact_annual_generator_id_match"]=c._merge.eq("both")
    c["prime_mover_same_as_annual_inventory"]=(
        c.exact_annual_generator_id_match&
        c.prime_mover_page4.eq(c.prime_mover_eia860))
    rows=[]
    for plant in TARGETS:
        annual=a.loc[a.plant_id.eq(plant)]
        for period in PERIODS:
            one=b.loc[b.plant_id.eq(plant)&b.period.eq(period)]
            four=c.loc[c.plant_id.eq(plant)&c.period.eq(period)]
            if one.empty or four.empty:raise ValueError("Incomplete target month")
            gt=one.loc[one.fuel.astype("string").str.strip().str.upper().eq("NG") &
                       one.prime_mover.eq("GT")&one.source_value_reported]
            non_gt=one.loc[one.fuel.astype("string").str.strip().str.upper().eq("NG") &
                           one.prime_mover.ne("GT")&one.source_value_reported]
            observed=four.loc[four.source_value_reported]
            annual_gt=annual.loc[annual.prime_mover.eq("GT")]
            p4_gt=observed.loc[observed.prime_mover_page4.eq("GT")]
            if gt.empty or observed.empty:raise ValueError("Required GT or Page4 reporting missing")
            one_gt=float(gt.reported_signed_net_mwh.sum())
            four_gt=float(p4_gt.reported_signed_net_mwh.sum())
            one_non_gt=float(non_gt.reported_signed_net_mwh.sum())
            four_non_gt=float(observed.loc[observed.prime_mover_page4.ne("GT"),
                                           "reported_signed_net_mwh"].sum())
            rows.append({
                "plant_id":plant,"period":period,
                "annual_operable_generator_count":len(annual),
                "annual_gt_generator_count":len(annual_gt),
                "annual_gt_generator_ids":";".join(sorted(annual_gt.generator_id.astype(str))),
                "annual_gt_nameplate_mw":float(annual_gt.nameplate_capacity_mw.sum()),
                "page4_reported_generator_count":len(observed),
                "page4_exact_annual_id_matches":int(observed.exact_annual_generator_id_match.sum()),
                "page4_mover_matches_where_exact_id":int(
                    observed.prime_mover_same_as_annual_inventory.sum()),
                "page4_reported_gt_generator_count":len(p4_gt),
                "page1_gt_ng_mwh":one_gt,"page4_gt_mwh":four_gt,
                "page1_non_gt_ng_mwh":one_non_gt,
                "page4_non_gt_mwh":four_non_gt,
                "non_gt_residual_mwh":one_non_gt-four_non_gt,
                "gt_reporting_grain_difference_mwh":one_gt-four_gt,
                "possible_gt_population_present":bool(len(annual_gt)>0),
                "page1_gt_to_unit_allocation_certified":False})
    result=pd.DataFrame(rows)
    manifest={"target_plant_ids":list(TARGETS),
        "source_inventory":"EIA860 2024 Operable, 2024 annual identities",
        "source_actual_month":"EIA923 Page1 plant/fuel/prime-mover and Page4 generator reporting",
        "page4_exact_id_match_possible":True,
        "page1_gt_has_generator_id":False,
        "matching_gt_prime_mover_proves_gt_monthly_unit_allocation":False,
        "different_reporting_population_may_exist":True,
        "no_monthly_output_imputed":True,
        "heat_related_derating_calibrated":False,
        "actual_outage_or_eens_observed":False}
    return result,c.drop(columns="_merge"),manifest


def main():
    p=argparse.ArgumentParser()
    for arg in ("eia860","page1","page4","output"):
        p.add_argument("--"+arg,required=True)
    z=p.parse_args()
    read=lambda path:pd.read_csv(path,dtype={"plant_id":"string","generator_id":"string"})
    table,p4,metadata=gate(read(z.eia860),read(z.page1),read(z.page4))
    out=Path(z.output);out.mkdir(parents=True,exist_ok=True)
    table.to_csv(out/"target_gt_annual_generator_identity_gate.csv",index=False)
    p4.to_csv(out/"target_gt_page4_generator_id_join.csv",index=False)
    (out/"target_gt_annual_identity_manifest.json").write_text(
        json.dumps(metadata,indent=2)+"\n")
    print(table.to_string(index=False))

if __name__=="__main__":
    main()
