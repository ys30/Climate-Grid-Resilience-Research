"""Paper C 2024 seven-day four-BA PyPSA historical baseline admission matrix.

Join ORIGINAL EIA930 raw balance, source-native category reporting and CISO
information-only battery telemetry provenance. A fully source-keyed observation
is NOT a historically adequate four-BA physical PyPSA model, and a BA with
balance closure is not granted transfer ratings, generator availability,
SOC or source-calibrated unserved energy.
"""
import argparse
import json
from pathlib import Path

import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
START="2024-07-01T00:00:00Z"
STABLE=("Natural Gas","Coal","Nuclear")
IMPORTANT_MODERN=("Solar without Integrated Battery Storage",
                  "Wind without Integrated Battery Storage",
                  "Hydropower Excluding Pumped Storage",
                  "Battery Storage","Pumped Storage")


def evaluate(balance,fuels,raw_manifest,fuel_manifest,battery_manifest):
    if not raw_manifest.get("source_ba_hours_complete") or not raw_manifest.get(
        "raw_reported_values_never_imputed"):
        raise ValueError("2024 original 672-hour BA source accounting was not verified")
    if not fuel_manifest.get("2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent"):
        raise ValueError("Official 2024 EIA930 fuel schema revision not preserved")
    if not battery_manifest.get("no_storage_energy_mwh_initial_soc_or_efficiency_inferred"):
        raise ValueError("CISO source battery SOC and energy-rating uncertainty not preserved")
    needed_balance={"ba","utc_hour_start","demand_mw","net_generation_mw",
                    "net_interchange_mw","raw_arithmetic_closes",
                    "source_partition","raw_triplet_present"}
    needed_fuel={"year","ba","utc_hour_start","original_fuel_category",
                 "reported_fuel_mwh","fuel_value_reported","original_partition"}
    if not needed_balance.issubset(balance) or not needed_fuel.issubset(fuels):
        raise ValueError("Missing original EIA930 hourly source columns")
    b=balance.copy()
    f=fuels.loc[fuels.year.eq(2024)].copy()
    b["utc_hour_start"]=pd.to_datetime(b.utc_hour_start,utc=True)
    f["utc_hour_start"]=pd.to_datetime(f.utc_hour_start,utc=True)
    times=set(pd.date_range(START,periods=168,freq="h"))
    expected={(ba,t) for ba in BAS for t in times}
    if set(b.ba)!=set(BAS) or set(zip(b.ba,b.utc_hour_start))!=expected:
        raise ValueError("Original 2024 balance BA-hour grid incomplete")
    if b.duplicated(["ba","utc_hour_start"]).any() or f.duplicated(
        ["ba","utc_hour_start","original_fuel_category"]).any():
        raise ValueError("Duplicated original EIA930 source key")
    if set(zip(f.ba,f.utc_hour_start))!=expected:
        raise ValueError("Original 2024 fuel category BA-hour grid incomplete")
    if b.demand_mw.isna().any() or b.net_generation_mw.isna().any():
        raise ValueError("Original 2024 hourly net generation or demand not complete")
    if b.demand_mw.lt(0).any():
        raise ValueError("Invalid negative source demand")
    if b.loc[~b.raw_triplet_present,"net_interchange_mw"].notna().any():
        raise ValueError("Original raw triplet missingness inconsistent")
    if f.loc[~f.fuel_value_reported,"reported_fuel_mwh"].notna().any():
        raise ValueError("Original source blank fuel value was silently filled")
    check=f.merge(b[["ba","utc_hour_start","net_generation_mw","source_partition"]],
                  on=["ba","utc_hour_start"],validate="many_to_one")
    if len(check)!=len(f):
        raise ValueError("Original EIA930 fuel-to-balance row join incomplete")
    expected_part=check.original_partition.apply(lambda x:"2024_"+x)
    if not check.source_partition.eq(expected_part).all():
        raise ValueError("2024 original semiannual source partition differs across data products")
    # A reporting category with an original null is not a witnessed zero-MW generator.
    detail=[]
    for ba in BAS:
        source_ba=b[b.ba.eq(ba)]
        source_f=f[f.ba.eq(ba)]
        old=source_f[source_f.original_partition.eq("Jan_Jun")]
        new=source_f[source_f.original_partition.eq("Jul_Dec")]
        assert source_ba.shape[0]==168
        for label in STABLE:
            t=source_f[source_f.original_fuel_category.eq(label)]
            if len(t)!=168:
                raise ValueError("Original stable fuel source category hours missing")
            detail.append({"ba":ba,"original_category":label,"required_source_hours":168,
                "reported_hours":int(t.fuel_value_reported.sum()),
                "missing_hours":int((~t.fuel_value_reported).sum()),
                "source_partition":"7h old + 161h new",
                "numeric_source_completely_observed":bool(t.fuel_value_reported.all()),
                "physical_generator_availability_verified":False})
        for label in IMPORTANT_MODERN:
            t=new[new.original_fuel_category.eq(label)]
            if len(t)!=161:
                raise ValueError("Original post-reclassification fuel reporting label absent")
            detail.append({"ba":ba,"original_category":label,"required_source_hours":161,
                "reported_hours":int(t.fuel_value_reported.sum()),
                "missing_hours":int((~t.fuel_value_reported).sum()),
                "source_partition":"161h new only; first 7h legacy noncomparable",
                "numeric_source_completely_observed":bool(t.fuel_value_reported.all()),
                "physical_generator_availability_verified":False})
    report=pd.DataFrame(detail)
    rows=[]
    for ba in BAS:
        p=b.loc[b.ba.eq(ba)]
        x=report[report.ba.eq(ba)]
        missing_ti=int(p.net_interchange_mw.isna().sum())
        bad_close=int((~p.raw_arithmetic_closes.astype(bool)).sum())
        rows.append({
            "year":2024,"ba":ba,
            "observed_utc_hour_start_count":len(p),
            "hourly_original_demand_present_count":int(p.demand_mw.notna().sum()),
            "hourly_original_net_generation_present_count":int(p.net_generation_mw.notna().sum()),
            "hourly_original_total_interchange_present_count":int(p.net_interchange_mw.notna().sum()),
            "raw_total_interchange_missing_hours":missing_ti,
            "raw_arithmetic_nonclosing_or_incomplete_hours":bad_close,
            "category_groups_complete_numeric":int(x.numeric_source_completely_observed.sum()),
            "category_groups_total_screened":len(x),
            "modern_original_battery_reported_hours":int(x.loc[
                x.original_category.eq("Battery Storage"),"reported_hours"].iloc[0]),
            "historical_information_battery_5min_source_available":ba=="CISO",
            "historical_battery_power_telemetry_points_if_CISO":2016 if ba=="CISO" else None,
            "battery_physical_soc_and_energy_mwh_verified":False,
            "fuel_technology_mapping_and_plant_availability_complete":False,
            "transmission_intertie_physical_ratings_verified":False,
            "hydro_energy_and_storage_constraints_verified":False,
            "historical_pypsa_four_ba_calibration_admissible":False,
            "historical_EENS_or_shortage_inference_admissible":False,
            "reason_not_admissible":(
                "Original BA source nonclosure/missing TI; unequal old/new fuel technology "
                "reporting; unknown hourly plant availability; missing hydro/storage "
                "energy constraints and verified intertie ratings; CAISO battery "
                "informational telemetry does not establish SOC or system adequacy.")
        })
    matrix=pd.DataFrame(rows)
    if len(report)!=4*(len(STABLE)+len(IMPORTANT_MODERN)):
        raise ValueError("Four BA × eight source-category completeness rows expected")
    if matrix.historical_pypsa_four_ba_calibration_admissible.any():
        raise ValueError("Unjustified source-based physical baseline admission")
    scope={"study_window":START+" / 168h",
        "source_input_1":"EIA930 July 2024 original Jan-Jun and Jul-Dec BA raw D/NG/TI hourly",
        "source_input_2":"Original EIA930 2023/24 source-native fuel category hourly audit, 2024 subset",
        "source_input_3":"CAISO original historical 5min battery information-only power envelope",
        "source_join":"Exact UTC start-hour + original BA; archive partition verified",
        "not_technically_calibrated_generator_availability":True,
        "no_verified_historical_battery_SOC_or_MWh":True,
        "no_verified_historical_intertie_capacity":True,
        "no_historical_energy_not_served_calculated":True,
        "full_source_hour_coverage_does_not_prove_physical_adequacy":True}
    return matrix,report,scope


def main():
    p=argparse.ArgumentParser()
    for k in ("balance","fuel","balance-manifest","fuel-manifest",
              "battery-manifest","output"):
        p.add_argument("--"+k,required=True)
    a=p.parse_args()
    matrix,detail,scope=evaluate(
        pd.read_csv(a.balance),pd.read_csv(a.fuel),
        json.loads(Path(a.balance_manifest).read_text()),
        json.loads(Path(a.fuel_manifest).read_text()),
        json.loads(Path(a.battery_manifest).read_text()))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    matrix.to_csv(out/"paper_c_2024_historical_baseline_source_admission_by_ba.csv",index=False)
    detail.to_csv(out/"paper_c_2024_original_fuel_report_completeness_by_ba.csv",index=False)
    (out/"paper_c_2024_historical_baseline_admission_scope.json").write_text(
        json.dumps(scope,indent=2)+"\n")
    print("SOURCE-VALIDATED 2024 BA HISTORICAL BASELINE ADMISSION",matrix.to_string(index=False))


if __name__=="__main__":
    main()
