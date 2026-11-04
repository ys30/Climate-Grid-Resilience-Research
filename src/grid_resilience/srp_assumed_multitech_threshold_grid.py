"""Matched hypothetical thermal x wind resource-availability grid, SRP Jan 2024.

Uses the same official EIA-860 primary-fuel/prime-mover roster and observed
EIA-930 demand+net-interchange boundary as the four-case synthetic experiment.
No EIA-930 fuel generation replay, ERA5, observed outage, or calibrated
technology availability is used. Gap is artificial modeled coverage only.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .multi_technology_dispatch import solve as dispatch
from .srp_net_exchange_pypsa_screen import screened_load
from .srp_assumed_multitech_factorial import (
    BASE_PU,capacity_from_annual_roster,matched_availability
)

THERMAL_TECH = frozenset({"gas","coal","nuclear"})
DEFAULT_THERMAL = (0.0,0.25,0.5,1.0)
DEFAULT_WIND = (0.0,0.5,0.75,1.0)


def validate_grid(thermal,wind):
    t=np.asarray(thermal,dtype=float)
    w=np.asarray(wind,dtype=float)
    for v,label in ((t,"thermal"),(w,"wind")):
        if v.ndim!=1 or v.size<2 or not np.isfinite(v).all():
            raise ValueError(f"Invalid {label} factors")
        if (v<0).any() or (v>1).any() or len(np.unique(v))!=v.size:
            raise ValueError(f"Factors for {label} must be distinct and within [0,1]")
    return sorted(t.tolist()),sorted(w.tolist())


def analyze_grid(rows,*,threshold_mwh=1e-3):
    if threshold_mwh<0 or not np.isfinite(threshold_mwh):
        raise ValueError("Invalid gap threshold")
    required={"thermal_factor","wind_factor","modeled_gap_mwh"}
    if not required.issubset(rows):
        raise ValueError("Missing grid columns")
    d=rows.copy()
    if d.duplicated(["thermal_factor","wind_factor"]).any():
        raise ValueError("Duplicate grid factor pair")
    if not np.isfinite(d[list(required)].to_numpy(float)).all() or (
        d.modeled_gap_mwh < -1e-4).any():
        raise ValueError("Invalid grid values")
    thermal=sorted(d.thermal_factor.unique())
    wind=sorted(d.wind_factor.unique())
    if len(d)!=len(thermal)*len(wind):
        raise ValueError("Incomplete factorial grid")
    mat=d.pivot(index="thermal_factor",columns="wind_factor",values="modeled_gap_mwh")
    # Adding thermal or wind availability cannot worsen an optimized shortage.
    if (np.diff(mat.to_numpy(),axis=0)>0.01).any() or (
        np.diff(mat.to_numpy(),axis=1)>0.01).any():
        raise AssertionError("Supply-availability monotonicity violated")
    boundary=[]
    for w in wind:
        values=mat[w]
        zero=values[values<=threshold_mwh]
        boundary.append({
            "wind_factor":float(w),
            "smallest_tested_thermal_factor_with_no_gap":(
                float(zero.index.min()) if len(zero) else None),
            "all_tested_thermal_factors_show_gap":len(zero)==0,
            "max_gap_mwh_at_tested_lowest_thermal":float(values.iloc[0]),
        })
    interactions=[]
    for t0,t1 in zip(thermal[:-1],thermal[1:]):
        for w0,w1 in zip(wind[:-1],wind[1:]):
            d2=float(mat.loc[t0,w0]-mat.loc[t1,w0]-
                     mat.loc[t0,w1]+mat.loc[t1,w1])
            interactions.append({"lower_thermal_factor":float(t0),
                                 "upper_thermal_factor":float(t1),
                                 "lower_wind_factor":float(w0),
                                 "upper_wind_factor":float(w1),
                                 "discrete_interaction_mwh":d2})
    return pd.DataFrame(boundary),pd.DataFrame(interactions),{
        "grid_points":int(len(d)),
        "positive_gap_grid_points":int((d.modeled_gap_mwh>threshold_mwh).sum()),
        "maximum_artificial_gap_mwh":float(d.modeled_gap_mwh.max()),
        "minimum_artificial_gap_mwh":float(d.modeled_gap_mwh.min()),
        "grid_only_no_interpolation":True,
        "real_world_outage_claim":False,
        "historical_calibration_certified":False
    }


def run(boundary,roster,out,*,thermal=DEFAULT_THERMAL,wind=DEFAULT_WIND):
    thermal,wind=validate_grid(thermal,wind)
    root=Path(out);root.mkdir(parents=True,exist_ok=True)
    capacity,population=capacity_from_annual_roster(roster)
    load=screened_load(boundary,"SRP")
    availability=matched_availability(load,capacity)
    load.to_csv(root/"source_boundary.csv",index=False)
    capacity.to_csv(root/"nonoverlapping_technology_nameplates.csv",index=False)
    rows=[]
    for t in thermal:
        for w in wind:
            key=f"thermal_{t:g}_wind_{w:g}"
            case=root/"cases"/key
            case.mkdir(parents=True,exist_ok=True)
            a=availability.copy()
            a.loc[a.technology.isin(THERMAL_TECH),"availability_pu"]*=t
            a.loc[a.technology.eq("wind"),"availability_pu"]*=w
            a.to_csv(case/"availability.csv",index=False)
            result=dispatch(root/"source_boundary.csv",
                            root/"nonoverlapping_technology_nameplates.csv",
                            case/"availability.csv",case)
            if len(result)!=1 or result.ba.iloc[0]!="SRP":
                raise ValueError("Unexpected dispatch result")
            rows.append({"thermal_factor":t,"wind_factor":w,
                         "modeled_gap_mwh":float(result.unserved_energy_mwh.iloc[0]),
                         "scenario_key":key})
    table=pd.DataFrame(rows)
    threshold,interactions,metrics=analyze_grid(table)
    table.to_csv(root/"thermal_wind_threshold_grid.csv",index=False)
    threshold.to_csv(root/"thermal_no_gap_grid_boundary.csv",index=False)
    interactions.to_csv(root/"thermal_wind_discrete_interactions.csv",index=False)
    manifest={
        "source_population":population,
        "assumed_base_availability":BASE_PU,
        "thermal_technologies_modified":sorted(THERMAL_TECH),
        "thermal_factors":thermal,"wind_factors":wind,
        "comparison_design":"EIA860 primary fuel/prime mover nameplate; EIA930 demand+net interchange; synthetic availability only",
        "uses_observed_generation_as_availability":False,
        "uses_independent_meteorology_as_availability":False,
        "includes_storage_or_physical_transfer_network":False,
        "climate_attribution_certified":False,
        **metrics}
    (root/"threshold_grid_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(table.to_string(index=False))
    return table,threshold,interactions,manifest


def main():
    a=argparse.ArgumentParser()
    for key in ("boundary","roster","output"):a.add_argument("--"+key,required=True)
    a.add_argument("--thermal-factors",type=float,nargs="+",default=DEFAULT_THERMAL)
    a.add_argument("--wind-factors",type=float,nargs="+",default=DEFAULT_WIND)
    args=a.parse_args()
    run(pd.read_csv(args.boundary),
        pd.read_csv(args.roster,dtype={"plant_id":"string","generator_id":"string"}),
        args.output,thermal=args.thermal_factors,wind=args.wind_factors)


if __name__=="__main__":
    main()
