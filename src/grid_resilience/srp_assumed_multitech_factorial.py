"""Matched 744h SRP multi-tech *assumption-only* PyPSA sensitivity.

EIA-860 annual SRP Plant BA nameplates provide capacity classes; EIA-930
demand and net interchange provide hourly boundary. No EIA-930 generation,
EIA-923 plant net MWh, weather observations or calibrated forced outages
enter technology availability. Results are SCREENING ONLY, not EENS.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .srp_net_exchange_pypsa_screen import screened_load
from .multi_technology_dispatch import solve as pypsa_solve

PRIMARY_FUEL = {"NG":"gas","SUB":"coal","NUC":"nuclear",
                "SUN":"solar","WND":"wind","WAT":"hydro"}
BASE_PU = {"gas":0.85,"coal":0.85,"nuclear":0.90,
           "hydro":0.50,"wind":0.35,"solar":0.80}
SCENARIOS = {
    "baseline": (1.0,1.0),
    "thermal_derating": (0.8,1.0),
    "wind_derating": (1.0,0.6),
    "compound": (0.8,0.6),
}


def capacity_from_annual_roster(roster, *, ba="SRP"):
    required={"plant_id","generator_id","plant_reported_ba",
              "energy_source_1","prime_mover","nameplate_capacity_mw"}
    if not required.issubset(roster):
        raise ValueError("Missing official EIA860 Plant BA/identity/fuel/capacity")
    r=roster.copy()
    for key in ("plant_id","generator_id","plant_reported_ba"):
        r[key]=r[key].astype("string").str.strip()
        if r[key].isna().any() or r[key].eq("").any():
            raise ValueError("Missing official EIA860 identity")
    r["plant_id"]=r.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
    r=r.loc[r.plant_reported_ba.eq(ba)].copy()
    if r.empty or r.duplicated(["plant_id","generator_id"]).any():
        raise ValueError("Empty BA or duplicate plant generator identity")
    r["nameplate_capacity_mw"]=pd.to_numeric(r.nameplate_capacity_mw,errors="coerce")
    if not np.isfinite(r.nameplate_capacity_mw.to_numpy(float)).all() or r.nameplate_capacity_mw.lt(0).any():
        raise ValueError("Invalid official nameplate")
    r["primary_fuel"]=r.energy_source_1.astype("string").str.strip()
    r["prime_mover"]=r.prime_mover.astype("string").str.strip()
    # Never turn pumped-storage PS (WAT), battery BA, or unreviewed mover/fuel
    # combinations into free dispatchable hydro or another supply technology.
    mover_rules={"gas":{"GT","CT","CA","CS","ST"},
                 "coal":{"ST"},"nuclear":{"ST"},
                 "hydro":{"HY"},"solar":{"PV"},"wind":{"WT"}}
    r["technology"]=r.primary_fuel.map(PRIMARY_FUEL)
    valid=r.apply(lambda row: row.technology in mover_rules and
                  row.prime_mover in mover_rules[row.technology],axis=1)
    r.loc[~valid,"technology"]=pd.NA
    included=r.loc[r.technology.notna()].copy()
    excluded=r.loc[r.technology.isna()].copy()
    if included.empty:raise ValueError("No explicitly classifiable technologies")
    c=included.groupby("technology",as_index=False).agg(
        capacity_mw=("nameplate_capacity_mw","sum"),
        roster_generators=("generator_id","size"))
    c["ba"]=ba
    c["marginal_cost"]=c.technology.map({
        "nuclear":10.,"wind":2.,"solar":3.,"hydro":5.,
        "coal":45.,"gas":55.})
    c=c[["ba","technology","capacity_mw","marginal_cost","roster_generators"]]
    report={"ba":ba,"official_ba_generator_rows":len(r),
            "included_generator_rows":len(included),
            "excluded_generator_rows":len(excluded),
            "excluded_primary_fuel_counts":excluded.primary_fuel.value_counts(dropna=False).to_dict(),
            "assigned_nameplate_mw":float(included.nameplate_capacity_mw.sum()),
            "excluded_nameplate_mw":float(excluded.nameplate_capacity_mw.sum()),
            "fuel_classification_is_primary_source_only":True,
            "prime_mover_classification_gate_applied":True,
            "pumped_storage_and_battery_excluded":True,
            "multi_fuel_dispatch_verified":False,
            "storage_soc_modeled":False,
            "ba_physical_dispatch_rights_verified":False,
            "historical_calibration_certified":False}
    return c,report


def matched_availability(demand, capacity, *, local_utc_offset_hours=-7):
    required={"timestamp","ba","demand_mw"}
    if not required.issubset(demand):raise ValueError("Missing boundary source fields")
    d=demand.copy()
    d["timestamp"]=pd.to_datetime(d.timestamp,utc=True,errors="raise")
    if d.timestamp.duplicated().any() or d.empty:
        raise ValueError("Duplicate or empty time series")
    if len(d)!=744 or not pd.DatetimeIndex(d.timestamp.sort_values()).equals(
            pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")):
        raise ValueError("This first experiment requires 744 UTC January hours")
    if not np.isfinite(pd.to_numeric(d.demand_mw,errors="coerce").to_numpy(float)).all():
        raise ValueError("Nonfinite boundary requirement")
    if (d.demand_mw<0).any():raise ValueError("Negative supply requirement")
    ts=d.timestamp.sort_values()
    local_hour=(ts.dt.hour.to_numpy()+local_utc_offset_hours)%24
    # Assumed daylight-only sine, not solar irradiance or observed PV output.
    day=np.maximum(np.sin(np.pi*(local_hour-6)/12),0.)
    rows=[]
    for r in capacity.itertuples(index=False):
        if r.technology not in BASE_PU:raise ValueError("Unsupported classification")
        profile=(BASE_PU[r.technology]*day if r.technology=="solar" else
                 np.full(len(ts),BASE_PU[r.technology]))
        for timestamp,value in zip(ts,profile):
            rows.append({"timestamp":timestamp.isoformat(),"ba":r.ba,
                         "technology":r.technology,
                         "availability_pu":float(value)})
    result=pd.DataFrame(rows)
    if result.duplicated(["timestamp","ba","technology"]).any():
        raise ValueError("Duplicate assumed tech profile")
    return result


def run(boundary,roster,output,*,ba="SRP"):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    c,capreport=capacity_from_annual_roster(roster,ba=ba)
    d=screened_load(boundary,ba)
    base=matched_availability(d,c)
    d.to_csv(out/"assumed_multitech_boundary.csv",index=False)
    c.to_csv(out/"assumed_multitech_capacity.csv",index=False)
    results=[]
    for case,(thermal_factor,wind_factor) in SCENARIOS.items():
        avail=base.copy()
        thermal=avail.technology.isin(["gas","coal","nuclear"])
        avail.loc[thermal,"availability_pu"]*=thermal_factor
        avail.loc[avail.technology.eq("wind"),"availability_pu"]*=wind_factor
        folder=out/case
        folder.mkdir(parents=True,exist_ok=True)
        avail.to_csv(folder/"availability.csv",index=False)
        solved=pypsa_solve(out/"assumed_multitech_boundary.csv",
                           out/"assumed_multitech_capacity.csv",
                           folder/"availability.csv",folder)
        if len(solved)!=1 or solved.ba.iloc[0]!=ba:
            raise ValueError("Unexpected BA solver output")
        results.append({"scenario":case,"assumed_thermal_factor":thermal_factor,
                        "assumed_wind_factor":wind_factor,
                        "modeled_gap_mwh":float(solved.unserved_energy_mwh.iloc[0])})
    summary=pd.DataFrame(results)
    gaps=summary.set_index("scenario").modeled_gap_mwh
    if gaps["baseline"]>gaps["thermal_derating"]+1e-3 or gaps["baseline"]>gaps["wind_derating"]+1e-3:
        raise AssertionError("Stronger source-independent derating decreased shortage")
    if gaps["thermal_derating"]>gaps["compound"]+1e-3 or gaps["wind_derating"]>gaps["compound"]+1e-3:
        raise AssertionError("Compound derating decreased shortage")
    interaction=float(gaps["compound"]-gaps["thermal_derating"]-gaps["wind_derating"]+gaps["baseline"])
    summary.to_csv(out/"assumed_multitech_four_case_results.csv",index=False)
    manifest={"source_population":capreport,
        "scenarios":{name:{"thermal_multiplier":t,"wind_multiplier":w}
                      for name,(t,w) in SCENARIOS.items()},
        "default_technology_pu":BASE_PU,
        "solar_daylight_utc_offset_hours_assumed":-7,
        "nonadditive_interaction_mwh":interaction,
        "independent_of_eia930_fuel_generation_replay":True,
        "technology_availability_is_synthetic_not_meteorology":True,
        "physical_BA_fleet_complete":False,
        "real_outages_or_EENS_inferred":False,
        "historical_calibration_certified":False}
    (out/"assumed_multitech_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(summary.to_string(index=False))
    return summary,manifest


def main():
    p=argparse.ArgumentParser()
    for key in ("boundary","roster","output"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    run(pd.read_csv(a.boundary),
        pd.read_csv(a.roster,dtype={"plant_id":"string","generator_id":"string"}),
        a.output)


if __name__=="__main__":
    main()
