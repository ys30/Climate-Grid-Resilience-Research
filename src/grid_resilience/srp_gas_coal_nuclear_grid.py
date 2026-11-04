"""SRP January 2024 gas/coal/nuclear separation with wind endpoints.

EIA860 nameplates and EIA930 demand/interchange; ALL availability factors are
assumed. No historical generation replay, weather attribution, observed EENS,
or proven BA dispatch rights. Each PyPSA run spans the same 744 UTC hours.
"""
import argparse
import json
from pathlib import Path
from itertools import product

import numpy as np
import pandas as pd

from .multi_technology_dispatch import solve as dispatch
from .srp_net_exchange_pypsa_screen import screened_load
from .srp_assumed_multitech_factorial import (
    BASE_PU, capacity_from_annual_roster, matched_availability
)
from .srp_fossil_nuclear_decoupled_grid import validate_factors

DEFAULT_GAS=(0.5,0.625,0.75)
DEFAULT_COAL=(0.5,0.75,1.)
DEFAULT_NUCLEAR=(0.75,1.)
DEFAULT_WIND=(0.,1.)
DIMENSIONS=("gas_factor","coal_factor","nuclear_factor","wind_factor")


def summarize(df,eps=0.001):
    if not set((*DIMENSIONS,"modeled_gap_mwh")).issubset(df):
        raise ValueError("Missing grid fields")
    d=df.copy()
    if d.duplicated(list(DIMENSIONS)).any():
        raise ValueError("Duplicate grid combination")
    fields=[*DIMENSIONS,"modeled_gap_mwh"]
    for key in fields:
        d[key]=pd.to_numeric(d[key],errors="coerce")
    if not np.isfinite(d[fields].to_numpy(float)).all() or d.modeled_gap_mwh.lt(-eps).any():
        raise ValueError("Invalid grid numeric values")
    factors={k:sorted(d[k].unique()) for k in DIMENSIONS}
    if len(d)!=np.prod([len(v) for v in factors.values()]):
        raise ValueError("Incomplete scenario combinations")
    for name in DIMENSIONS:
        other=[k for k in DIMENSIONS if k!=name]
        for _,group in d.groupby(other):
            gaps=group.sort_values(name).modeled_gap_mwh.to_numpy(float)
            if (np.diff(gaps)>0.01).any():
                raise AssertionError("Availability monotonicity violation: "+name)
    boundaries=[]
    for (coal,nuclear,wind),group in d.groupby(
            ["coal_factor","nuclear_factor","wind_factor"]):
        no_gap=group.loc[group.modeled_gap_mwh.le(eps),"gas_factor"]
        gap=group.loc[group.modeled_gap_mwh.gt(eps),"gas_factor"]
        boundaries.append({
            "coal_factor":float(coal),"nuclear_factor":float(nuclear),
            "wind_factor":float(wind),
            "highest_tested_gas_factor_with_gap":float(gap.max()) if len(gap) else None,
            "lowest_tested_gas_factor_with_no_gap":float(no_gap.min()) if len(no_gap) else None,
            "continuous_transition_estimated":False,
        })
    return pd.DataFrame(boundaries),{
        "scenario_count":int(len(d)),
        "positive_artificial_gap_scenarios":int(d.modeled_gap_mwh.gt(eps).sum()),
        "maximum_artificial_gap_mwh":float(d.modeled_gap_mwh.max()),
        "monotonicity_verified":True,
        "historical_calibration_certified":False,
    }


def run(balance,roster,out,*,gas=DEFAULT_GAS,coal=DEFAULT_COAL,
        nuclear=DEFAULT_NUCLEAR,wind=DEFAULT_WIND):
    factors=[validate_factors(v,k) for k,v in zip(
        DIMENSIONS,(gas,coal,nuclear,wind))]
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    capacity,population=capacity_from_annual_roster(roster)
    load=screened_load(balance,"SRP")
    availability=matched_availability(load,capacity)
    load.to_csv(out/"boundary.csv",index=False)
    capacity.to_csv(out/"technology_nameplates.csv",index=False)
    scenarios=[]
    for g,c,n,w in product(*factors):
        label=f"gas_{g:g}_coal_{c:g}_nuclear_{n:g}_wind_{w:g}"
        sub=out/"scenarios"/label
        sub.mkdir(parents=True,exist_ok=True)
        a=availability.copy()
        for technology,value in (("gas",g),("coal",c),("nuclear",n),("wind",w)):
            a.loc[a.technology.eq(technology),"availability_pu"]*=value
        a.to_csv(sub/"availability.csv",index=False)
        result=dispatch(out/"boundary.csv",out/"technology_nameplates.csv",
                        sub/"availability.csv",sub)
        if len(result)!=1 or str(result.ba.iloc[0])!="SRP":
            raise ValueError("Unexpected PyPSA BA output")
        scenarios.append(dict(zip(DIMENSIONS,(g,c,n,w)))|{
            "modeled_gap_mwh":float(result.unserved_energy_mwh.iloc[0]),
            "scenario":label})
    d=pd.DataFrame(scenarios)
    bounds,metrics=summarize(d)
    d.to_csv(out/"gas_coal_nuclear_wind_grid.csv",index=False)
    bounds.to_csv(out/"conditional_gas_threshold_brackets.csv",index=False)
    manifest={
        **metrics,"model_population":population,
        "grid_factors":{k:v for k,v in zip(DIMENSIONS,factors)},
        "base_assumed_capacity_factors":BASE_PU,
        "historical_eia930_generation_replayed":False,
        "independent_weather_source_included":False,
        "storage_or_verified_transmission_modeled":False,
        "artificial_gap_is_observed_eens":False,
        "independent_hourly_plant_availability_verified":False,
        "note":"Single BA, no real outage calibration. Nuclear, gas, coal and wind factors are artificial multipliers of assumed technology availability."}
    (out/"gas_coal_grid_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(d.to_string(index=False))
    return d,bounds,manifest


def main():
    parser=argparse.ArgumentParser()
    for name in ("boundary","roster","output"):
        parser.add_argument("--"+name,required=True)
    args=parser.parse_args()
    run(pd.read_csv(args.boundary),
        pd.read_csv(args.roster,dtype={"plant_id":"string","generator_id":"string"}),
        args.output)


if __name__=="__main__":
    main()
