"""Audit continuous 672h hydro counterfactual against original four-week PyPSA.

Ensure hydro-free 672h run reproduces all 64 independently solved
July isolated source BA/week/scenario baseline records. Aggregate
modelled shortage reductions and hydro dispatch separately; neither is
measured avoided outage energy.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

def summarize(solved,hydro_dispatch,original):
    needed={"resource_scenario","scenario","week","ba","modeled_unserved_mwh"}
    if not needed.issubset(solved):
        raise ValueError("Missing new PyPSA 672h outcome")
    orig={"event_id","network_variant","scenario","ba","unserved_energy_mwh"}
    if not orig.issubset(original):
        raise ValueError("Missing prior corrected-hour source scenarios")
    expected=original.loc[original.network_variant.eq("isolated")].copy()
    expected["week"]=pd.to_numeric(expected.event_id.str.extract(r"WEEK_(\d+)")[0],
                                   errors="coerce")
    control=solved.loc[solved.resource_scenario.eq("HY_0MW_0MWh")].copy()
    keys=["week","ba","scenario"]
    if len(expected)!=64 or len(control)!=64 or expected.duplicated(keys).any() or control.duplicated(keys).any():
        raise ValueError("Missing full four-week by BA/scenario original controls")
    check=control.merge(expected,on=keys,how="inner",validate="one_to_one")
    if len(check)!=64:
        raise ValueError("Corrected baseline scenario key mismatch")
    dif=(check.modeled_unserved_mwh-check.unserved_energy_mwh).abs()
    if dif.gt(.05).any():
        raise ValueError(f"New 672h no-hydro controls mismatch original isolated week solver: {dif.max()}")
    check["absolute_replay_error_mwh"]=dif
    expected_labels={"HY_0MW_0MWh","HY_500MW_598947MWh",
                     "HY_2000MW_598947MWh","HY_2000MW_1497369MWh"}
    if (set(solved.resource_scenario)!=expected_labels or
        len(solved)!=256 or solved.duplicated(["resource_scenario"]+keys).any()):
        raise ValueError("Incomplete hydro intervention × scenario × week × BA")
    required_dispatch={"resource_scenario","scenario","week",
                       "hydro_dispatched_mwh","hydro_peak_dispatch_mw"}
    if not required_dispatch.issubset(hydro_dispatch) or len(hydro_dispatch)!=64:
        raise ValueError("Incomplete hydro energy accounting")
    if hydro_dispatch.duplicated(["resource_scenario","scenario","week"]).any():
        raise ValueError("Duplicate hydro week discharge records")
    comparison=solved.groupby(["resource_scenario","scenario"],as_index=False).agg(
        modelled_system_shortage_mwh=("modeled_unserved_mwh","sum"))
    base=comparison.loc[comparison.resource_scenario.eq("HY_0MW_0MWh"),
                        ["scenario","modelled_system_shortage_mwh"]].rename(
        columns={"modelled_system_shortage_mwh":"original_hydro_free_shortage_mwh"})
    comparison=comparison.merge(base,on="scenario",validate="many_to_one")
    comparison["simulated_shortage_reduction_mwh"]=(comparison.original_hydro_free_shortage_mwh-
                                                   comparison.modelled_system_shortage_mwh)
    if comparison.simulated_shortage_reduction_mwh.lt(-.1).any():
        raise ValueError("Additional free dispatchable hydro raised optimized source shortage")
    dh=hydro_dispatch.groupby(["resource_scenario","scenario"],as_index=False).agg(
        optimally_dispatched_hypothetical_hy_mwh=("hydro_dispatched_mwh","sum"))
    comparison=comparison.merge(dh,on=["resource_scenario","scenario"],validate="one_to_one")
    comparison["hydro_dispatch_minus_shortage_reduction_mwh"]=(
        comparison.optimally_dispatched_hypothetical_hy_mwh-
        comparison.simulated_shortage_reduction_mwh)
    if comparison.hydro_dispatch_minus_shortage_reduction_mwh.lt(-.1).any():
        raise ValueError("Modeled shortage reduction exceeds hydro dispatched energy")
    by_factor=[]
    for label,g in comparison.groupby("resource_scenario"):
        s=g.set_index("scenario").modelled_system_shortage_mwh
        by_factor.append({"resource_scenario":label,
                "four_case_compound_interaction_mwh":float(
                    s["heat_wind"]-s["heat_only"]-s["wind_only"]+s["baseline"]),
                "baseline_system_shortage_mwh":float(s["baseline"]),
                "baseline_hypothetical_hydro_dispatched_mwh":float(
                    g.loc[g.scenario.eq("baseline"),"optimally_dispatched_hypothetical_hy_mwh"].iloc[0]),
                "baseline_shortage_reduction_mwh":float(
                    g.loc[g.scenario.eq("baseline"),"simulated_shortage_reduction_mwh"].iloc[0])})
    result=pd.DataFrame(by_factor)
    manifest={"original_source_run":42104106361,
        "contiguous_intertemporal_solver_run":42122153716,
        "exact_hydro_free_baseline_ba_week_scenario_comparisons":64,
        "max_absolute_hydro_free_control_replay_error_mwh":float(dif.max()),
        "full_28day_energy_budget_applied_once":True,
        "reported_hydro_generation_equals_shortage_reduction":False,
        "intervention_is_expressly_assumed_not_historical":True,
        "observed_historical_outages_or_eens":False,
        "observed_hy_hourly_operation_reconstructed":False,
        "pumped_storage_soc_solved_in_this_run":False}
    return comparison,result,check,manifest


def main():
    p=argparse.ArgumentParser()
    for x in ("new-factorial","hydro-dispatch","original-factorial","output"):
        p.add_argument("--"+x,required=True)
    a=p.parse_args()
    x,y,z,m=summarize(pd.read_csv(a.new_factorial),
        pd.read_csv(a.hydro_dispatch),pd.read_csv(a.original_factorial))
    root=Path(a.output);root.mkdir(parents=True,exist_ok=True)
    x.to_csv(root/"hydro_intertemporal_all_16_aggregated_shortage_vs_hy.csv",index=False)
    y.to_csv(root/"hydro_intertemporal_factorial_interaction_by_scenario.csv",index=False)
    z.to_csv(root/"hydro_free_original_fourweek_64_row_exact_replay.csv",index=False)
    (root/"hydro_672h_reproducibility_and_interaction_manifest.json").write_text(
        json.dumps(m,indent=2)+"\n")
    print("HY 672H SYSTEM INTERACTIONS AND BASELINE MITIGATION")
    print(y.to_string(index=False))
    print("HY SYSTEM MODEL SOURCE AND SHORTFALL-AVOIDANCE")
    print(x.to_string(index=False))
    print("REPLAY MANIFEST",json.dumps(m,indent=2))

if __name__=="__main__":
    main()
