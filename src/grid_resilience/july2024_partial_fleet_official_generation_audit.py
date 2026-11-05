"""July 2024 four-BA partial-fleet supply coverage versus observed EIA930 net generation.

A structural falsification diagnostic, not generator capacity/availability
calibration. Compare contemporaneous EIA930 net-generation BA reports with
EIA860 *modeled partial* gas+wind nameplate capacities. BA reported net
generation need not map to the partial roster or any one owned generator.
No physical load shedding or EENS is inferred.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
START=pd.Timestamp("2024-07-01T00:00:00Z")
END=START+pd.Timedelta(hours=672)


def audit(demand,capacity,eia930,solved):
    required_d={"timestamp","ba","demand_mw"}
    required_c={"ba","gas_mw","wind_mw","source_year","capacity_source"}
    required_e={"Balancing Authority","UTC Time at End of Hour","Net Generation (MW)","Demand (MW)"}
    required_s={"event_id","network_variant","scenario","ba","unserved_energy_mwh"}
    for name,frame,cols in (("demand",demand,required_d),("capacity",capacity,required_c),
                            ("official_eia930",eia930,required_e),("solved",solved,required_s)):
        if not cols.issubset(frame):
            raise ValueError(f"Missing original {name} evidence columns: {cols-set(frame.columns)}")
    d,c,e,s=demand.copy(),capacity.copy(),eia930.copy(),solved.copy()
    d["timestamp"]=pd.to_datetime(d.timestamp,utc=True,errors="raise")
    d["demand_mw"]=pd.to_numeric(d.demand_mw,errors="coerce")
    if set(d.ba)!=set(BAS) or len(d)!=672*4 or d.duplicated(["timestamp","ba"]).any():
        raise ValueError("Expected exactly 672 four BA observed demand source hours")
    expected=pd.date_range(START,periods=672,freq="h")
    for _,g in d.groupby("ba"):
        if not pd.DatetimeIndex(g.timestamp.sort_values()).equals(expected):
            raise ValueError("Incomplete original modeled 28-day UTC source demand grid")
    for field in ("gas_mw","wind_mw"):
        c[field]=pd.to_numeric(c[field],errors="coerce")
    if len(c)!=4 or c.ba.duplicated().any() or set(c.ba)!=set(BAS):
        raise ValueError("Four BA partial fleet identity changed")
    if not c.capacity_source.astype(str).str.contains("GENERIC_THERMAL_PROXY").all():
        raise ValueError("This study only admits the audited original partial-fleet proxy")
    if not np.isfinite(c[["gas_mw","wind_mw"]].to_numpy(float)).all() or c[["gas_mw","wind_mw"]].lt(0).any().any():
        raise ValueError("Invalid original proxy capacity")
    c["partial_gas_wind_nameplate_mw"]=c.gas_mw+c.wind_mw
    if c.partial_gas_wind_nameplate_mw.le(0).any():
        raise ValueError("Nonpositive illustrative partial available nameplate")
    e=e.loc[e["Balancing Authority"].astype("string").str.strip().isin(BAS)].copy()
    e["timestamp"]=pd.to_datetime(e["UTC Time at End of Hour"],
       format="%m/%d/%Y %I:%M:%S %p",utc=True,errors="raise")-pd.Timedelta(hours=1)
    e["ba"]=e["Balancing Authority"].astype("string").str.strip()
    e=e.loc[e.timestamp.ge(START)&e.timestamp.lt(END)]
    if len(e)!=len(d) or e.duplicated(["timestamp","ba"]).any():
        raise ValueError("Incomplete original observed EIA930 BA net generation source")
    e["reported_net_generation_mw"]=pd.to_numeric(e["Net Generation (MW)"],errors="coerce")
    e["official_demand_mw"]=pd.to_numeric(e["Demand (MW)"],errors="coerce")
    if not np.isfinite(e[["reported_net_generation_mw","official_demand_mw"]].to_numpy(float)).all():
        raise ValueError("Missing official EIA930 net generation or demand")
    x=d.merge(e[["timestamp","ba","reported_net_generation_mw","official_demand_mw"]],
              on=["timestamp","ba"],how="left",validate="one_to_one",indicator=True)
    if not x._merge.eq("both").all():
        raise ValueError("Missing original BA official net-gen hour key")
    if not np.allclose(x.demand_mw,x.official_demand_mw,rtol=0,atol=1e-8):
        raise ValueError("Model original demand differs from same-hour official EIA930 demand")
    x=x.drop(columns=["_merge"]).merge(
        c[["ba","gas_mw","wind_mw","partial_gas_wind_nameplate_mw"]],
        on="ba",how="inner",validate="many_to_one")
    x["week"]=((x.timestamp-START)//pd.Timedelta(hours=168)).astype(int)+1
    x["reported_gen_exceeds_proxy_capacity_mw"]=(x.reported_net_generation_mw-
                                                  x.partial_gas_wind_nameplate_mw).clip(lower=0)
    x["baseline_isolated_supply_shortfall_lower_bound_mw"]=(x.demand_mw-
        x.partial_gas_wind_nameplate_mw).clip(lower=0)
    rows=[]
    for (week,ba),g in x.groupby(["week","ba"],sort=True):
        rows.append({
            "week":int(week),"ba":ba,"hours":len(g),
            "official_reported_net_generation_mwh":float(g.reported_net_generation_mw.sum()),
            "demand_mwh":float(g.demand_mw.sum()),
            "partial_gas_nameplate_mw":float(g.gas_mw.iloc[0]),
            "partial_wind_nameplate_mw":float(g.wind_mw.iloc[0]),
            "total_partial_gas_wind_nameplate_mw":float(g.partial_gas_wind_nameplate_mw.iloc[0]),
            "hours_reported_ba_net_gen_above_partial_nameplate":int(
                g.reported_gen_exceeds_proxy_capacity_mw.gt(1e-8).sum()),
            "sum_positive_reported_net_gen_minus_proxy_mwh":float(
                g.reported_gen_exceeds_proxy_capacity_mw.sum()),
            "max_reported_net_gen_minus_proxy_mw":float(
                g.reported_gen_exceeds_proxy_capacity_mw.max()),
            "hours_observed_demand_above_partial_nameplate":int(
                g.baseline_isolated_supply_shortfall_lower_bound_mw.gt(1e-8).sum()),
            "isolated_partial_nameplate_deficit_lower_bound_mwh":float(
                g.baseline_isolated_supply_shortfall_lower_bound_mw.sum())
        })
    out=pd.DataFrame(rows)
    if len(out)!=16 or not out.hours.eq(168).all():
        raise ValueError("Expected exactly four weeks × four BA")
    s=s.loc[s.scenario.eq("baseline")&s.network_variant.eq("isolated")].copy()
    s["week"]=pd.to_numeric(s.event_id.astype(str).str.extract(r"WEEK_(\d+)")[0],errors="coerce")
    s["unserved_energy_mwh"]=pd.to_numeric(s.unserved_energy_mwh,errors="coerce")
    if len(s)!=16 or s.duplicated(["week","ba"]).any() or not np.isfinite(s.unserved_energy_mwh).all():
        raise ValueError("Missing original isolated PyPSA baseline scenario evidence")
    out=out.merge(s[["week","ba","unserved_energy_mwh"]],on=["week","ba"],how="left",validate="one_to_one")
    out=out.rename(columns={"unserved_energy_mwh":"isolated_baseline_modeled_shortage_mwh"})
    if out.isolated_baseline_modeled_shortage_mwh.isna().any():
        raise ValueError("Incomplete matched source solver baseline")
    # With no links and no gas ramp limits, gas+wind output cannot exceed
    # gas+wind nameplate, so this is a deterministic mathematical lower
    # bound, NOT a counterfactual historical outage lower bound.
    difference=out.isolated_baseline_modeled_shortage_mwh-out.isolated_partial_nameplate_deficit_lower_bound_mwh
    if difference.lt(-.05).any():
        raise ValueError("Modeled PyPSA baseline violates obvious partial-nameplate deficit bound")
    out["modeled_shortage_above_partial_nameplate_bound_mwh"]=difference
    meta={
        "source_archived_pypsa_run":42104106361,
        "original_official_eia930_run":41325415594,
        "source_distinct_hours":672,"source_week_count":4,"source_bas":list(BAS),
        "official_utc_hour_ending_minus_one_hour":True,
        "eia930_official_and_model_demand_exact_match":True,
        "capacity_is_2024_eia860_partial_gas_and_wind_proxy_only":True,
        "observed_eia930_ba_net_gen_vs_nameplate_are_not_same_generator_cohort":True,
        "reported_ba_net_gen_above_partial_capacity_does_not_identify_missing_fleet":True,
        "partial_nameplate_deficit_is_lower_bound_on_model_shortage_not_actual_outage":True,
        "fuel_specific_missing_net_capacity_estimated":False,
        "storage_soc_or_real_intertie_constraints_verified":False,
        "historical_real_eens_or_forced_outages_estimated":False
    }
    return out,meta


def main():
    p=argparse.ArgumentParser()
    for key in ("demand","capacity","official-eia930","solved","output"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    x,m=audit(pd.read_csv(a.demand),pd.read_csv(a.capacity),
        pd.read_csv(a.official_eia930,dtype="string"),pd.read_csv(a.solved))
    root=Path(a.output);root.mkdir(parents=True,exist_ok=True)
    x.to_csv(root/"july2024_fourweek_ba_partial_supply_vs_official_netgen.csv",index=False)
    (root/"july2024_fourweek_partial_fleet_coverage_manifest.json").write_text(
        json.dumps(m,indent=2)+"\n")
    print("OFFICIAL REPORTED NET GENERATION AND PARTIAL MODEL SUPPLY COVERAGE")
    print(x.to_string(index=False))


if __name__=="__main__":
    main()
