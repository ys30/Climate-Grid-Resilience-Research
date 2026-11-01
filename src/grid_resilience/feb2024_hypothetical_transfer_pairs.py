"""Paired hypothetical AZPS import transfer sensitivities, never observed MW ratings.

Compare exactly the same demand, fleet, uniform availability and costs with
isolated and explicitly assumed one-link transfer bounds.
"""
import argparse, json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve

def run(demand_csv, capacity_csv, base_availability_csv, output, levels=(0.7,0.4), link_mw=(0,250,500,1000)):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    base=pd.read_csv(base_availability_csv)
    required={"timestamp","ba","technology","availability_pu"}
    if not required.issubset(base):raise ValueError("Missing availability fields")
    if base.empty or not base.availability_pu.eq(1).all():
        raise ValueError("Reference requires 100% hypothetical availability")
    if len(set(levels))!=len(levels) or any(not 0<x<=1 for x in levels):raise ValueError("Invalid levels")
    if len(set(link_mw))!=len(link_mw) or any(x<0 for x in link_mw) or 0 not in link_mw:
        raise ValueError("Require unique nonnegative link scenarios including isolated 0 MW")
    rows=[]
    for fraction in levels:
        for cap in link_mw:
            label=f"avail_{round(fraction*100):02d}_transfer_{int(cap)}mw"
            folder=out/label;folder.mkdir(parents=True,exist_ok=True)
            avail=base.copy();avail["availability_pu"]=fraction
            avail.to_csv(folder/"assumed_availability.csv",index=False)
            links=None
            if cap:
                links=folder/"hypothetical_links.csv"
                pd.DataFrame([{"from_ba":"AZPS","to_ba":"SRP","capacity_mw":cap}]).to_csv(links,index=False)
            shortages=solve(demand_csv,capacity_csv,folder/"assumed_availability.csv",
                            folder/"solve",links_csv=links)
            for r in shortages.itertuples(index=False):
                rows.append({"scenario":label,"availability_fraction":fraction,
                             "hypothetical_link_capacity_mw":cap,"ba":r.ba,
                             "unserved_energy_mwh":float(r.unserved_energy_mwh)})
    result=pd.DataFrame(rows)
    controls=result[result.hypothetical_link_capacity_mw.eq(0)][
        ["ba","availability_fraction","unserved_energy_mwh"]].rename(
        columns={"unserved_energy_mwh":"isolated_unserved_energy_mwh"})
    result=result.merge(controls,on=["ba","availability_fraction"],how="left",validate="many_to_one")
    result["shortfall_reduction_vs_isolated_mwh"]=result.isolated_unserved_energy_mwh-result.unserved_energy_mwh
    result.sort_values(["availability_fraction","hypothetical_link_capacity_mw","ba"]).to_csv(
        out/"hypothetical_transfer_paired_shortfall.csv",index=False)
    manifest={"scenario_count":len(levels)*len(link_mw),"result_rows":len(result),
              "hypothetical_transfer_pair":"AZPS–SRP",
              "link_capacities_mw":list(link_mw),"availability_fractions":list(levels),
              "actual_line_ratings_verified":False,"historical_calibration_certified":False,
              "warning":"Single hypothetical lossless bidirectional transport Link. This does not represent observed bilateral topology, AC physics or physically verified transfer capacity."}
    (out/"hypothetical_transfer_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    for k in ("demand","capacity","availability","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    print(json.dumps(run(a.demand,a.capacity,a.availability,a.output),indent=2))
if __name__=="__main__":main()
