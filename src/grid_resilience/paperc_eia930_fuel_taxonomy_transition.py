"""Original EIA-930 wind/solar/hydro/storage taxonomy discontinuity audit.

Never collapse 2024 Jan-Jun legacy fuel categories into Jul-Dec split labels.
All reported numbers are signed source hourly means integrated over one hour;
blank is not zero. Reporting completeness is not BA supply adequacy.
"""
import argparse
import json
from pathlib import Path

import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
LABELS={
    "wind": {
        "legacy":("Wind",),
        "modern":("Wind without Integrated Battery Storage",
                  "Wind with Integrated Battery Storage")},
    "solar": {
        "legacy":("Solar",),
        "modern":("Solar without Integrated Battery Storage",
                  "Solar with Integrated Battery Storage")},
    "hydro": {
        "legacy":("Hydropower and Pumped Storage",),
        "modern":("Hydropower Excluding Pumped Storage","Pumped Storage")},
    "storage": {
        "legacy":(),
        "modern":("Battery Storage",)},
}
COHORT_HOURS={(2023,"Jul_Dec"):168,(2024,"Jan_Jun"):7,(2024,"Jul_Dec"):161}


def audit(hourly,scope):
    if scope.get("2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent") is not True:
        raise ValueError("Official EIA930 taxonomy discontinuity scope not verified")
    if scope.get("blank_never_assumed_zero") is not True:
        raise ValueError("Missing source-vintage blank-not-zero contract")
    need={"year","ba","utc_hour_start","original_partition","original_fuel_category",
          "reported_fuel_mwh","fuel_value_reported","reported_zero"}
    if not need.issubset(hourly):
        raise ValueError("Original hourly EIA930 source categories missing")
    if hourly.duplicated(["year","ba","utc_hour_start","original_fuel_category"]).any():
        raise ValueError("Duplicate original BA hour category")
    raw=hourly.copy()
    raw["utc_hour_start"]=pd.to_datetime(raw.utc_hour_start,utc=True)
    raw["fuel_value_reported"]=raw.fuel_value_reported.map(
        {True:True,False:False,"True":True,"False":False})
    raw["reported_zero"]=raw.reported_zero.map(
        {True:True,False:False,"True":True,"False":False})
    if raw[["fuel_value_reported","reported_zero"]].isna().any().any():
        raise ValueError("Invalid original reported vs zero state")
    if raw.loc[~raw.fuel_value_reported,"reported_fuel_mwh"].notna().any():
        raise ValueError("Missing official fuel reading was replaced with an invented value")
    if raw.loc[raw.fuel_value_reported,"reported_fuel_mwh"].isna().any():
        raise ValueError("Reported original fuel value unavailable")
    if raw.loc[raw.reported_zero,"reported_fuel_mwh"].ne(0).any():
        raise ValueError("Reported zero differs from numeric value")
    records=[]
    details=[]
    for (year,part),nh in COHORT_HOURS.items():
        style="legacy" if year==2023 or part=="Jan_Jun" else "modern"
        sample=raw.loc[raw.year.eq(year)&raw.original_partition.eq(part)]
        if sample.groupby("ba").utc_hour_start.nunique().to_dict()!={ba:nh for ba in BAS}:
            raise ValueError("Expected exact official BA+hour source partition coverage")
        for ba in BAS:
            current=sample.loc[sample.ba.eq(ba)]
            for family,names in LABELS.items():
                for label in names[style]:
                    group=current.loc[current.original_fuel_category.eq(label)].copy()
                    if len(group)!=nh or group.utc_hour_start.nunique()!=nh:
                        raise ValueError("Missing required original source category or hour")
                    observations=int(group.fuel_value_reported.sum())
                    blank=nh-observations
                    signed=group.reported_fuel_mwh.sum(min_count=1)
                    records.append({
                        "year":year,"ba":ba,"source_half":part,
                        "source_schema":style,"fuel_family_for_display_only":family,
                        "original_category_label":label,
                        "source_hours":nh,"reported_hours":observations,
                        "reported_zeros":int(group.reported_zero.sum()),
                        "blank_hours":blank,
                        "reported_fraction":observations/nh,
                        "signed_mwh_on_reported_hours_only":float(signed) if observations else None,
                        "partition_complete_mwh_only_if_no_blanks":float(signed) if blank==0 else None,
                        "cross_2024_schema_full_168h_fuel_total_certified":False,
                        "actual_hourly_available_mw_or_ens_identified":False})
                    details.append(group.assign(
                        fuel_family_for_display_only=family,
                        original_source_label_not_harmonized=True))
    out=pd.DataFrame(records)
    d=pd.concat(details,ignore_index=True)
    if len(out)!=4*(3+3+7):
        raise ValueError("Expected 52 BA-partition-category source rows")
    # No original year-2024 168h reconstruction from cross-schema categories.
    if out.loc[out.year.eq(2024),"cross_2024_schema_full_168h_fuel_total_certified"].any():
        raise ValueError("Unexpected cross-schema harmonization claim")
    state={"source_partitions":[{"year":y,"partition":p,"hours_per_ba":h}
                                for (y,p),h in COHORT_HOURS.items()],
           "fuel_families_for_display_only":list(LABELS),
           "legacy_and_modern_schema_mwh_not_automatically_additive":True,
           "missing_category_cells_not_zero_generation":True,
           "modern_battery_storage_not_equivalent_to_legacy_hydro_storage":True,
           "2023_and_2024_cohorts_different_dates":True,
           "source_reporting_not_historical_supply_adequacy":True}
    return d,out,state


def main():
    p=argparse.ArgumentParser()
    for x in ("hourly","manifest","output"):p.add_argument("--"+x,required=True)
    a=p.parse_args()
    d,s,m=audit(pd.read_csv(a.hourly),json.loads(Path(a.manifest).read_text()))
    target=Path(a.output);target.mkdir(parents=True,exist_ok=True)
    d.to_csv(target/"paper_c_wind_solar_hydro_storage_original_hourly_labels.csv",index=False)
    s.to_csv(target/"paper_c_wind_solar_hydro_storage_partition_coverage.csv",index=False)
    (target/"paper_c_wind_solar_hydro_storage_scope.json").write_text(json.dumps(m,indent=2)+"\n")
    print("SCHEMA-AWARE REPORTING COUNTS")
    print(s.groupby(["year","ba","source_half","fuel_family_for_display_only"])
          [["source_hours","reported_hours","blank_hours"]].sum().to_string())
    print("2024 SOURCE CATEGORY SUBSET")
    print(s.loc[s.year.eq(2024)].to_string(index=False))


if __name__=="__main__":
    main()
