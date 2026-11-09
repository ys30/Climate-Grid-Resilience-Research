"""2024 original EIA930 within-schema (161h) fuel-components diagnostic.

The 7h older 2024 Jan-Jun schema is excluded. The six named ORIGINAL
Jul-Dec source categories are not a complete physical generation fleet.
A raw-BA-net minus reported-six-category sum is an arithmetic difference,
NOT unserved load, imports, fuel omission amount, line loss or EENS.
If any requested fuel category is blank at an hour, do not create a total.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
FUELS=("Natural Gas","Coal","Nuclear",
       "Wind without Integrated Battery Storage",
       "Solar without Integrated Battery Storage",
       "Hydropower Excluding Pumped Storage")
START=pd.Timestamp("2024-07-01T07:00:00Z")
HOURS=161


def audit(balance,fuel,manifest):
    if not manifest.get("2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent"):
        raise ValueError("Source fuel taxonomy change not certified")
    if not manifest.get("blank_never_assumed_zero"):
        raise ValueError("Original source blank-not-zero gate missing")
    keys={"year","ba","utc_hour_start","original_partition",
          "original_fuel_category","reported_fuel_mwh","fuel_value_reported"}
    if not keys.issubset(fuel):
        raise ValueError("Missing original EIA930 fuel reporting fields")
    required={"ba","utc_hour_start","source_partition","net_generation_mw",
              "demand_mw","net_interchange_mw"}
    if not required.issubset(balance):
        raise ValueError("Missing original EIA930 BA balance fields")
    f=fuel.loc[fuel.year.eq(2024)&fuel.original_partition.eq("Jul_Dec")&
               fuel.original_fuel_category.isin(FUELS)].copy()
    b=balance.loc[balance.source_partition.eq("2024_Jul_Dec")].copy()
    for obj in (f,b):
        obj["utc_hour_start"]=pd.to_datetime(obj.utc_hour_start,utc=True)
    expected={(ba,START+pd.Timedelta(hours=h)) for ba in BAS for h in range(HOURS)}
    if set(zip(b.ba,b.utc_hour_start))!=expected:
        raise ValueError("Modern source BA hour keys incomplete")
    if b.duplicated(["ba","utc_hour_start"]).any() or f.duplicated(
        ["ba","utc_hour_start","original_fuel_category"]).any():
        raise ValueError("Duplicate original source BA-hour category")
    if f.loc[~f.fuel_value_reported,"reported_fuel_mwh"].notna().any():
        raise ValueError("Null original category incorrectly replaced by zero or other value")
    if f.loc[f.fuel_value_reported,"reported_fuel_mwh"].isna().any():
        raise ValueError("Claimed numeric original source value missing")
    expected_category={(ba,t,name) for ba,t in expected for name in FUELS}
    if set(zip(f.ba,f.utc_hour_start,f.original_fuel_category))!=expected_category:
        raise ValueError("Missing 2024 modern source category keys")
    if b[["demand_mw","net_generation_mw"]].isna().any().any():
        raise ValueError("Official demand or net generation missing")
    grid=(f.pivot(index=["ba","utc_hour_start"],
                  columns="original_fuel_category",values="reported_fuel_mwh")
           .reset_index())
    grid=grid.merge(b[["ba","utc_hour_start","net_generation_mw","demand_mw",
                       "net_interchange_mw"]],on=["ba","utc_hour_start"],
                    how="inner",validate="one_to_one")
    if len(grid)!=len(expected):
        raise ValueError("Incomplete original BA-hour join")
    complete=grid[list(FUELS)].notna().all(axis=1)
    grid["all_six_original_components_numeric"]=complete
    grid["sum_six_original_reported_components_mwh"]=grid[list(FUELS)].sum(
        axis=1,min_count=len(FUELS))
    grid["net_minus_six_source_category_arithmetic_mwh"]=(
        grid.net_generation_mw-grid.sum_six_original_reported_components_mwh)
    grid["difference_not_unserved_energy_imports_or_generation_loss"]=True
    grid["all_generating_technologies_and_metered_dispatch_recovered"]=False
    grid["original_2024_legacy_first_7h_excluded"]=True
    grid["storage_soc_and_physical_intertie_calibration_verified"]=False
    summary=[]
    for ba in BAS:
        p=grid[grid.ba.eq(ba)]
        valid=p.loc[p.all_six_original_components_numeric]
        summary.append({
            "ba":ba,"original_modern_schema_source_hours":len(p),
            "hours_six_components_all_numeric":len(valid),
            "hours_incomplete_six_component_vector":len(p)-len(valid),
            "original_ba_net_generation_mwh":float(p.net_generation_mw.sum()),
            "six_component_reported_sum_mwh_complete_hours_only":
                float(valid.sum_six_original_reported_components_mwh.sum()) if len(valid) else None,
            "raw_ba_net_mwh_on_same_complete_hours":
                float(valid.net_generation_mw.sum()) if len(valid) else None,
            "net_minus_selected_components_same_hours_mwh":
                float(valid.net_minus_six_source_category_arithmetic_mwh.sum()) if len(valid) else None,
            "original_ti_numeric_hours":int(p.net_interchange_mw.notna().sum()),
            "no_claim_of_physical_generation_coverage_or_supply_adequacy":True,
            "original_modern_161h_not_complete_168h":True})
    summary=pd.DataFrame(summary)
    if not summary.original_modern_schema_source_hours.eq(HOURS).all():
        raise ValueError("Wrong modern source partition duration")
    scope={"study_window":"2024-07-01 07:00 to 2024-07-08 00:00 UTC exclusive",
           "modern_source_only_hours":161,
           "first_7h_legacy_source_kept_out_of_cross_category_sum":True,
           "original_selected_labels":list(FUELS),
           "any_blank_prevents_six_component_total_that_hour":True,
           "net_minus_selected_categories_not_necessarily_unreported_generation":True,
           "no_import_export_or_system_shortage_inference":True,
           "no_real_EENS_or_plant_availability_calibration":True}
    return grid,summary,scope


def main():
    p=argparse.ArgumentParser()
    for n in ("balance","fuel","manifest","output"):
        p.add_argument("--"+n,required=True)
    a=p.parse_args()
    data,summary,scope=audit(pd.read_csv(a.balance),pd.read_csv(a.fuel),
                             json.loads(Path(a.manifest).read_text()))
    dest=Path(a.output);dest.mkdir(parents=True,exist_ok=True)
    data.to_csv(dest/"paperc_july2024_161h_ba_six_fuel_original_hourly.csv",index=False)
    summary.to_csv(dest/"paperc_july2024_161h_ba_six_fuel_source_summary.csv",index=False)
    (dest/"paperc_july2024_161h_source_cohort_scope.json").write_text(
        json.dumps(scope,indent=2)+"\n")
    print("ORIGINAL 2024 MODERN SIX-FUEL COHORT",summary.to_string(index=False))


if __name__=="__main__":
    main()
