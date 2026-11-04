"""Controlled SRP 744h PyPSA: synthetic constant wind vs ERA5 site power-curve proxies.

All non-wind inputs and boundary are matched exactly between scenarios.
Weather-derived wind proxies are NOT calibrated wind-farm outputs; the
synthetic gas, coal, nuclear and other technology availability assumptions
are NOT physical heat response or observed forced outages.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from .srp_assumed_multitech_factorial import (
    capacity_from_annual_roster,matched_availability,BASE_PU)
from .srp_net_exchange_pypsa_screen import screened_load
from .multi_technology_dispatch import solve as dispatch


def validate_curve_hours(curve):
    needed={"timestamp_utc","curve_scenario","fleet_uncalibrated_proxy_pu"}
    if not needed.issubset(curve):raise ValueError("Missing ERA5 fleet proxy fields")
    data=curve.copy()
    data["timestamp_utc"]=pd.to_datetime(data.timestamp_utc,utc=True,errors="raise")
    data["fleet_uncalibrated_proxy_pu"]=pd.to_numeric(
        data.fleet_uncalibrated_proxy_pu,errors="coerce")
    if not np.isfinite(data.fleet_uncalibrated_proxy_pu.to_numpy(float)).all() or not (
        data.fleet_uncalibrated_proxy_pu.between(0,1).all()):
        raise ValueError("Invalid wind proxy range")
    expected=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    if data.curve_scenario.isna().any() or data.empty:
        raise ValueError("Missing wind curve names")
    for case,g in data.groupby("curve_scenario"):
        if len(g)!=744 or g.timestamp_utc.duplicated().any() or not pd.DatetimeIndex(
            g.timestamp_utc.sort_values()).equals(expected):
            raise ValueError("Missing or misaligned UTC wind hours")
    return data


def construct_cases(boundary,roster,curves,*,gas=.5,coal=.5,nuclear=.75):
    for factor in (gas,coal,nuclear):
        if not np.isfinite(factor) or not 0<=factor<=1:
            raise ValueError("Invalid resource stress multiplier")
    capacity,population=capacity_from_annual_roster(roster)
    if "wind" not in set(capacity.technology):
        raise ValueError("No wind nameplate in the modeled source BA roster")
    b=screened_load(boundary,"SRP")
    base=matched_availability(b,capacity)
    for tech,factor in (("gas",gas),("coal",coal),("nuclear",nuclear)):
        base.loc[base.technology.eq(tech),"availability_pu"]*=factor
    c=validate_curve_hours(curves)
    cases={"fixed_wind_0p35":base.copy()}
    for curve,frame in c.groupby("curve_scenario"):
        case="era5_"+str(curve)
        if case in cases:raise ValueError("Duplicate case")
        x=base.copy()
        wind=x.technology.eq("wind")
        ix=pd.to_datetime(x.loc[wind,"timestamp"],utc=True)
        profile=frame.set_index("timestamp_utc").fleet_uncalibrated_proxy_pu.reindex(ix)
        if profile.isna().any():raise ValueError("Unmatched site-weather hours")
        x.loc[wind,"availability_pu"]=profile.to_numpy()
        cases[case]=x
    return b,capacity,cases,population


def run(boundary,roster,curves,output,*,gas=.5,coal=.5,nuclear=.75):
    b,cap,cases,population=construct_cases(
        boundary,roster,curves,gas=gas,coal=coal,nuclear=nuclear)
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    b.to_csv(root/"matched_eia930_supply_requirement.csv",index=False)
    cap.to_csv(root/"matched_eia860_technology_capacity.csv",index=False)
    outcomes=[]
    for label,avail in cases.items():
        directory=root/label
        directory.mkdir(parents=True,exist_ok=True)
        avail.to_csv(directory/"source_matched_assumed_availability.csv",index=False)
        result=dispatch(root/"matched_eia930_supply_requirement.csv",
                        root/"matched_eia860_technology_capacity.csv",
                        directory/"source_matched_assumed_availability.csv",directory)
        if len(result)!=1 or result.ba.iloc[0]!="SRP":
            raise ValueError("Unexpected PyPSA output BA")
        hourly=pd.read_csv(directory/"shortfall_hourly_mw.csv")
        if len(hourly)!=744:raise ValueError("Incomplete optimized hourly outcomes")
        outcomes.append({"scenario":label,
                         "artificial_gap_mwh":float(result.unserved_energy_mwh.iloc[0]),
                         "positive_gap_hours":int((hourly.SRP_shortfall_mw>1e-6).sum()),
                         "mean_wind_assumed_or_proxy_pu":float(
                             avail.loc[avail.technology.eq("wind"),"availability_pu"].mean())})
    result=pd.DataFrame(outcomes)
    if len(result)!=4 or result.artificial_gap_mwh.lt(-1e-4).any():
        raise AssertionError("Expected fixed + three ERA5 curve controls")
    result.to_csv(root/"wind_proxy_matched_pypsa_comparison.csv",index=False)
    report={"experiment":"identical 744h BA requirement, EIA860 capacities, and nonwind assumptions",
            "gas_multiplier":gas,"coal_multiplier":coal,"nuclear_multiplier":nuclear,
            "reference_fixed_wind_pu":BASE_PU["wind"],
            "resource_population":population,
            "weather_site_point_100m_not_turbine_hub":True,
            "wind_curve_turbine_specific_calibration":False,
            "other_technologies_use_synthetic_profiles":True,
            "measured_shortfall_or_eens":False,
            "historical_reliability_calibrated":False,
            "weather_climate_causal_effect_identified":False}
    (root/"wind_proxy_matched_pypsa_manifest.json").write_text(
        json.dumps(report,indent=2)+"\n")
    print(result.to_string(index=False))
    return result,report


def main():
    p=argparse.ArgumentParser()
    for key in ("boundary","roster","curves","output"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    run(pd.read_csv(a.boundary),pd.read_csv(a.roster,dtype={
        "plant_id":"string","generator_id":"string"}),pd.read_csv(a.curves),a.output)


if __name__=="__main__":
    main()
