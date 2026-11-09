"""Full original 2024 Jul-Dec EIA-930 fuel-schema reporting audit, 161h only.

No source null converted to zero; partial observed sum is descriptive only,
not generation closure or physical energy shortage. Compare to prior six-fuel
vector on identical BA UTC keys; never stitch the first seven legacy hours.
"""
import argparse
import json
from pathlib import Path

import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
START=pd.Timestamp("2024-07-01T07:00:00Z")
N=161

def analyze(fuel, six, manifest):
    if not manifest.get("blank_never_assumed_zero") or not manifest.get(
        "2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent"):
        raise ValueError("Original schema/missingness provenance absent")
    need={"year","ba","utc_hour_start","original_partition","original_fuel_category",
          "reported_fuel_mwh","fuel_value_reported"}
    if not need.issubset(fuel):
        raise ValueError("Original EIA-930 full fuel fields missing")
    x=fuel.loc[fuel.year.eq(2024)&fuel.original_partition.eq("Jul_Dec")].copy()
    x["utc_hour_start"]=pd.to_datetime(x.utc_hour_start,utc=True)
    expected={(ba,START+pd.Timedelta(hours=h)) for ba in BAS for h in range(N)}
    if set(zip(x.ba,x.utc_hour_start))!=expected:
        raise ValueError("Original source BA hour keys incomplete")
    if x.duplicated(["ba","utc_hour_start","original_fuel_category"]).any():
        raise ValueError("Duplicate BA-hour-fuel source record")
    labels=tuple(sorted(x.original_fuel_category.unique()))
    if len(labels)<12:
        raise ValueError("Original modern fuel taxonomy unexpectedly narrow")
    if x.groupby(["ba","utc_hour_start"]).original_fuel_category.nunique().ne(
        len(labels)).any():
        raise ValueError("Source category schema is not rectangular across BA hours")
    present=x.fuel_value_reported.astype(str).str.lower().map({"true":True,"false":False})
    if present.isna().any():raise ValueError("Invalid original reporting flag")
    x["numeric_reported"]=present.astype(bool)
    if x.loc[~x.numeric_reported,"reported_fuel_mwh"].notna().any():
        raise ValueError("Original null falsely imputed")
    if x.loc[x.numeric_reported,"reported_fuel_mwh"].isna().any():
        raise ValueError("Numeric original source cell missing")
    cat=(x.groupby(["ba","original_fuel_category"],as_index=False)
           .agg(required_hours=("numeric_reported","size"),
                numeric_hours=("numeric_reported","sum"),
                reported_zero_hours=("reported_fuel_mwh",lambda z:int((z==0).sum())),
                partial_observed_mwh=("reported_fuel_mwh",lambda z:z.sum(min_count=1))))
    cat["blank_hours"]=cat.required_hours-cat.numeric_hours
    cat["full_partition_mwh_only_when_no_blanks"]=cat.partial_observed_mwh.where(
        cat.blank_hours.eq(0))
    cat["missing_original_value_not_zero"]=True
    hour=(x.groupby(["ba","utc_hour_start"],as_index=False)
            .agg(fuel_labels_present=("original_fuel_category","size"),
                 numeric_fuel_cells=("numeric_reported","sum"),
                 observed_only_mwh=("reported_fuel_mwh",lambda z:z.sum(min_count=1))))
    hour["blank_fuel_cells"]=hour.fuel_labels_present-hour.numeric_fuel_cells
    hour["all_original_categories_numeric"]=hour.blank_fuel_cells.eq(0)
    hour["all_category_reported_mwh_only_if_complete"]=hour.observed_only_mwh.where(
        hour.all_original_categories_numeric)
    original=six.copy()
    original["utc_hour_start"]=pd.to_datetime(original.utc_hour_start,utc=True)
    if original.duplicated(["ba","utc_hour_start"]).any():
        raise ValueError("Duplicate six-category source row")
    need_six={"ba","utc_hour_start","net_generation_mw",
              "all_six_original_components_numeric",
              "sum_six_original_reported_components_mwh"}
    if not need_six.issubset(original):
        raise ValueError("Missing previous source-admitted six fuel baseline fields")
    joined=hour.merge(original[list(need_six)],on=["ba","utc_hour_start"],
                      validate="one_to_one",indicator=True)
    if len(joined)!=4*N or not joined["_merge"].eq("both").all():
        raise ValueError("Unmatched original six-fuel and full-fuel UTC cohort")
    joined=joined.drop(columns=["_merge"])
    joined["raw_net_minus_all_categories_only_if_complete"]=(
        joined.net_generation_mw-joined.all_category_reported_mwh_only_if_complete)
    joined["partial_observed_sum_not_exhaustive_supply"]=True
    joined["residual_not_generation_loss_imports_or_EENS"]=True
    summary=(joined.groupby("ba",as_index=False).agg(
        original_hours=("utc_hour_start","size"),
        total_numeric_category_cells=("numeric_fuel_cells","sum"),
        total_blank_category_cells=("blank_fuel_cells","sum"),
        hours_all_original_categories_numeric=("all_original_categories_numeric","sum"),
        hours_six_numeric=("all_six_original_components_numeric","sum"),
        original_ba_net_mwh=("net_generation_mw","sum")))
    summary["source_fuel_categories_per_hour"]=len(labels)
    scope={"year":2024,"source_partition":"2024 Jul_Dec only",
           "original_utc_start":START.isoformat(),"hours_per_ba":N,
           "original_category_labels":list(labels),
           "all_categories_complete_only_when_all_numeric":True,
           "original_source_nulls_never_imputed_to_zero":True,
           "partial_observed_sum_not_exhaustive_generation":True,
           "source_difference_not_physical_shortage_or_EENS":True,
           "2024_first_seven_hours_legacy_not_harmonized":True}
    return cat,joined,summary,scope

def main():
    a=argparse.ArgumentParser()
    for k in ("fuel","six","manifest","output"):
        a.add_argument("--"+k,required=True)
    p=a.parse_args()
    cat,joined,summary,scope=analyze(
        pd.read_csv(p.fuel),pd.read_csv(p.six),
        json.loads(Path(p.manifest).read_text()))
    out=Path(p.output);out.mkdir(parents=True,exist_ok=True)
    cat.to_csv(out/"paper_c_2024_161h_full_original_fuel_category_reporting.csv",index=False)
    joined.to_csv(out/"paper_c_2024_161h_full_original_fuel_hourly_completeness.csv",index=False)
    summary.to_csv(out/"paper_c_2024_161h_full_original_fuel_ba_summary.csv",index=False)
    (out/"paper_c_2024_161h_full_fuel_source_scope.json").write_text(
        json.dumps(scope,indent=2)+"\n")
    print("FULL ORIGINAL FUEL CATEGORIES",json.dumps(scope["original_category_labels"]))
    print("FULL FUEL BA REPORTING",summary.to_string(index=False))
    print("FULL FUEL PER CATEGORY",cat.to_string(index=False))

if __name__=="__main__":
    main()
