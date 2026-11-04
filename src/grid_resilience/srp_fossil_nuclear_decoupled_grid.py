"""Fossil vs nuclear availability decoupling in an assumed SRP screening grid.

EIA-860 Plant BA annual generator nameplate, EIA-930 observed hourly demand
and net interchange. Availability assumptions are synthetic; generation is
not replayed. Zero artificial gap is not evidence of historical adequacy.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .multi_technology_dispatch import solve as dispatch
from .srp_net_exchange_pypsa_screen import screened_load
from .srp_assumed_multitech_factorial import (
    BASE_PU, capacity_from_annual_roster, matched_availability
)

FOSSIL_FACTORS=(0.5,0.625,0.75,0.875,1.)
NUCLEAR_FACTORS=(0.75,1.)
WIND_FACTORS=(0.,1.)


def validate_factors(values, name):
    a=np.asarray(values,dtype=float)
    if a.ndim!=1 or len(a)<2 or not np.isfinite(a).all():
        raise ValueError("Missing/nonfinite "+name+" factors")
    if (a<0).any() or (a>1).any() or len(set(a))!=len(a):
        raise ValueError("Invalid or duplicate "+name+" factors")
    return sorted(a.tolist())


def summarize(table, *, eps=1e-3):
    keys=["fossil_factor","nuclear_factor","wind_factor"]
    required=set(keys+["modeled_gap_mwh"])
    if not required.issubset(table):
        raise ValueError("Missing grid metrics")
    d=table.copy()
    if d.duplicated(keys).any():raise ValueError("Duplicate parameter combination")
    for name in keys+["modeled_gap_mwh"]:
        d[name]=pd.to_numeric(d[name],errors="coerce")
    if not np.isfinite(d[keys+["modeled_gap_mwh"]].to_numpy(float)).all() or (d.modeled_gap_mwh<-eps).any():
        raise ValueError("Nonfinite grid data or negative artificial gap")
    factors={name:sorted(d[name].unique().tolist()) for name in keys}
    if len(d)!=int(np.prod([len(x) for x in factors.values()])):
        raise ValueError("Incomplete decoupled grid")
    # Any additional source availability must never increase optimized gap.
    for key in keys:
        others=[x for x in keys if x!=key]
        for _,group in d.groupby(others):
            gap=group.sort_values(key).modeled_gap_mwh.to_numpy(float)
            if (np.diff(gap)>0.01).any():
                raise AssertionError("Monotonicity violated for "+key)
    boundary=[]
    for (n,w),frame in d.groupby(["nuclear_factor","wind_factor"]):
        valid=frame.loc[frame.modeled_gap_mwh<=eps,"fossil_factor"]
        boundary.append({
            "nuclear_factor":float(n),"wind_factor":float(w),
            "lowest_tested_fossil_factor_with_zero_gap":float(valid.min()) if len(valid) else None,
            "highest_tested_fossil_factor_still_with_gap":float(
                frame.loc[frame.modeled_gap_mwh>eps,"fossil_factor"].max()
            ) if (frame.modeled_gap_mwh>eps).any() else None,
            "zero_gap_observed_in_test_grid":bool(len(valid)),
            "critical_value_interpolated":False,
        })
    return pd.DataFrame(boundary),{
        "grid_scenarios":int(len(d)),
        "positive_artificial_gap_scenarios":int((d.modeled_gap_mwh>eps).sum()),
        "min_artificial_gap_mwh":float(d.modeled_gap_mwh.min()),
        "max_artificial_gap_mwh":float(d.modeled_gap_mwh.max()),
        "availability_monotonicity_verified":True,
        "climate_attribution_certified":False,
        "historical_calibration_certified":False,
    }


def run(boundary,roster,output,*,fossil=FOSSIL_FACTORS,nuclear=NUCLEAR_FACTORS,wind=WIND_FACTORS):
    factors=[validate_factors(v,n) for v,n in (
        (fossil,"fossil"),(nuclear,"nuclear"),(wind,"wind"))]
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    capacity,population=capacity_from_annual_roster(roster)
    demand=screened_load(boundary,"SRP")
    availability=matched_availability(demand,capacity)
    demand.to_csv(root/"hourly_boundary.csv",index=False)
    capacity.to_csv(root/"generator_class_nameplates.csv",index=False)
    entries=[]
    for f in factors[0]:
        for n in factors[1]:
            for w in factors[2]:
                scenario=f"fossil_{f:g}_nuclear_{n:g}_wind_{w:g}"
                target=root/"cases"/scenario
                target.mkdir(parents=True,exist_ok=True)
                a=availability.copy()
                a.loc[a.technology.isin(["gas","coal"]),"availability_pu"]*=f
                a.loc[a.technology.eq("nuclear"),"availability_pu"]*=n
                a.loc[a.technology.eq("wind"),"availability_pu"]*=w
                a.to_csv(target/"availability.csv",index=False)
                solved=dispatch(root/"hourly_boundary.csv",root/"generator_class_nameplates.csv",
                                target/"availability.csv",target)
                if len(solved)!=1 or solved.ba.iloc[0]!="SRP":
                    raise ValueError("Unexpected solver BA")
                entries.append({"fossil_factor":f,"nuclear_factor":n,
                                "wind_factor":w,
                                "modeled_gap_mwh":float(solved.unserved_energy_mwh.iloc[0]),
                                "scenario":scenario})
    table=pd.DataFrame(entries)
    bounds,metrics=summarize(table)
    table.to_csv(root/"decoupled_factorial_grid.csv",index=False)
    bounds.to_csv(root/"decoupled_threshold_brackets.csv",index=False)
    manifest={
        "official_capacity_roster":population,
        "default_assumed_technology_availability":BASE_PU,
        "fossil_factor_applies_to":["gas","coal"],
        "nuclear_factor_applies_to":["nuclear"],
        "wind_factor_applies_to":["wind"],
        "fossil_factors":factors[0],"nuclear_factors":factors[1],"wind_factors":factors[2],
        "eia930_generation_replayed":False,
        "source_independent_hourly_weather_used":False,
        "annual_nameplate_not_hourly_available_capacity":True,
        "isolated_ba_and_fixed_net_interchange":True,
        "simulated_gap_is_actual_unserved_electricity":False,
        **metrics,
    }
    (root/"decoupled_grid_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(table.to_string(index=False))
    return table,bounds,manifest


def main():
    p=argparse.ArgumentParser()
    for k in ("boundary","roster","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    run(pd.read_csv(a.boundary),
        pd.read_csv(a.roster,dtype={"plant_id":"string","generator_id":"string"}),
        a.output)


if __name__=="__main__":
    main()
