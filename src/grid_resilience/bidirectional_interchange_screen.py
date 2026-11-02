"""Bidirectional EIA-930 boundary screen, with fixed import injection and export sink.

No fabricated network topology: observed imports and exports are fixed schedules.
Excess imports are absorbed by an explicit spill sink, not silently clipped.
"""
import argparse,calendar,json
from pathlib import Path
import pandas as pd

def solve(balance,capacity,year,month,ba):
    import pypsa
    needed={"timestamp","demand_mw","interchange_mw"}
    if not needed.issubset(balance) or not {"ba","technology","capacity_mw","marginal_cost"}.issubset(capacity):
        raise ValueError("Missing source fields")
    d=balance.copy();c=capacity.copy()
    d["timestamp"]=pd.to_datetime(d.timestamp,utc=True,errors="raise")
    for col in ("demand_mw","interchange_mw"):d[col]=pd.to_numeric(d[col],errors="raise")
    for col in ("capacity_mw","marginal_cost"):c[col]=pd.to_numeric(c[col],errors="raise")
    hours=pd.date_range(f"{year}-{month:02d}-01",periods=calendar.monthrange(year,month)[1]*24,freq="h",tz="UTC")
    if d.duplicated("timestamp").any() or len(d)!=len(hours) or not pd.DatetimeIndex(d.timestamp.sort_values()).equals(hours):
        raise ValueError("Incomplete/duplicate UTC month")
    if d[["demand_mw","interchange_mw"]].isna().any().any() or c.isna().any().any():
        raise ValueError("Missing numeric inputs")
    if (d.demand_mw<0).any() or (c.capacity_mw<0).any():raise ValueError("Negative demand/capacity")
    if set(c.ba)!={ba} or c.duplicated(["ba","technology"]).any():raise ValueError("BA/technology coverage mismatch")
    d=d.set_index("timestamp").reindex(hours)
    imports=(-d.interchange_mw).clip(lower=0)
    exports=d.interchange_mw.clip(lower=0)
    n=pypsa.Network();n.set_snapshots(hours.tz_localize(None));n.add("Bus",ba)
    n.add("Load","domestic",bus=ba,p_set=d.demand_mw.to_numpy())
    n.add("Load","observed_exports",bus=ba,p_set=exports.to_numpy())
    n.add("Generator","observed_imports",bus=ba,p_nom=float(imports.max())+1,p_set=imports.to_numpy(),marginal_cost=0)
    # Import surplus is an explicit, costly disposal option (not a real historical flow).
    n.add("Generator","unserved",bus=ba,p_nom=float((d.demand_mw+exports).max())+1,
          marginal_cost=100000.0)
    n.add("Load","import_surplus_disposal",bus=ba,p_set=0.0)
    # Represent spill as a dispatchable store, able to absorb energy at 0.1 cost.
    n.add("Store","boundary_spill",bus=ba,e_nom=float(imports.sum())+1,e_initial=0,
          e_cyclic=False,marginal_cost=0.1)
    for r in c.itertuples(index=False):
        n.add("Generator",str(r.technology),bus=ba,p_nom=float(r.capacity_mw),
              marginal_cost=float(r.marginal_cost))
    status,condition=n.optimize(solver_name="highs")
    if condition!="optimal":raise RuntimeError(f"Optimization failed: {status}/{condition}")
    generation=n.generators_t.p
    actual= float(generation[[str(x) for x in c.technology]].to_numpy().sum())
    short=float(generation.unserved.sum())
    imported=float(generation.observed_imports.sum())
    spill=float((-n.stores_t.p["boundary_spill"]).clip(lower=0).sum())
    # Stores charging is positive consumption when stores_t.p is negative.
    demand=float(d.demand_mw.sum());export=float(exports.sum())
    if abs(actual+imported+short-demand-export-spill)>max(0.01,(demand+export)*1e-8):
        raise ValueError("Boundary energy conservation failed")
    return {"year":year,"month":month,"ba":ba,"demand_mwh":demand,
            "observed_import_injection_mwh":imported,"observed_export_sink_mwh":export,
            "modeled_plant_generation_mwh":actual,"modeled_unserved_mwh":short,
            "modeled_import_surplus_disposal_mwh":spill,
            "historical_calibration_certified":False,
            "boundary_import_export_fixed":True,
            "notes":"Single-bus fixed observed interchange, incomplete fleet, hypothetical capacities, spill is not historical curtailment."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--balance",required=True);p.add_argument("--capacity",required=True)
    p.add_argument("--year",type=int,required=True);p.add_argument("--month",type=int,required=True)
    p.add_argument("--ba",default="SRP");p.add_argument("--output",required=True)
    a=p.parse_args()
    result=solve(pd.read_csv(a.balance),pd.read_csv(a.capacity),a.year,a.month,a.ba)
    dest=Path(a.output);dest.mkdir(parents=True,exist_ok=True)
    (dest/"bidirectional_boundary_screen.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
