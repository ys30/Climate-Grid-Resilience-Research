"""Summarize matched wind-source / hydro-constraint comparisons conservatively.

This is a descriptive sensitivity analysis, not a causal estimate.
The current design changes hydro power and energy jointly in some rows;
therefore it does NOT identify a two-factor interaction coefficient.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def analyze(input_csv,output):
    d=pd.read_csv(input_csv)
    required={"hydro_budget_fraction","hydro_power_fraction","era5","replay","era5_minus_replay_shortfall_mwh"}
    if not required.issubset(d) or len(d)<3:raise ValueError("Missing matched scenario data")
    if d.duplicated(["hydro_budget_fraction","hydro_power_fraction"]).any():raise ValueError("Duplicate assumptions")
    delta=d.era5-d.replay
    if (abs(delta-d.era5_minus_replay_shortfall_mwh)>1e-3).any():raise AssertionError("Pair difference mismatch")
    if (d[["era5","replay"]]<-0.1).any().any():raise ValueError("Negative unserved energy")
    same_power=d[d.hydro_power_fraction.eq(0.1)].sort_values("hydro_budget_fraction").copy()
    if len(same_power)<3:raise ValueError("Not enough fixed-power observations")
    if (same_power[["era5","replay"]].diff().iloc[1:]>0.1).any().any():
        raise AssertionError("Higher hydro energy budget unexpectedly raises shortage")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    same_power["difference_gwh"]=same_power.era5_minus_replay_shortfall_mwh/1000
    same_power.to_csv(out/"fixed_hydro_power_energy_budget_comparison.csv",index=False)
    result={
      "matched_scenarios":int(len(d)),
      "fixed_hydro_power_fraction":0.1,
      "fixed_power_energy_budget_levels":same_power.hydro_budget_fraction.tolist(),
      "fixed_power_delta_gwh":same_power.difference_gwh.tolist(),
      "all_scenarios_era5_minus_replay_delta_gwh":(delta/1000).tolist(),
      "largest_observed_difference_gwh":float(delta.max()/1000),
      "smallest_observed_difference_gwh":float(delta.min()/1000),
      "joint_power_and_energy_changes_confounded":True,
      "factorial_interaction_coefficient_estimable":False,
      "observed_outage_or_reliability_risk":False,
      "guidance":"Report fixed-10%-power subset as hydro-energy sensitivity. Joint 20%-30% power comparisons do not isolate hydro energy effects."}
    (out/"hydro_wind_interaction_interpretation.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(analyze(a.input,a.output),indent=2))
if __name__=="__main__":main()
