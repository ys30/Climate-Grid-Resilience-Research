"""Original-source July 2024 capacity-coverage stress sensitivity.

Increment a *synthetic* perfectly available generic thermal proxy in each BA
by 0/25/50% of its JULY WEEK-ONE observed BA peak demand. Original source
EIA-930/ERA5 input hours, originally frozen links and climate stress factors
are held fixed; this is NOT additional observed EIA860 capacity or a real
grid adequacy estimate. All four non-overlapping July weeks are included to close the predeclared E2
capacity-sensitivity scope. Adjacent weeks are not independent extreme events.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from grid_resilience.research_run import run as run_factorial
from grid_resilience.july2024_four_week_factorial_replication import CASES, BAS

FRACTIONS=(0.0,0.25,0.50)
WEEKS=(1,2,3,4)
VARIANTS=("isolated","links_10pct")
TARGET_BAS=tuple(sorted(BAS))


def capacity_grid(original,week1_demand):
    required={"ba","gas_mw","wind_mw","source_year","capacity_source"}
    if not required.issubset(original) or original.ba.duplicated().any() or set(original.ba)!=BAS:
        raise ValueError("Frozen source capacity identity incomplete")
    if not original.capacity_source.astype(str).str.contains("GENERIC_THERMAL_PROXY").all():
        raise ValueError("Original source partial-fleet gate invalid")
    d=week1_demand.copy()
    if not {"timestamp","ba","demand_mw"}.issubset(d) or len(d)!=4*168:
        raise ValueError("Original observed Week 1 BA demand incomplete")
    d["timestamp"]=pd.to_datetime(d.timestamp,utc=True,errors="raise")
    if d.duplicated(["ba","timestamp"]).any() or set(d.ba)!=BAS:
        raise ValueError("Duplicated original BA/UTC hour")
    for ba,part in d.groupby("ba"):
        if len(part)!=168 or part.timestamp.nunique()!=168:
            raise ValueError(f"Original 168h source incomplete {ba}")
    p=d.assign(demand_mw=pd.to_numeric(d.demand_mw,errors="raise")).groupby("ba").demand_mw.max()
    if not np.isfinite(p.values).all() or (p<=0).any():
        raise ValueError("Invalid source peak")
    c=original.copy()
    c["gas_mw"]=pd.to_numeric(c.gas_mw,errors="raise")
    c["wind_mw"]=pd.to_numeric(c.wind_mw,errors="raise")
    if not np.isfinite(c[["gas_mw","wind_mw"]].values).all() or (c[["gas_mw","wind_mw"]]<0).any().any():
        raise ValueError("Invalid source capacity")
    outputs={}
    for f in FRACTIONS:
        x=c.copy()
        x["additional_hypothetical_firm_mw"]=x.ba.map(p)*f
        x["gas_mw"]=x.gas_mw + x.additional_hypothetical_firm_mw
        outputs[f]=x
    return outputs


def summarize(records):
    f=records.copy()
    needed={"fraction","week","network_variant","scenario","ba","unserved_energy_mwh"}
    if not needed.issubset(f):
        raise ValueError("Missing source capacity stress solver fields")
    expected={(frac,week,network,case,ba) for frac in FRACTIONS for week in WEEKS
              for network in VARIANTS for case in CASES for ba in TARGET_BAS}
    key=["fraction","week","network_variant","scenario","ba"]
    if f.duplicated(key).any() or set(map(tuple,f[key].itertuples(index=False,name=None))) != expected:
        raise ValueError("Scenario coverage not exact 3x4x2x4x4")
    f["unserved_energy_mwh"]=pd.to_numeric(f.unserved_energy_mwh,errors="raise")
    if not np.isfinite(f.unserved_energy_mwh).all() or (f.unserved_energy_mwh < -1e-5).any():
        raise ValueError("Nonfinite or invalid model shortage")
    rows=[]
    for (frac,week,network),g in f.groupby(["fraction","week","network_variant"],sort=True):
        x=g.pivot(index="ba",columns="scenario",values="unserved_energy_mwh")
        if set(x.index)!=BAS or set(x.columns)!=set(CASES):
            raise ValueError("Incomplete matched climate factorial")
        for ba in (*TARGET_BAS,"SYSTEM"):
            v=x.loc[ba] if ba!="SYSTEM" else x.sum(axis=0)
            interaction=float(v["heat_wind"]-v["heat_only"]-v["wind_only"]+v["baseline"])
            rows.append(dict(
                added_capacity_fraction_of_week1_ba_peak=frac,
                week=week,network_variant=network,ba=ba,
                baseline_modeled_gap_mwh=float(v["baseline"]),
                heat_only_modeled_gap_mwh=float(v["heat_only"]),
                wind_only_modeled_gap_mwh=float(v["wind_only"]),
                compound_modeled_gap_mwh=float(v["heat_wind"]),
                modeled_heat_wind_second_difference_mwh=interaction
            ))
    summary=pd.DataFrame(rows)
    if len(summary)!=3*4*2*5:
        raise ValueError("Wrong detailed stress result count")
    return summary


def validate_original_no_change(summary, original, tolerance=0.001):
    x=summary.loc[summary.added_capacity_fraction_of_week1_ba_peak.eq(0)].copy()
    needed={"event_id","network_variant","ba","baseline_shortage_mwh",
            "modeled_factorial_interaction_mwh"}
    if not needed.issubset(original):
        raise ValueError("Original archived source summary missing")
    o=original.loc[original.event_id.isin([f"JULY2024_WEEK_{w}" for w in WEEKS])].copy()
    if len(o)!=4*2*5:
        raise ValueError("Original archived BA/SYSTEM source keys incomplete")
    o["week"]=o.event_id.str.extract(r"WEEK_(\d+)").astype(int)
    compare=x.merge(o,on=["week","network_variant","ba"],how="outer",indicator=True,validate="one_to_one")
    if not compare._merge.eq("both").all() or len(compare)!=40:
        raise ValueError("Original zero-add capacity model keys do not match")
    for current,old in [("baseline_modeled_gap_mwh","baseline_shortage_mwh"),
                        ("modeled_heat_wind_second_difference_mwh","modeled_factorial_interaction_mwh")]:
        if (compare[current]-compare[old]).abs().max()>tolerance:
            raise ValueError(f"ORIGINAL MODEL REPRODUCTION GATE FAILED {current}")
    return float(max((compare["baseline_modeled_gap_mwh"]-compare["baseline_shortage_mwh"]).abs().max(),
                     (compare["modeled_heat_wind_second_difference_mwh"]-
                      compare["modeled_factorial_interaction_mwh"]).abs().max()))


def main():
    p=argparse.ArgumentParser()
    for v in ("prepared","original-ba","output"):
        p.add_argument("--"+v,required=True)
    args=p.parse_args()
    root=Path(args.prepared);out=Path(args.output)
    out.mkdir(parents=True,exist_ok=True)
    scope=json.loads((root/"four_week_source_manifest.json").read_text())
    if scope.get("nonoverlapping_168h_windows")!=4 or scope.get("physical_eens_or_historical_outages_estimated") is not False:
        raise ValueError("Original source cohort scope admission failed")
    grid=capacity_grid(pd.read_csv(root/"frozen_partial_eia860_capacity.csv"),
                       pd.read_csv(root/"week_1/demand.csv"))
    link_files={"isolated":root/"isolated_ba_links.csv",
                "links_10pct":root/"frozen_hypothetical_links.csv"}
    records=[]
    for fraction,c in grid.items():
        cap=out/f"capacity_plus_{int(fraction*100)}pct.csv"
        c.to_csv(cap,index=False)
        for week in WEEKS:
            folder=root/f"week_{week}"
            for variant,link in link_files.items():
                dest=out/"solver"/f"plus_{int(fraction*100)}pct"/f"week_{week}"/variant
                manifest=run_factorial(folder/"demand.csv",folder/"weather.csv",cap,
                                      link,dest,f"JULY2024_WEEK_{week}",
                                      variant,"hypothetical")
                if manifest["input_validation"]["hours"]!=168:
                    raise ValueError("Source 168h boundary failed")
                v=pd.read_csv(dest/"solved/factorial_dispatch.csv")
                v["fraction"]=fraction;v["week"]=week;v["network_variant"]=variant
                records.append(v)
    all_rows=pd.concat(records,ignore_index=True)
    result=summarize(all_rows)
    difference=validate_original_no_change(result,pd.read_csv(args.original_ba))
    result.to_csv(out/"paperc_2024_capacity_coverage_model_interactions.csv",index=False)
    result.loc[result.ba.eq("SYSTEM")].to_csv(
        out/"paperc_2024_capacity_coverage_system_interactions.csv",index=False)
    manifest=dict(
        added_capacity_type="perfectly_firm_hypothetical_generic_thermal_proxy_only",
        fractions_of_first_week_observed_BA_peak=list(FRACTIONS),
        selected_weeks=list(WEEKS),network_variants=list(VARIANTS),
        climate_scenario_names=list(CASES),
        original_no_addition_matches_archive_within_mwh=0.001,
        maximum_original_anchor_difference_mwh=difference,
        scenario_optimizations=96,ba_solver_records=384,
        local_ba_plus_system_summaries=120,
        source_2024_partial_fleet_not_complete=True,
        additional_firm_capacity_observed_or_eia860_verified=False,
        physical_network_ratings_calibrated=False,
        actual_eens_or_blackouts_estimated=False,
        selected_weeks_are_not_independent_weather_events=True
    )
    (out/"paperc_2024_capacity_coverage_scope.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(result.loc[result.ba.eq("SYSTEM")].to_string(index=False))
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
