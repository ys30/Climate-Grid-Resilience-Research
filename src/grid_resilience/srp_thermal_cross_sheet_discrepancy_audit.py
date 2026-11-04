"""Audit EIA923 Page1-Page4 plant-month source discrepancies without calibration claims.

Consumes verified cross-sheet EIA923 overlap rows. Compare signed values only
for *both-reporting* plant-months, retaining unreported source rows as NaN.
A monthly report difference is a source reconciliation flag, never weather
derating, operating outage, generation efficiency, or a measurement error.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def analyze(plant_month, *, absolute_tolerance_mwh=1.0):
    needed={"period","plant_id","technology","nameplate_mw",
            "page1_technology_reported","page4_plant_reported",
            "page1_eligible_signed_net_mwh","page4_signed_net_mwh"}
    if not needed.issubset(plant_month):
        raise ValueError("Missing cross-sheet source reporting fields")
    if not np.isfinite(absolute_tolerance_mwh) or absolute_tolerance_mwh<0:
        raise ValueError("Invalid absolute reporting tolerance")
    x=plant_month.copy()
    x["plant_id"]=x.plant_id.astype("string").str.strip()
    for key in ("page1_technology_reported","page4_plant_reported"):
        if x[key].isna().any() or not x[key].isin([True,False]).all():
            raise ValueError("Missing boolean reporting identity")
    if x.duplicated(["period","plant_id"]).any():
        raise ValueError("Duplicate plant-month identity")
    if set(x.period)!={"2024-01","2024-07"} or set(x.technology)!={"gas","coal"}:
        raise ValueError("Unexpected thermal reporting scope")
    for field in ("page1_eligible_signed_net_mwh","page4_signed_net_mwh","nameplate_mw"):
        x[field]=pd.to_numeric(x[field],errors="coerce")
    if not np.isfinite(x.nameplate_mw.to_numpy(float)).all() or (x.nameplate_mw<=0).any():
        raise ValueError("Invalid annual nameplate")
    p1=x.page1_technology_reported
    p4=x.page4_plant_reported
    for key,mask in (("page1_eligible_signed_net_mwh",p1),
                     ("page4_signed_net_mwh",p4)):
        if x.loc[mask,key].isna().any() or not np.isfinite(x.loc[mask,key].to_numpy(float)).all():
            raise ValueError("Reported source generation missing")
        if x.loc[~mask,key].notna().any():
            raise ValueError("Unreported source generation must remain missing")
    x["both_sources_report"]=p1&p4
    both=x.loc[x.both_sources_report].copy()
    both["page1_minus_page4_mwh"]=(
        both.page1_eligible_signed_net_mwh-both.page4_signed_net_mwh)
    both["absolute_difference_mwh"]=both.page1_minus_page4_mwh.abs()
    both["flag_material_absolute_difference"]=(
        both.absolute_difference_mwh>absolute_tolerance_mwh)
    # Preserve signed contribution; absolute difference contribution is a
    # separate diagnostic and never a net energy deficit.
    totals=both.groupby(["period","technology"],as_index=False).agg(
        matched_plant_count=("plant_id","size"),
        page1_overlap_net_mwh=("page1_eligible_signed_net_mwh","sum"),
        page4_overlap_net_mwh=("page4_signed_net_mwh","sum"),
        net_source_difference_mwh=("page1_minus_page4_mwh","sum"),
        absolute_source_difference_mwh=("absolute_difference_mwh","sum"),
        flagged_plant_count=("flag_material_absolute_difference","sum"))
    both=both.merge(totals[["period","technology",
        "net_source_difference_mwh","absolute_source_difference_mwh"]],
        on=["period","technology"],validate="many_to_one")
    both["share_of_absolute_discrepancy"]=np.where(
        both.absolute_source_difference_mwh>0,
        both.absolute_difference_mwh/both.absolute_source_difference_mwh,np.nan)
    both=both.sort_values(["period","technology","absolute_difference_mwh"],
                          ascending=[True,True,False])
    population=x.groupby(["period","technology"],as_index=False).agg(
        eligible_source_plant_count=("plant_id","size"),
        page1_reported_count=("page1_technology_reported","sum"),
        page4_reported_count=("page4_plant_reported","sum"))
    totals=population.merge(totals,on=["period","technology"],validate="one_to_one")
    totals["any_missing_source_reporting"]=(
        (totals.page1_reported_count!=totals.eligible_source_plant_count)|
        (totals.page4_reported_count!=totals.eligible_source_plant_count))
    totals["source_net_difference_fraction_of_page4"]=np.where(
        totals.page4_overlap_net_mwh.abs()>0,
        totals.net_source_difference_mwh/totals.page4_overlap_net_mwh.abs(),
        np.nan)
    missing=x.loc[~x.both_sources_report,[
        "period","plant_id","technology","nameplate_mw",
        "page1_technology_reported","page4_plant_reported"]].sort_values(
        ["period","technology","plant_id"])
    # Reconcile per-plant numerics to independently reported totals.
    for item in totals.itertuples(index=False):
        group=both.loc[both.period.eq(item.period)&both.technology.eq(item.technology)]
        if not np.isclose(group.page1_minus_page4_mwh.sum(),
                          item.net_source_difference_mwh,atol=1e-6,rtol=0):
            raise AssertionError("Source net discrepancy conservation failed")
        if not np.isclose(group.absolute_difference_mwh.sum(),
                          item.absolute_source_difference_mwh,atol=1e-6,rtol=0):
            raise AssertionError("Source absolute discrepancy conservation failed")
    manifest={
        "periods":["2024-01","2024-07"],
        "source_grain":"EIA923 Page1 plant/fuel/mover vs Page4 generator/month",
        "absolute_difference_tolerance_mwh":float(absolute_tolerance_mwh),
        "missing_source_is_zero":False,
        "page1_and_page4_additive":False,
        "signed_net_differences_may_cancel":True,
        "difference_is_missing_electricity_or_outage":False,
        "monthly_difference_proves_thermal_derating":False,
        "source_scope_reconciled_to_unit_level":False,
        "historical_reliability_calibrated":False,
    }
    return both,totals,missing,manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--overlap",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    detail,summary,missing,manifest=analyze(pd.read_csv(args.overlap))
    root=Path(args.output);root.mkdir(parents=True,exist_ok=True)
    detail.to_csv(root/"source_discrepancy_ranked_plant_month.csv",index=False)
    summary.to_csv(root/"source_discrepancy_category_summary.csv",index=False)
    missing.to_csv(root/"source_missing_plant_month.csv",index=False)
    (root/"source_discrepancy_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print(summary.to_string(index=False))
    print(detail[["period","technology","plant_id","page1_minus_page4_mwh",
                  "share_of_absolute_discrepancy"]].to_string(index=False))


if __name__=="__main__":
    main()
