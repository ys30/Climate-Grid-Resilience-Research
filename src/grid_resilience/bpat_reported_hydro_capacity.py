"""Restore reported non-storage BPAT hydro nameplate in exploratory dispatch.

EIA-860 Plant-attributed hydro category is from single-fuel operable
generators with storage and pumped technology excluded by upstream filter.
Hourly deliverability remains wholly assumed, NOT a historical claim.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve

def compare(demand,capacity,availability,full_capacity,output):
    c=pd.read_csv(capacity);a=pd.read_csv(availability);full=pd.read_csv(full_capacity)
    required={"ba","technology","nameplate_capacity_mw"}
    if not required.issubset(full):raise ValueError("Missing EIA-860 capacity fields")
    hydro=full.loc[(full.ba=="BPAT")&(full.technology=="hydro")]
    if len(hydro)!=1:raise ValueError("Expected exactly one BPAT nonstorage hydro capacity category")
    mw=float(hydro.iloc[0].nameplate_capacity_mw)
    if not 0<mw<float("inf"):raise ValueError("Invalid BPAT hydro capacity")
    if ((c.ba=="BPAT")&(c.technology=="hydro")).any():raise ValueError("Already has BPAT hydro")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for case,extra in [("baseline_without_hydro",0),("reported_eia860_hydro_assumed_firm",mw)]:
        folder=out/case;folder.mkdir(exist_ok=True)
        cc=c.copy();aa=a.copy()
        if extra>0:
            cc=pd.concat([cc,pd.DataFrame([{"ba":"BPAT","technology":"hydro",
                                           "capacity_mw":extra,"marginal_cost":0}])],ignore_index=True)
            times=a.timestamp.drop_duplicates()
            aa=pd.concat([aa,pd.DataFrame({"timestamp":times,"ba":"BPAT","technology":"hydro",
                       "availability_pu":1.0})],ignore_index=True)
        cc.to_csv(folder/"capacity.csv",index=False)
        aa.to_csv(folder/"availability.csv",index=False)
        solved=solve(demand,folder/"capacity.csv",folder/"availability.csv",folder/"dispatch")
        for r in solved.itertuples(index=False):
            rows.append({"case":case,"ba":r.ba,"added_reported_hydro_nameplate_mw":extra,
                         "shortfall_mwh":r.unserved_energy_mwh})
    pd.DataFrame(rows).to_csv(out/"reported_hydro_capacity_experiment.csv",index=False)
    meta={"bp_attributed_eia860_nonstorage_single_fuel_hydro_nameplate_mw":mw,
          "source":"EIA-860 2024 Plant BA and Generator Operable nameplate",
          "hydro_assumed_firm_at_all_696_hours":True,
          "pumped_storage_excluded":True,"historical_generation_calibrated":False,
          "hydrological_monthly_energy_limits_applied":False,
          "warning":"Nameplate is not feasible 2024-02 hourly hydro output; scenario is upper-bound-style diagnostic with assumed full availability."}
    (out/"reported_hydro_capacity_experiment_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    return meta
def main():
    p=argparse.ArgumentParser()
    for field in ("demand","capacity","availability","full-capacity","output"):
        p.add_argument("--"+field,required=True)
    a=p.parse_args()
    print(json.dumps(compare(a.demand,a.capacity,a.availability,a.full_capacity,a.output),indent=2))
if __name__=="__main__":main()
