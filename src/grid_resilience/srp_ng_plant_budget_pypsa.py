"""Isolated SRP gas-plant portfolio with optional monthly NG energy ceilings.

Counterfactual SOURCE-SCOPE experiment only: Page1 NG plant MWh are NOT
an observed SRP-dispatch ceiling and may not match EIA930 BA fuel scope.
No other technologies are modeled; 'unserved' is an artificial portfolio
coverage gap, NOT actual shortage or historical EENS.
"""
import argparse
import calendar
import json
from pathlib import Path

import numpy as np
import pandas as pd


def validate_inputs(balance, plants, year=2024, month=1):
    needed={"timestamp","demand_mw","interchange_mw"}
    required={"plant_id","candidate_nameplate_mw","page1_signed_ng_mwh"}
    if not needed.issubset(balance) or not required.issubset(plants):
        raise ValueError("Missing balance or plant envelope fields")
    hours=calendar.monthrange(year,month)[1]*24
    timestamps=pd.date_range(f"{year}-{month:02d}-01",periods=hours,freq="h",tz="UTC")
    b=balance.copy()
    b["timestamp"]=pd.to_datetime(b.timestamp,utc=True,errors="raise")
    if len(b)!=hours or b.timestamp.duplicated().any() or not pd.DatetimeIndex(
        b.timestamp.sort_values()).equals(timestamps):
        raise ValueError("Missing/duplicate 744-hour UTC monthly boundary")
    b=b.set_index("timestamp").reindex(timestamps)
    for field in ("demand_mw","interchange_mw"):
        b[field]=pd.to_numeric(b[field],errors="coerce")
    if not np.isfinite(b[["demand_mw","interchange_mw"]].to_numpy(float)).all():
        raise ValueError("Nonfinite observed BA hourly values")
    if b.demand_mw.lt(0).any():raise ValueError("Negative observed demand")
    p=plants.copy()
    p["plant_id"]=p.plant_id.astype("string").str.strip().str.replace(
        r"^0+(?=[0-9])","",regex=True)
    if p.plant_id.isna().any() or p.plant_id.eq("").any() or p.plant_id.duplicated().any():
        raise ValueError("Missing/duplicate plant IDs")
    for field in ("candidate_nameplate_mw","page1_signed_ng_mwh"):
        p[field]=pd.to_numeric(p[field],errors="coerce")
    if not np.isfinite(p[["candidate_nameplate_mw","page1_signed_ng_mwh"]].to_numpy(float)).all():
        raise ValueError("Nonfinite source capacity or monthly generation")
    if p.candidate_nameplate_mw.le(0).any() or p.page1_signed_ng_mwh.lt(0).any():
        raise ValueError("Nonpositive plant capacity or negative NG energy")
    if (p.page1_signed_ng_mwh>p.candidate_nameplate_mw*hours+1e-5).any():
        raise ValueError("Page1 plant source energy exceeds candidate nameplate ceiling")
    return b,p.sort_values("plant_id").reset_index(drop=True),timestamps


def solve(balance, plants, *, year=2024,month=1,scale=1.0,unlimited=False):
    import pypsa
    if not np.isfinite(scale) or scale<0:
        raise ValueError("Invalid assumed budget scale")
    b,p,times=validate_inputs(balance,plants,year,month)
    network=pypsa.Network()
    network.set_snapshots(times.tz_localize(None))
    network.add("Bus","SRP")
    imports=(-b.interchange_mw).clip(lower=0)
    exports=b.interchange_mw.clip(lower=0)
    network.add("Load","domestic",bus="SRP",p_set=b.demand_mw.to_numpy())
    network.add("Load","observed_export_sink",bus="SRP",p_set=exports.to_numpy())
    network.add("Generator","observed_import_schedule",bus="SRP",
                p_nom=float(imports.max())+1,p_set=imports.to_numpy(),marginal_cost=0)
    network.add("Generator","portfolio_gap",bus="SRP",
                p_nom=float((b.demand_mw+exports).max())+1,marginal_cost=100000.0)
    network.add("Generator","import_surplus_spill",bus="SRP",
                p_nom=float(imports.max())+1,p_min_pu=-1,p_max_pu=0,marginal_cost=-0.1)
    for r in p.itertuples(index=False):
        kwargs={} if unlimited else {"e_sum_max":float(scale*r.page1_signed_ng_mwh)}
        network.add("Generator","NG_PLANT_"+str(r.plant_id),bus="SRP",
                    p_nom=float(r.candidate_nameplate_mw),
                    marginal_cost=40.0,**kwargs)
    status,condition=network.optimize(solver_name="highs")
    if condition!="optimal":raise RuntimeError(f"Optimization failed: {status}/{condition}")
    gen=network.generators_t.p
    rows=[]
    total=0.0
    for r in p.itertuples(index=False):
        name="NG_PLANT_"+str(r.plant_id)
        mwh=float(gen[name].sum())
        limit=float(scale*r.page1_signed_ng_mwh) if not unlimited else None
        if limit is not None and mwh>limit+1e-3:
            raise ValueError("Plant budget exceeded")
        rows.append({"plant_id":str(r.plant_id),"candidate_nameplate_mw":float(r.candidate_nameplate_mw),
                     "page1_ng_observed_mwh":float(r.page1_signed_ng_mwh),
                     "scenario_budget_mwh":limit,
                     "scenario_dispatched_ng_mwh":mwh,
                     "energy_ceiling_scenario":"unlimited_nameplate" if unlimited else f"{scale:g}x_page1"})
        total+=mwh
    gap=float(gen.portfolio_gap.sum())
    imported=float(gen.observed_import_schedule.sum())
    spill=float(-gen.import_surplus_spill.sum())
    hourly=gen[["NG_PLANT_"+str(x) for x in p.plant_id]].sum(axis=1)+gen.portfolio_gap+gen.observed_import_schedule+gen.import_surplus_spill-b.demand_mw.to_numpy()-exports.to_numpy()
    max_residual=float(hourly.abs().max())
    if max_residual>1e-3:raise ValueError("Hourly energy conservation failed")
    demand=float(b.demand_mw.sum())
    exported=float(exports.sum())
    if abs(total+gap+imported-spill-demand-exported)>0.01:
        raise ValueError("Monthly energy conservation failed")
    manifest={"year":year,"month":month,"hours":len(times),
              "scenario":"unlimited_nameplate" if unlimited else f"{scale:g}x_page1",
              "assumed_budget_scale":None if unlimited else float(scale),
              "portfolio_plants":len(p),
              "page1_ng_source_mwh":float(p.page1_signed_ng_mwh.sum()),
              "candidate_nameplate_mw":float(p.candidate_nameplate_mw.sum()),
              "scenario_gas_dispatch_mwh":total,
              "modeled_portfolio_gap_mwh":gap,
              "observed_import_injection_mwh":imported,
              "observed_export_sink_mwh":exported,
              "domestic_demand_mwh":demand,
              "modeled_import_surplus_disposal_mwh":spill,
              "max_hourly_bus_residual_mw":max_residual,
              "other_supply_technologies_included":False,
              "observed_monthly_mwh_is_assumed_energy_cap_not_verified_dispatch":True,
              "portfolio_gap_is_real_unserved_energy":False,
              "full_ba_generation_calibrated":False,
              "historical_calibration_certified":False}
    return pd.DataFrame(rows),manifest


def compare(balance,plants,year=2024,month=1,scales=(1.0,0.75)):
    names=set()
    results=[];details=[]
    for unlimited,scale in [(True,1.)]+[(False,float(x)) for x in scales]:
        k="unlimited" if unlimited else f"{scale:g}"
        if k in names:raise ValueError("Duplicate budget scenario")
        names.add(k)
        rows,m=solve(balance,plants,year=year,month=month,scale=scale,unlimited=unlimited)
        rows["scenario"]=m["scenario"]
        details.append(rows)
        results.append(m)
    return pd.concat(details,ignore_index=True),pd.DataFrame(results)


def main():
    a=argparse.ArgumentParser()
    for key in ("balance","plant-envelope","output"):
        a.add_argument("--"+key,required=True)
    a.add_argument("--year",type=int,default=2024)
    a.add_argument("--month",type=int,default=1)
    a.add_argument("--scales",type=float,nargs="+",default=[1.0,0.75])
    args=a.parse_args()
    detail,summary=compare(pd.read_csv(args.balance),pd.read_csv(args.plant_envelope),
                           year=args.year,month=args.month,scales=args.scales)
    target=Path(args.output);target.mkdir(parents=True,exist_ok=True)
    detail.to_csv(target/"ng_plant_budget_scenarios.csv",index=False)
    summary.to_csv(target/"ng_portfolio_budget_comparison.csv",index=False)
    (target/"ng_portfolio_budget_manifest.json").write_text(json.dumps({
        "comparison_scenarios":summary.to_dict("records"),
        "source_scope_consistent_with_eia930_fuel_generation":False,
        "historical_calibration_certified":False,
        "warning":"Isolated NG portfolio; model gap is NOT observed unserved demand. Page1 monthly energies are hypothetical constraints, not verified hourly SRP dispatch."
    },indent=2)+"\n")
    print(summary.to_string(index=False))


if __name__=="__main__":
    main()
