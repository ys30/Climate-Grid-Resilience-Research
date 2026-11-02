"""Observed EIA-930 exchange boundary: imports are must-take generator, exports are fixed load.

This is a source-scheduled external boundary, NOT a transmission flow simulation.
"""
import argparse,json,calendar,math
from pathlib import Path
import pandas as pd

def run(balance, capacity, ba, year, month):
    import pypsa
    b=balance.copy(); c=capacity.copy()
    for k in ("timestamp","demand_mw","interchange_mw"):
        if k not in b: raise ValueError("Missing "+k)
    b["timestamp"]=pd.to_datetime(b.timestamp,utc=True,errors="raise")
    for k in ("demand_mw","interchange_mw"):b[k]=pd.to_numeric(b[k],errors="raise")
    if b[["timestamp","demand_mw","interchange_mw"]].isna().any().any():raise ValueError("Missing boundary data")
    if not b[["demand_mw","interchange_mw"]].map(math.isfinite).all().all():raise ValueError("Nonfinite boundary data")
    expected=pd.date_range(f"{year}-{month:02d}-01",periods=calendar.monthrange(year,month)[1]*24,freq="h",tz="UTC")
    if len(b)!=len(expected) or b.timestamp.duplicated().any() or not pd.DatetimeIndex(b.timestamp.sort_values()).equals(expected):raise ValueError("Incomplete UTC month")
    b=b.set_index("timestamp").reindex(expected)
    if (b.demand_mw<0).any():raise ValueError("Negative demand")
    c=c[c.ba.eq(ba)].copy()
    if c.empty or c.technology.duplicated().any():raise ValueError("Missing or duplicate capacity")
    for k in ("capacity_mw","marginal_cost"):c[k]=pd.to_numeric(c[k],errors="raise")
    if c[["capacity_mw","marginal_cost"]].isna().any().any() or (c.capacity_mw<0).any():raise ValueError("Invalid capacity")
    if not c[["capacity_mw","marginal_cost"]].map(math.isfinite).all().all():raise ValueError("Nonfinite capacity or costs")
    imports=(-b.interchange_mw).clip(lower=0)
    exports=b.interchange_mw.clip(lower=0)
    n=pypsa.Network();n.set_snapshots(expected.tz_localize(None));n.add("Bus",ba)
    n.add("Load","local_demand",bus=ba,p_set=b.demand_mw.to_numpy())
    n.add("Load","observed_export",bus=ba,p_set=exports.to_numpy())
    for r in c.itertuples(index=False):
        n.add("Generator",f"local__{r.technology}",bus=ba,p_nom=float(r.capacity_mw),marginal_cost=float(r.marginal_cost))
    # Import generator has fixed, observed hourly dispatch and can be > local demand.
    # Spill sink is required to avoid infeasibility in that case.
    peak=float(imports.max())
    if peak>0:
        n.add("Generator","observed_import",bus=ba,p_nom=peak,p_min_pu=(imports/peak).to_numpy(),p_max_pu=(imports/peak).to_numpy(),marginal_cost=0)
    n.add("Generator","unserved",bus=ba,p_nom=float((b.demand_mw+exports).max())+1,marginal_cost=1e5)
    # Oversupply cannot exceed must-take imports since local generation is dispatchable.
    n.add("Generator","spill",bus=ba,p_nom=max(1.0,peak),p_min_pu=-1,p_max_pu=0,marginal_cost=-1)
    status,condition=n.optimize(solver_name="highs")
    if status!="ok" or condition!="optimal":
        raise RuntimeError(f"Nonoptimal exchange solve: {status}, {condition}")
    g=n.generators_t.p
    if g.empty:raise RuntimeError("No dispatch")
    if ((g["unserved"]>1e-6) & (g["spill"] < -1e-6)).any():
        raise RuntimeError("Unserved energy and deliberate spillage simultaneously in one hour")
    if (g["spill"]>1e-6).any() or (g["unserved"] < -1e-6).any():
        raise RuntimeError("Unexpected spillage or unserved dispatch direction")
    # Check the actual optimizer output hour by hour; monthly sums can hide cancellations.
    modeled_import=(g["observed_import"] if peak>0 else pd.Series(0.0,index=g.index))
    if (modeled_import.to_numpy()-imports.to_numpy()).__abs__().max()>1e-5:
        raise RuntimeError("Optimized import dispatch differs from fixed EIA-930 schedule")
    local_hourly=sum((g[f"local__{tech}"] for tech in c.technology),pd.Series(0.0,index=g.index))
    hourly_residual=(local_hourly.to_numpy()+modeled_import.to_numpy()
        +g["unserved"].to_numpy()+g["spill"].to_numpy()
        -b.demand_mw.to_numpy()-exports.to_numpy())
    max_hourly_residual=float(abs(hourly_residual).max())
    if max_hourly_residual>1e-4:
        raise RuntimeError(f"Hourly dispatch balance violated: {max_hourly_residual} MW")
    local=sum(float(g[f"local__{tech}"].sum()) for tech in c.technology)
    result={"solver_status":status,"solver_condition":condition,"local_generation_mwh":local,"scheduled_import_mwh":float(imports.sum()),
        "scheduled_export_mwh":float(exports.sum()),"local_demand_mwh":float(b.demand_mw.sum()),
        "unserved_mwh":float(g["unserved"].sum()),"spilled_mwh":-float(g["spill"].sum()),
        "net_interchange_mwh":float(b.interchange_mw.sum()),
        "hours_with_unserved":int((g["unserved"]>1e-6).sum()),
        "hours_with_spillage":int((g["spill"]< -1e-6).sum()),
        "max_absolute_hourly_balance_residual_mw":max_hourly_residual,
        "historical_calibration_certified":False,"real_network_interchange_simulated":False}
    residual=result["local_generation_mwh"]+result["scheduled_import_mwh"]+result["unserved_mwh"]-result["local_demand_mwh"]-result["scheduled_export_mwh"]-result["spilled_mwh"]
    result["energy_balance_residual_mwh"]=residual
    if abs(residual)>1e-3:raise RuntimeError("Dispatch energy not balanced")
    return result

def main():
    p=argparse.ArgumentParser()
    for k in ("balance","capacity","output"):p.add_argument("--"+k,required=True)
    p.add_argument("--ba",default="SRP");p.add_argument("--year",type=int,default=2024);p.add_argument("--month",type=int,default=1)
    a=p.parse_args()
    m=run(pd.read_csv(a.balance),pd.read_csv(a.capacity),a.ba,a.year,a.month)
    o=Path(a.output);o.mkdir(parents=True,exist_ok=True)
    (o/"explicit_import_export_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print(json.dumps(m,indent=2))
if __name__=="__main__":main()
