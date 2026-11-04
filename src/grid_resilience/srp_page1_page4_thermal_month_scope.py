"""Cross-sheet SRP thermal source reporting audit, EIA923 Page1 vs Page4.

Page1 plant/fuel/mover and Page4 generator/month report distinct scopes.
For matching plant IDs, net MWh can be *compared* as a diagnostic but must
never be added together or labeled independent measured generation.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

MONTHS=("2024-01","2024-07")


def reconcile(page1,page4,sites):
    for label,frame,columns in (
        ("page1",page1,{"plant_id","reported_ba","period","prime_mover","reported_fuel","net_generation_mwh"}),
        ("page4",page4,{"plant_id","generator_id","reported_ba","period","generation_mwh"}),
        ("sites",sites,{"plant_id","technology","nameplate_mw"})):
        if not columns.issubset(frame):
            raise ValueError(f"{label}: missing {sorted(columns-set(frame))}")
    a,b,s=page1.copy(),page4.copy(),sites.copy()
    for x in (a,b,s):
        x["plant_id"]=x.plant_id.astype("string").str.strip().str.replace(
            r"^0+(?=[0-9])","",regex=True)
        if x.plant_id.isna().any() or x.plant_id.eq("").any():
            raise ValueError("Invalid source plant identity")
    if s.plant_id.duplicated().any() or set(s.technology)!={"gas","coal"}:
        raise ValueError("Invalid unique annual EIA860 thermal site scope")
    s["nameplate_mw"]=pd.to_numeric(s.nameplate_mw,errors="coerce")
    if not np.isfinite(s.nameplate_mw.to_numpy(float)).all() or s.nameplate_mw.le(0).any():
        raise ValueError("Invalid nameplate")
    a=a.loc[a.reported_ba.astype("string").str.strip().eq("SRP") &
            a.period.astype("string").isin(MONTHS)].copy()
    b=b.loc[b.reported_ba.astype("string").str.strip().eq("SRP") &
            b.period.astype("string").isin(MONTHS)].copy()
    if b.duplicated(["plant_id","generator_id","reported_ba","period"]).any():
        raise ValueError("Duplicate Page4 source generator/month")
    for x,value in ((a,"net_generation_mwh"),(b,"generation_mwh")):
        x[value]=pd.to_numeric(x[value],errors="coerce")
        if not np.isfinite(x[value].to_numpy(float)).all():
            raise ValueError("Missing or nonfinite source generation")
    # Page1 fuel classes are official fuel/mover reporting categories.
    # A Page1 row is eligible for the cross-sheet diagnostic only with an
    # explicit technology match, not merely plant co-location.
    a["technology"]=np.select([
        a.reported_fuel.astype("string").str.upper().eq("NG") &
        a.prime_mover.astype("string").str.upper().isin(["GT","CT","CA","CS","ST"]),
        a.reported_fuel.astype("string").str.upper().eq("SUB") &
        a.prime_mover.astype("string").str.upper().eq("ST")],
        ["gas","coal"],default="different_fuel_or_mover")
    a=a.merge(s[["plant_id","technology"]],on="plant_id",how="inner",
              suffixes=("_p1","_inventory"),validate="many_to_one")
    a=a.loc[a.technology_p1.eq(a.technology_inventory)]
    one=a.groupby(["period","plant_id"],as_index=False).agg(
        page1_eligible_signed_net_mwh=("net_generation_mwh","sum"),
        page1_source_fuel_mover_rows=("net_generation_mwh","size"))
    four=b.merge(s[["plant_id"]],on="plant_id",how="inner",validate="many_to_one").groupby(
        ["period","plant_id"],as_index=False).agg(
        page4_signed_net_mwh=("generation_mwh","sum"),
        page4_reported_generators=("generator_id","nunique"))
    universe=pd.MultiIndex.from_product([MONTHS,sorted(s.plant_id)],
        names=["period","plant_id"]).to_frame(index=False)
    rows=universe.merge(s,on="plant_id",validate="many_to_one").merge(
        one,on=["period","plant_id"],how="left",validate="one_to_one").merge(
        four,on=["period","plant_id"],how="left",validate="one_to_one")
    rows["page1_technology_reported"]=rows.page1_source_fuel_mover_rows.notna()
    rows["page4_plant_reported"]=rows.page4_reported_generators.notna()
    rows["both_sources_report"]=rows.page1_technology_reported&rows.page4_plant_reported
    rows["source_difference_p1_minus_p4_mwh"]=(
        rows.page1_eligible_signed_net_mwh-rows.page4_signed_net_mwh)
    summary=[]
    for (period,technology),part in rows.groupby(["period","technology"]):
        common=part.loc[part.both_sources_report]
        summary.append({
            "period":period,"technology":technology,
            "annual_eia860_plant_count":len(part),
            "page1_technology_reported_plants":int(part.page1_technology_reported.sum()),
            "page4_reported_plants":int(part.page4_plant_reported.sum()),
            "both_sources_reported_plants":int(part.both_sources_report.sum()),
            "page1_only_plants":int((part.page1_technology_reported&~part.page4_plant_reported).sum()),
            "page4_only_plants":int((~part.page1_technology_reported&part.page4_plant_reported).sum()),
            "neither_source_plants":int((~part.page1_technology_reported&~part.page4_plant_reported).sum()),
            "both_sources_nameplate_mw":float(common.nameplate_mw.sum()),
            "page1_overlap_only_signed_mwh":float(common.page1_eligible_signed_net_mwh.sum()),
            "page4_overlap_only_signed_mwh":float(common.page4_signed_net_mwh.sum()),
            "overlap_difference_p1_minus_p4_mwh":float(common.source_difference_p1_minus_p4_mwh.sum()),
            "any_missing_reporting":bool(not part.both_sources_report.all())})
    stat=pd.DataFrame(summary).sort_values(["period","technology"])
    manifest={
        "scope":"SRP EIA860 Plant BA source-eligible annual gas/coal plants",
        "page1":"Page1 reported BA plant-fuel-mover month, only matching primary technology",
        "page4":"Page4 reported BA generator month, all movers aggregated within matched plant",
        "months":list(MONTHS),
        "source_values_are_signed":True,
        "page1_plus_page4_is_double_counted_generation":True,
        "page1_page4_direct_equivalence_guaranteed":False,
        "monthly_reconciliation_can_calibrate_hourly_heat_derating":False,
        "temperature_causality_estimated":False,
        "missing_is_zero":False,
        "historical_reliability_calibrated":False,
    }
    return rows,stat,manifest


def main():
    p=argparse.ArgumentParser()
    for key in ("page1-jan","page1-jul","page4","sites","output"):
        p.add_argument("--"+key,required=True)
    args=p.parse_args()
    a=pd.concat([pd.read_csv(args.page1_jan,dtype={"plant_id":"string"}),
                 pd.read_csv(args.page1_jul,dtype={"plant_id":"string"})],ignore_index=True)
    rows,stat,m=reconcile(a,pd.read_csv(args.page4,dtype={
        "plant_id":"string","generator_id":"string"}),
        pd.read_csv(args.sites,dtype={"plant_id":"string"}))
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    rows.to_csv(out/"thermal_page1_page4_plant_month_overlap.csv",index=False)
    stat.to_csv(out/"thermal_page1_page4_overlap_summary.csv",index=False)
    (out/"thermal_page1_page4_overlap_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print(stat.to_string(index=False))

if __name__=="__main__":
    main()
