"""Bidirectional EIA-930 boundary screen, with fixed import injection and export sink.

No fabricated network topology: observed imports and exports are fixed schedules.
Excess imports are absorbed by an explicit spill sink, not silently clipped.
"""
import argparse,calendar,json
from pathlib import Path
import pandas as pd

def solve(balance,capacity,year,month,ba,resource_settings=None,hourly_output=None):
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
    # A dispatchable NEGATIVE generator absorbs surplus in the same hour.
    # The small positive cost of negative dispatch discourages unnecessary spill.
    n.add("Generator","boundary_spill",bus=ba,p_nom=float(imports.max())+1,
          p_min_pu=-1.0,p_max_pu=0.0,marginal_cost=-0.1)
    for r in c.itertuples(index=False):
        n.add("Generator",str(r.technology),bus=ba,p_nom=float(r.capacity_mw),
              marginal_cost=float(r.marginal_cost))
    resource_mapping=None
    if resource_settings is not None:
        from grid_resilience.hy_ps_pypsa_components import add_hy_ps
        resource_mapping=add_hy_ps(n,ba,resource_settings,prefix=ba)
    status,condition=n.optimize(solver_name="highs")
    if condition!="optimal":raise RuntimeError(f"Optimization failed: {status}/{condition}")
    generation=n.generators_t.p
    actual= float(generation[[str(x) for x in c.technology]].to_numpy().sum())
    short=float(generation.unserved.sum())
    imported=float(generation.observed_imports.sum())
    spill=float(-generation.boundary_spill.sum())
    # This is irreversible same-hour surplus absorption, not a storage device.
    hydro_mwh=0.0;ps_charge_mwh=0.0;ps_discharge_mwh=0.0
    if resource_mapping is not None:
        hydro_mwh=float(-n.links_t.p1[resource_mapping["hydro_link"]].sum())
        ps_charge_mwh=float(n.links_t.p0[resource_mapping["storage_charge_link"]].sum())
        ps_discharge_mwh=float(-n.links_t.p1[resource_mapping["storage_discharge_link"]].sum())
        assert hydro_mwh<=resource_mapping["energy_budget_mwh"]+1e-5
    # Check every hourly balance, not only monthly totals. Link bus1 sign is negative
    # for delivered power; charging is a positive withdrawal from the BA bus.
    hourly=generation[[str(x) for x in c.technology]].sum(axis=1)
    hourly=hourly+generation.observed_imports+generation.unserved+generation.boundary_spill
    if resource_mapping is not None:
        hourly=hourly-n.links_t.p1[resource_mapping["hydro_link"]]
        hourly=hourly-n.links_t.p1[resource_mapping["storage_discharge_link"]]
        hourly=hourly-n.links_t.p0[resource_mapping["storage_charge_link"]]
    hourly_residual=hourly-d.demand_mw.to_numpy()-exports.to_numpy()
    if hourly_output is not None:
        hourly_table=pd.DataFrame({
            "timestamp_utc":hours.astype(str),
            "demand_mw":d.demand_mw.to_numpy(),
            "observed_export_mw":exports.to_numpy(),
            "observed_import_mw":generation.observed_imports.to_numpy(),
            "screened_fleet_generation_mw":generation[[str(x) for x in c.technology]].sum(axis=1).to_numpy(),
            "modeled_unserved_mw":generation.unserved.to_numpy(),
            "boundary_spill_mw":(-generation.boundary_spill).to_numpy(),
            "hydro_dispatch_mw":(-n.links_t.p1[resource_mapping["hydro_link"]]).to_numpy() if resource_mapping else 0.0,
            "ps_charge_mw":n.links_t.p0[resource_mapping["storage_charge_link"]].to_numpy() if resource_mapping else 0.0,
            "ps_discharge_mw":(-n.links_t.p1[resource_mapping["storage_discharge_link"]]).to_numpy() if resource_mapping else 0.0,
            "bus_balance_residual_mw":hourly_residual.to_numpy()
        })
        path=Path(hourly_output);path.parent.mkdir(parents=True,exist_ok=True)
        hourly_table.to_csv(path,index=False)
    max_hourly_residual_mw=float(hourly_residual.abs().max())
    if max_hourly_residual_mw>1e-3:
        raise ValueError(f"Hourly SRP bus balance failed: max residual {max_hourly_residual_mw} MW")
    demand=float(d.demand_mw.sum());export=float(exports.sum())
    if abs(actual+imported+short+hydro_mwh+ps_discharge_mwh-demand-export-spill-ps_charge_mwh)>max(0.01,(demand+export)*1e-8):
        raise ValueError("Boundary energy conservation failed")
    return {"year":year,"month":month,"ba":ba,"demand_mwh":demand,
            "observed_import_injection_mwh":imported,"observed_export_sink_mwh":export,
            "modeled_plant_generation_mwh":actual,"modeled_unserved_mwh":short,
            "modeled_import_surplus_disposal_mwh":spill,
            "max_hourly_bus_residual_mw":max_hourly_residual_mw,
            "hydro_dispatch_mwh":hydro_mwh,"ps_charge_mwh":ps_charge_mwh,
            "ps_discharge_mwh":ps_discharge_mwh,"hy_ps_counterfactual_enabled":resource_mapping is not None,
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
