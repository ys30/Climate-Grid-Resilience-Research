"""Join independently observed 2024 CAMD EPA unit hours to a pinned static EPA/EIA crosswalk.

An EPA unit may map to many EIA generators, or no generators. The crosswalk
is historical and neither operating hours nor gross load constitute
generator-specific net electrical MW or performance. Missing link != outage.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

TARGET=("141","55129","147")


def join_units(operating,relationships):
    a=operating.copy()
    b=relationships.copy()
    need_a={"oris","epa_unit_id","source_calendar_hour_rows",
            "positive_operating_time_rows","reported_operating_hours_sum",
            "positive_gross_load_rows"}
    need_b={"CAMD_PLANT_ID","CAMD_UNIT_ID","EIA_PLANT_ID","EIA_GENERATOR_ID",
            "EIA_UNIT_TYPE","MATCH_TYPE_GEN"}
    if not need_a.issubset(a) or not need_b.issubset(b):
        raise ValueError("Missing verified EPA 2024 or crosswalk source fields")
    for df,p,u in ((a,"oris","epa_unit_id"),(b,"CAMD_PLANT_ID","CAMD_UNIT_ID")):
        df[p]=df[p].astype("string").str.strip().str.replace(
            r"^0+(?=[0-9])","",regex=True)
        df[u]=df[u].astype("string").str.strip()
        if df[p].isna().any() or df[u].isna().any() or df[p].eq("").any() or df[u].eq("").any():
            raise ValueError("Missing normalized EPA unit ID")
    if a.duplicated(["oris","epa_unit_id"]).any():
        raise ValueError("Duplicate observed EPA unit")
    if set(a.oris)!=set(TARGET):
        raise ValueError("Incomplete target facility source coverage")
    a["source_calendar_hour_rows"]=pd.to_numeric(a.source_calendar_hour_rows,errors="raise")
    a["positive_operating_time_rows"]=pd.to_numeric(a.positive_operating_time_rows,errors="raise")
    a["reported_operating_hours_sum"]=pd.to_numeric(a.reported_operating_hours_sum,errors="raise")
    a["positive_gross_load_rows"]=pd.to_numeric(a.positive_gross_load_rows,errors="raise")
    if not a.source_calendar_hour_rows.eq(8784).all():
        raise ValueError("Incomplete source-calendar 2024 EPA unit reporting")
    if (a.positive_operating_time_rows>a.source_calendar_hour_rows).any() or a[
        ["positive_operating_time_rows","reported_operating_hours_sum",
         "positive_gross_load_rows"]].isna().any().any():
        raise ValueError("Invalid source operation coverage")
    b["EIA_PLANT_ID"]=b.EIA_PLANT_ID.astype("string").str.strip().str.replace(
        r"^0+(?=[0-9])","",regex=True)
    b=b.loc[b.CAMD_PLANT_ID.isin(TARGET)].copy()
    if not b.EIA_PLANT_ID.eq(b.CAMD_PLANT_ID).all():
        raise ValueError("EPA/EIA plant IDs differ: manually validate")
    b=b.loc[b.EIA_GENERATOR_ID.notna()&b.CAMD_UNIT_ID.notna()].copy()
    b["EIA_GENERATOR_ID"]=b.EIA_GENERATOR_ID.astype("string").str.strip()
    b["EIA_UNIT_TYPE"]=b.EIA_UNIT_TYPE.astype("string").str.strip()
    # Drop only exact duplicate relationships, never choose first among
    # one-to-many links or silently reclassify a mover into GT.
    b=b.drop_duplicates(["CAMD_PLANT_ID","CAMD_UNIT_ID",
                         "EIA_GENERATOR_ID","EIA_UNIT_TYPE"])
    bridge=a.merge(b,left_on=["oris","epa_unit_id"],
        right_on=["CAMD_PLANT_ID","CAMD_UNIT_ID"],
        how="left",validate="one_to_many",indicator=True)
    rows=[]
    for (plant,unit),g in bridge.groupby(["oris","epa_unit_id"],sort=True):
        found=g.loc[g._merge.eq("both")]
        rows.append({
            "oris":str(plant),"epa_unit_id":str(unit),
            "source_calendar_hour_rows":int(g.source_calendar_hour_rows.iloc[0]),
            "positive_operating_time_rows":int(g.positive_operating_time_rows.iloc[0]),
            "reported_operating_hours_sum":float(g.reported_operating_hours_sum.iloc[0]),
            "positive_gross_load_rows":int(g.positive_gross_load_rows.iloc[0]),
            "direct_static_crosswalk_relationship_count":len(found),
            "linked_eia_generator_ids":";".join(sorted(
                set(found.EIA_GENERATOR_ID.dropna().astype(str)))),
            "linked_eia_prime_mover_classes":";".join(sorted(
                set(found.EIA_UNIT_TYPE.dropna().astype(str)))),
            "static_crosswalk_unit_found":bool(len(found)),
            "eia860_gt_generator_directly_linked":bool(
                found.EIA_UNIT_TYPE.astype(str).eq("GT").any()),
            "actual_eia_generator_net_mw_validated":False,
            "2024_ecmps_monitoring_plan_verified":False
        })
    result=pd.DataFrame(rows)
    summary=result.groupby("oris",as_index=False).agg(
        observed_epa_units=("epa_unit_id","size"),
        units_with_static_crosswalk=("static_crosswalk_unit_found","sum"),
        units_without_static_crosswalk=("static_crosswalk_unit_found",
                                         lambda s:int((~s).sum())),
        units_with_direct_gt_class_link=("eia860_gt_generator_directly_linked","sum"))
    metadata={
        "source_2024_epa_calendar_unit_rows_run":41888598785,
        "source_pinned_epa_eia_crosswalk_run":41876110511,
        "crosswalk_is_verified_2024_generator_mapping":False,
        "eia_gt_generator_net_mw_inferred":False,
        "epacamd_hourly_gross_load_is_eia_generator_net_mw":False,
        "unmapped_source_unit_is_outage":False,
        "actual_temperature_derating_calibrated":False,
        "epa_source_hour_date_timezone_verified":False,
        "matching_eia_id_or_mover_is_not_physical_electric_power_allocation":True
    }
    return result,summary,bridge.drop(columns="_merge"),metadata


def main():
    p=argparse.ArgumentParser()
    for key in ("operation","crosswalk","output"):
        p.add_argument("--"+key,required=True)
    args=p.parse_args()
    result,summary,detail,meta=join_units(
        pd.read_csv(args.operation,dtype={"oris":"string","epa_unit_id":"string"}),
        pd.read_csv(args.crosswalk,dtype="string"))
    root=Path(args.output);root.mkdir(parents=True,exist_ok=True)
    result.to_csv(root/"epa_2024_unit_to_eia_static_link_summary.csv",index=False)
    summary.to_csv(root/"epa_2024_plant_crosswalk_coverage.csv",index=False)
    detail.to_csv(root/"epa_2024_unit_static_relationship_rows.csv",index=False)
    (root/"epa_2024_unit_crosswalk_manifest.json").write_text(
        json.dumps(meta,indent=2)+"\n")
    print(summary.to_string(index=False))
    print(result.to_string(index=False))


if __name__=="__main__":
    main()
