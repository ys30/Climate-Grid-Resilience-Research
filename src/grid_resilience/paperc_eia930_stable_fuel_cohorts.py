"""Source-admitted stable EIA930 hourly fuel categories across 2023/24 original archives.

Intersection-of-labels alone is NOT semantic equivalence; allow only a
small explicit predeclared stable label set, preserving reporting-null hours.
Different historical study weeks are distinct, not a controlled year effect.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
COHORTS={2023:"2023-07-10T00:00:00Z",2024:"2024-07-01T00:00:00Z"}
STABLE=("Coal","Natural Gas","Nuclear")


def admitted(hourly,meta):
    needed={"year","utc_hour_start","ba","original_partition",
            "original_fuel_category","reported_fuel_mwh","fuel_value_reported",
            "reported_zero"}
    if not needed.issubset(hourly):raise ValueError("Missing original source fuel field")
    if not meta.get("2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent"):
        raise ValueError("Original EIA930 taxonomy revision not retained")
    raw=hourly.copy()
    raw["utc_hour_start"]=pd.to_datetime(raw.utc_hour_start,utc=True,errors="raise")
    if raw.duplicated(["year","ba","utc_hour_start","original_fuel_category"]).any():
        raise ValueError("Duplicate original BA hour category")
    original=raw.loc[raw.original_fuel_category.isin(STABLE)].copy()
    expected={}
    for year,start in COHORTS.items():
        times=pd.date_range(start,periods=168,freq="h")
        expected[year]=set(times)
        for ba in BAS:
            for fuel in STABLE:
                x=original[(original.year==year)&original.ba.eq(ba)&
                           original.original_fuel_category.eq(fuel)]
                if len(x)!=168 or set(x.utc_hour_start)!=expected[year]:
                    raise ValueError("Stable fuel category did not cover all 168 source BA hours")
                if year==2024:
                    first=x[x.original_partition.eq("Jan_Jun")]
                    latter=x[x.original_partition.eq("Jul_Dec")]
                    if len(first)!=7 or len(latter)!=161:
                        raise ValueError("Original 2024 boundary 7/161 not preserved")
    if set(original.year)!={2023,2024} or set(original.ba)!=set(BAS):
        raise ValueError("Missing source population")
    original["fuel_value_reported"]=original.fuel_value_reported.map(
        {True:True,False:False,"True":True,"False":False})
    if original.fuel_value_reported.isna().any():
        raise ValueError("Invalid original reporting status")
    if original.loc[~original.fuel_value_reported,"reported_fuel_mwh"].notna().any():
        raise ValueError("Missing original fuel values cannot be silently filled")
    if original.loc[original.fuel_value_reported,"reported_fuel_mwh"].isna().any():
        raise ValueError("Claimed reported fuel value missing")
    original["reported_full_window_mwh_only_if_complete"]=pd.NA
    original["eia930_reported_fuel_not_available_generator_capacity"]=True
    groups=[]
    for (year,ba,fuel),g in original.groupby(
            ["year","ba","original_fuel_category"],sort=True):
        count=int(g.fuel_value_reported.sum())
        rawsum=g.reported_fuel_mwh.sum(min_count=1)
        groups.append({"year":int(year),"ba":ba,"stable_original_category":fuel,
            "source_hours":len(g),"reported_hours":count,"blank_hours":len(g)-count,
            "reported_zero_hours":int(g.reported_zero.sum()),
            "signed_reported_hours_energy_mwh":float(rawsum) if count else None,
            "full_168h_reported_energy_mwh":float(rawsum) if count==168 else None,
            "full_168h_fuel_energy_comparison_eligible":count==168,
            "2023_2024_same_july_week":False,
            "source_reported_energy_not_firm_capacity":True})
    summary=pd.DataFrame(groups)
    if len(summary)!=2*4*len(STABLE):
        raise ValueError("Unexpected stable original EIA930 category inventory")
    scope={"study_days":{"2023":"2023-07-10 through 2023-07-16 UTC",
                         "2024":"2024-07-01 through 2024-07-07 UTC"},
        "unchanged_original_fuel_labels_admitted":list(STABLE),
        "reporting_blank_is_not_zero":True,
        "2024_wind_solar_hydro_battery_taxonomy_not_harmonized":True,
        "full_168h_value_only_when_all_hours_reported":True,
        "same_hours_different_dates_prevent_naive_interannual_effect_estimate":True,
        "actual_hourly_generation_is_not_available_capacity_or_EENS":True}
    return original,summary,scope


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    hourly,summary,scope=admitted(
        pd.read_csv(a.source),json.loads(Path(a.manifest).read_text()))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    hourly.to_csv(out/"paperc_stable_category_two_cohorts_hourly.csv",index=False)
    summary.to_csv(out/"paperc_stable_category_two_cohorts_summary.csv",index=False)
    (out/"paperc_stable_category_source_scope.json").write_text(
        json.dumps(scope,indent=2)+"\n")
    print(summary.to_string(index=False))
    print(json.dumps({"eligible_full_windows":int(summary.full_168h_fuel_energy_comparison_eligible.sum()),
          "category_groups":len(summary)},indent=2))


if __name__=="__main__":main()
