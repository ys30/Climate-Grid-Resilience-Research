"""SRP EIA-930 non-gas hourly replay + EIA-923 NG budget stress test.

SOURCE-CONDITIONED ACCOUNTING COUNTERFACTUAL, not independent historical
dispatch calibration: replaying observed non-gas generation makes these
scenarios unsuitable for climate-attributable outage or adequacy claims.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .eia930_fuel_decomposition import FUELS
from .srp_ng_plant_budget_pypsa import validate_inputs

REPLAY = ("Coal", "Nuclear", "Hydropower and Pumped Storage",
          "Solar", "Wind", "Other Fuel Sources")
NOT_ASSUMED_ZERO = ("All Petroleum Products", "Unknown Fuel Sources")


def prepare_fuel_replay(raw, hours, *, ba="SRP"):
    required={"Balancing Authority","UTC Time at End of Hour","Net Generation (MW)",
              "Net Generation (MW) from Natural Gas"}
    required.update("Net Generation (MW) from "+fuel for fuel in (*REPLAY,*NOT_ASSUMED_ZERO))
    if not required.issubset(raw):
        raise ValueError("Missing official EIA930 fuel fields")
    d=raw.loc[raw["Balancing Authority"].astype("string").str.strip().eq(ba)].copy()
    d["timestamp"]=pd.to_datetime(d["UTC Time at End of Hour"],utc=True,errors="raise")-pd.Timedelta(hours=1)
    if len(d)!=len(hours) or d.timestamp.duplicated().any() or not pd.DatetimeIndex(
        d.timestamp.sort_values()).equals(hours):
        raise ValueError("Incomplete EIA930 BA hourly generation coverage")
    d=d.set_index("timestamp").reindex(hours)
    included={}
    for fuel in ("Natural Gas",*REPLAY):
        col="Net Generation (MW) from "+fuel
        s=pd.to_numeric(d[col],errors="coerce")
        if not np.isfinite(s.to_numpy(float)).all():
            raise ValueError("Missing/nonfinite EIA930 required replay fuel: "+fuel)
        included[fuel]=s.astype(float)
    reported_total=pd.to_numeric(d["Net Generation (MW)"],errors="coerce")
    if not np.isfinite(reported_total.to_numpy(float)).all():
        raise ValueError("Missing/nonfinite EIA930 overall generation")
    excluded=[]
    for fuel in NOT_ASSUMED_ZERO:
        col="Net Generation (MW) from "+fuel
        raw_col=d[col].astype("string").str.strip()
        if raw_col.notna().any() and raw_col.ne("").any():
            raise ValueError("Unexpected EIA930 oil/unknown observations: audit source before exclusion")
        excluded.append({"fuel":fuel,"missing_hours":len(hours),"assumed_zero":False})
    detail=pd.DataFrame(included,index=hours)
    non_ng=detail[list(REPLAY)].sum(axis=1)
    diagnostics={
        "reported_eia930_total_generation_mwh":float(reported_total.sum()),
        "reported_eia930_natural_gas_mwh":float(detail["Natural Gas"].sum()),
        "replayed_eia930_non_gas_signed_mwh":float(non_ng.sum()),
        "eia930_reported_total_minus_named_fuels_mwh":
            float((reported_total-detail.sum(axis=1)).sum()),
        "missing_source_fuel_categories":excluded,
        "non_ng_replay_is_observed_generation_not_independent_resource_availability":True,
    }
    return detail,non_ng,diagnostics


def solve(boundary,raw,plant_envelope,*,year=2024,month=1,budget_scale=None):
    import pypsa
    b,plants,hours=validate_inputs(boundary,plant_envelope,year,month)
    detail,nongas,replay=prepare_fuel_replay(raw,hours)
    if budget_scale is not None and (not np.isfinite(budget_scale) or budget_scale<0):
        raise ValueError("Invalid budget scaling")
    imports=(-b.interchange_mw).clip(lower=0)
    exports=b.interchange_mw.clip(lower=0)
    nongas_in=nongas.clip(lower=0)
    nongas_abs=(-nongas).clip(lower=0)
    n=pypsa.Network();n.set_snapshots(hours.tz_localize(None));n.add("Bus","SRP")
    n.add("Load","observed_demand",bus="SRP",p_set=b.demand_mw.to_numpy())
    n.add("Load","observed_exports",bus="SRP",p_set=exports.to_numpy())
    n.add("Load","signed_negative_non_gas_replay",bus="SRP",p_set=nongas_abs.to_numpy())
    n.add("Generator","fixed_non_gas_replay",bus="SRP",p_nom=float(nongas_in.max())+1,
          p_set=nongas_in.to_numpy(),marginal_cost=0)
    n.add("Generator","fixed_observed_imports",bus="SRP",p_nom=float(imports.max())+1,
          p_set=imports.to_numpy(),marginal_cost=0)
    n.add("Generator","portfolio_gap",bus="SRP",p_nom=float(
        (b.demand_mw+exports+nongas_abs).max())+1,marginal_cost=100000.)
    n.add("Generator","surplus_disposal",bus="SRP",p_nom=float(
        (nongas_in+imports).max()+plants.candidate_nameplate_mw.sum())+1,
        p_min_pu=-1.,p_max_pu=0.,marginal_cost=-0.1)
    for r in plants.itertuples(index=False):
        extra={} if budget_scale is None else {"e_sum_max":float(budget_scale*r.page1_signed_ng_mwh)}
        n.add("Generator","NG_PLANT_"+str(r.plant_id),bus="SRP",
              p_nom=float(r.candidate_nameplate_mw),marginal_cost=40.,**extra)
    status,condition=n.optimize(solver_name="highs")
    if (status,condition)!=("ok","optimal"):
        raise RuntimeError(f"Solver failed: {status}/{condition}")
    gen=n.generators_t.p
    plantcols=["NG_PLANT_"+str(x) for x in plants.plant_id]
    ng=gen[plantcols].sum(axis=1)
    gap=gen.portfolio_gap
    disposal=-gen.surplus_disposal
    # PyPSA snapshots are timezone-naive; source EIA timestamps are UTC aware.
    # Use aligned hourly arrays, never add pandas Series across mixed datetime indexes.
    check=pd.Series(
        ng.to_numpy()+nongas_in.to_numpy()+imports.to_numpy()+gap.to_numpy()
        -b.demand_mw.to_numpy()-exports.to_numpy()
        -nongas_abs.to_numpy()-disposal.to_numpy(),
        index=n.snapshots,dtype=float)
    if not np.isfinite(check.to_numpy()).all():
        raise ValueError("Nonfinite hourly bus balance")
    if float(check.abs().max())>1e-3:
        raise ValueError("Hourly bus balance failed")
    for r in plants.itertuples(index=False):
        if budget_scale is not None and float(gen["NG_PLANT_"+str(r.plant_id)].sum())>float(
            budget_scale*r.page1_signed_ng_mwh)+1e-3:
            raise ValueError("Monthly plant gas budget exceeded")
    scenario="unlimited" if budget_scale is None else f"{budget_scale:g}x_page1"
    hourly=pd.DataFrame({
        "timestamp_utc":hours.astype(str),"observed_demand_mw":b.demand_mw.to_numpy(),
        "observed_export_mw":exports.to_numpy(),"observed_import_mw":imports.to_numpy(),
        "replayed_non_gas_net_mw":nongas.to_numpy(),"modeled_ng_mw":ng.to_numpy(),
        "artificial_portfolio_gap_mw":gap.to_numpy(),"disposal_mw":disposal.to_numpy(),
        "hourly_bus_residual_mw":check.to_numpy(),
    })
    row={
        "scenario":scenario,"hour_count":len(hours),
        "modeled_ng_generation_mwh":float(ng.sum()),
        "fixed_non_gas_replay_mwh":float(nongas.sum()),
        "artificial_portfolio_gap_mwh":float(gap.sum()),
        "modeled_disposal_mwh":float(disposal.sum()),
        "observed_import_mwh":float(imports.sum()),
        "observed_export_mwh":float(exports.sum()),
        "observed_demand_mwh":float(b.demand_mw.sum()),
        "max_hourly_bus_residual_mw":float(check.abs().max()),
        "ng_page1_monthly_budget_mwh":None if budget_scale is None else float(
            budget_scale*plants.page1_signed_ng_mwh.sum()),
        "eia930_natural_gas_reported_mwh":replay["reported_eia930_natural_gas_mwh"],
        "eia930_generation_total_reported_mwh":replay["reported_eia930_total_generation_mwh"],
        "other_technologies_availability_independently_modeled":False,
        "artificial_gap_is_observed_outage":False,
        "historical_calibration_certified":False,
    }
    return hourly,row,replay,detail


def compare(boundary,raw,plants,*,year=2024,month=1):
    results=[];hourly={};category=None;replay=None
    for scale in (None,1.,0.75):
        h,r,source,fuels=solve(boundary,raw,plants,year=year,month=month,budget_scale=scale)
        results.append(r);hourly[r["scenario"]]=h
        category=fuels;replay=source
    result=pd.DataFrame(results)
    gaps=result.set_index("scenario").artificial_portfolio_gap_mwh
    if not (gaps["unlimited"]<=gaps["1x_page1"]+1e-2<=gaps["0.75x_page1"]+2e-2):
        raise AssertionError("Tightening NG energy budget improved artificial gap")
    if not (result.max_hourly_bus_residual_mw<1e-3).all():
        raise AssertionError("Failed monthly comparison conservation")
    return result,hourly,category,replay


def main():
    p=argparse.ArgumentParser()
    for x in ("boundary","eia930","plants","output"):p.add_argument("--"+x,required=True)
    a=p.parse_args()
    boundary=pd.read_csv(a.boundary);raw=pd.read_csv(a.eia930,low_memory=False)
    plants=pd.read_csv(a.plants,dtype={"plant_id":"string"})
    result,hourly,category,replay=compare(boundary,raw,plants)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/"ng_budget_nongas_replay_comparison.csv",index=False)
    for key,data in hourly.items():
        data.to_csv(out/("ng_nongas_replay_"+key+"_hourly.csv"),index=False)
    category.to_csv(out/"eia930_replayed_fuel_hourly.csv",index_label="timestamp_utc")
    (out/"ng_nongas_replay_manifest.json").write_text(json.dumps({
        "source_diagnostics":replay,"scenario_rows":result.to_dict("records"),
        "observed_non_gas_replay_is_not_independent_validation":True,
        "model_is_not_full_physical_ba_dispatch":True,
        "historical_calibration_certified":False
    },indent=2)+"\n")
    print(result.to_string(index=False))


if __name__=="__main__":
    main()
