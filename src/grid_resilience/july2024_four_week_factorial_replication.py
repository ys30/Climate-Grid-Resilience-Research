"""Replicate original four-case PyPSA sensitivity in four distinct July weeks.

Identical annual EIA860 partial fleet, assumed heat/wind responses and
hypothetical links for all source-observed 168h windows. Compare isolated
and hypothetical 10%-peak intertie cases; never treat modeled unserved load
as historically observed outages or calibrated EENS.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from grid_resilience.research_run import run as run_factorial

BAS={"CISO","AZPS","BPAT","SRP"}
CASES=("baseline","heat_only","wind_only","heat_wind")


def summarize(results):
    required={"event_id","network_variant","scenario","ba",
              "unserved_energy_mwh","shortage_hours","peak_shortfall_mw"}
    if not required.issubset(results):
        raise ValueError("Missing factorial source solver outcome columns")
    f=results.copy()
    for k in ("unserved_energy_mwh","shortage_hours","peak_shortfall_mw"):
        f[k]=pd.to_numeric(f[k],errors="coerce")
    if not np.isfinite(f[["unserved_energy_mwh","shortage_hours","peak_shortfall_mw"]].to_numpy(float)).all():
        raise ValueError("Nonfinite solver output")
    if f.unserved_energy_mwh.lt(-1e-4).any():
        raise ValueError("Negative optimized shortage")
    if f.duplicated(["event_id","network_variant","scenario","ba"]).any():
        raise ValueError("Duplicate outcome index")
    events=set(f.event_id)
    variants=set(f.network_variant)
    if len(events)!=4 or variants!={"isolated","links_10pct"}:
        raise ValueError("Expected exactly four distinct July observed windows and two frozen link cases")
    if len(f)!=4*2*4*4:
        raise ValueError("Unexpected number of factorial × BA source solves")
    counts=f.groupby(["event_id","network_variant"]).agg(
        unique_scenarios=("scenario","nunique"),unique_bas=("ba","nunique"),records=("ba","size"))
    if not (counts.unique_scenarios.eq(4).all() and counts.unique_bas.eq(4).all() and counts.records.eq(16).all()):
        raise ValueError("A per-event factorial is incomplete")
    if set(f.scenario)!=set(CASES) or set(f.ba)!=BAS:
        raise ValueError("Scenario/BA membership invalid")
    rows=[]
    for (event,variant),g in f.groupby(["event_id","network_variant"],sort=True):
        p=g.pivot(index="ba",columns="scenario",values="unserved_energy_mwh")
        if p.isna().any().any():
            raise ValueError("Incomplete BA factorial")
        p["interaction"]=p["heat_wind"]-p["heat_only"]-p["wind_only"]+p["baseline"]
        for ba,r in p.iterrows():
            rows.append({"event_id":event,"network_variant":variant,"ba":ba,
                "baseline_shortage_mwh":float(r["baseline"]),
                "heat_only_shortage_mwh":float(r["heat_only"]),
                "wind_only_shortage_mwh":float(r["wind_only"]),
                "compound_shortage_mwh":float(r["heat_wind"]),
                "modeled_factorial_interaction_mwh":float(r["interaction"])})
        totals=p.sum()
        rows.append({"event_id":event,"network_variant":variant,"ba":"SYSTEM",
            "baseline_shortage_mwh":float(totals["baseline"]),
            "heat_only_shortage_mwh":float(totals["heat_only"]),
            "wind_only_shortage_mwh":float(totals["wind_only"]),
            "compound_shortage_mwh":float(totals["heat_wind"]),
            "modeled_factorial_interaction_mwh":float(totals["interaction"])})
    out=pd.DataFrame(rows)
    system=out.loc[out.ba.eq("SYSTEM")].copy()
    p=system.pivot(index="event_id",columns="network_variant",
                   values="modeled_factorial_interaction_mwh")
    contrast=p.assign(links_minus_isolated_interaction_mwh=
                      p["links_10pct"]-p["isolated"]).reset_index()
    return out,contrast


def evaluate(root,output):
    path=Path(root)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    c=path/"frozen_partial_eia860_capacity.csv"
    links={"isolated":path/"isolated_ba_links.csv",
           "links_10pct":path/"frozen_hypothetical_links.csv"}
    source_manifest=json.loads((path/"four_week_source_manifest.json").read_text())
    if source_manifest["nonoverlapping_168h_windows"]!=4 or source_manifest["source_distinct_hourly_timestamps"]!=672:
        raise ValueError("Actual 4-week source event gate not passed")
    all_rows=[]
    for week in range(1,5):
        folder=path/f"week_{week}"
        for variant,network in links.items():
            event=f"JULY2024_WEEK_{week}"
            label=f"fourba_partial_fleet_{variant}"
            dest=out/f"week_{week}"/variant
            manifest=run_factorial(
                folder/"demand.csv",folder/"weather.csv",
                c,network,dest,event,label,"hypothetical")
            if manifest["input_validation"]["hours"]!=168:
                raise ValueError("Wrong real source 168-hour event")
            solved=pd.read_csv(dest/"solved/factorial_dispatch.csv")
            if len(solved)!=16:
                raise ValueError("Missing factorial solver scenario or BA")
            solved["network_variant"]=variant
            all_rows.append(solved)
    joined=pd.concat(all_rows,ignore_index=True)
    result,contrast=summarize(joined)
    joined.to_csv(out/"july_four_week_four_scenario_ba_dispatch.csv",index=False)
    result.to_csv(out/"july_four_week_factorial_interaction_by_ba.csv",index=False)
    contrast.to_csv(out/"july_four_week_isolated_vs_links_interaction.csv",index=False)
    meta={
        "source_distinct_hours":672,"distinct_real_july_weeks":4,
        "four_ba_week_rows":4*168,"scenario_names":list(CASES),
        "network_variants":["isolated","links_10pct"],
        "same_partial_eia860_annual_capacity_all_events":True,
        "same_hypothetical_intertie_rating_all_events":True,
        "same_assumed_heat_load_wind_response_all_events":True,
        "scenario_solves":32,"scenario_ba_records":128,
        "real_historical_generator_availability_calibrated":False,
        "physical_intertie_ratings_verified":False,
        "source_wind_proxy_is_observed_generation":False,
        "modeled_shortage_is_observed_eens":False,
        "independent_year_or_season_replication":False,
        "intra_july_consecutive_weeks_independent_weather_events_assumed":False,
        "factorial_interaction_causes_real_outages":False
    }
    (out/"july_four_week_replication_scope.json").write_text(json.dumps(meta,indent=2)+"\n")
    print("SOURCE-OBSERVED FOUR-WEEK SYSTEM FACTORIAL CONTRASTS")
    print(contrast.to_string(index=False))
    return contrast,meta


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--prepared",required=True)
    parser.add_argument("--output",required=True)
    a=parser.parse_args()
    evaluate(a.prepared,a.output)


if __name__=="__main__":
    main()
