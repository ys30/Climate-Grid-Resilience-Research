"""Explicit counterfactual fuel-dependent dispatch assumptions, NOT empirical costs.

Refuses unknown fuel codes. Energy-limited solar/wind/hydro/storage should not
be represented as firm constant availability in a historical adequacy model.
"""
import argparse,json
from pathlib import Path
import pandas as pd

ASSUMPTIONS={
 "NG":(55.0,0.85),"BIT":(85.0,0.80),"SUB":(80.0,0.80),
 "NUC":(20.0,0.90),"DFO":(150.0,0.70),"RFO":(130.0,0.70),
 "WAT":(12.0,0.40),"SUN":(0.0,0.20),"WND":(0.0,0.30),
 "GEO":(25.0,0.90),"LFG":(35.0,0.70),"OBG":(40.0,0.70),
 "BLQ":(45.0,0.70),"WDS":(45.0,0.70),"PUR":(60.0,0.60)}
def scenario(capacity):
    needed={"ba","technology","capacity_mw"}
    if not needed.issubset(capacity):raise ValueError("Missing capacities")
    d=capacity.copy()
    if d.empty or d.duplicated(["ba","technology"]).any():raise ValueError("Empty or duplicate inputs")
    d["capacity_mw"]=pd.to_numeric(d.capacity_mw,errors="raise")
    if not d.capacity_mw.gt(0).all():raise ValueError("Nonpositive capacity")
    unknown=set(d.technology)-set(ASSUMPTIONS)
    if unknown:raise ValueError(f"Unreviewed fuel codes: {sorted(unknown)}")
    d["assumed_marginal_cost"]=d.technology.map(lambda k:ASSUMPTIONS[k][0])
    d["assumed_capacity_factor"]=d.technology.map(lambda k:ASSUMPTIONS[k][1])
    d["original_nameplate_mw"]=d.capacity_mw
    d["capacity_mw"]=d.original_nameplate_mw*d.assumed_capacity_factor
    d["marginal_cost"]=d.assumed_marginal_cost
    d["hypothetical_assumptions"]=True
    return d
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--capacity",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    d=scenario(pd.read_csv(a.capacity))
    d.to_csv(out/"fuel_assumption_capacity_screen.csv",index=False)
    (out/"fuel_assumption_manifest.json").write_text(json.dumps({
        "historical_calibration_certified":False,"capacity_complete":False,
        "model_limits":"Counterfactual constant capacity multipliers and illustrative marginal costs, NOT actual hourly renewable profiles, fuel prices or outages.",
        "assumption_mapping":ASSUMPTIONS},indent=2)+"\n")
if __name__=="__main__":main()
