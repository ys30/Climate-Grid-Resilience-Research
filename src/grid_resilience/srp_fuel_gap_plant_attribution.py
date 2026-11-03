"""Trace EIA-923 Page1 NG/SUB plant contributions beside EIA-930 BA fuel totals.

Descriptive provenance diagnostic only. EIA-930 fuel-category generation
cannot be allocated to EIA-923 plants without a validated BA dispatch crosswalk.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd


def attribute(page1, eia930_fuels, *, ba="SRP", period="2024-01"):
    required={"plant_id","reported_ba","period","prime_mover","reported_fuel","net_generation_mwh"}
    if not required.issubset(page1):
        raise ValueError("Missing EIA-923 Page1 fields")
    needed={"eia930_fuel","reported_hours","blank_hours","signed_reported_mwh"}
    if not needed.issubset(eia930_fuels):
        raise ValueError("Missing EIA-930 category coverage fields")
    p=page1.copy()
    for key in ("plant_id","reported_ba","period","reported_fuel","prime_mover"):
        p[key]=p[key].astype("string").str.strip()
        if p[key].isna().any() or p[key].eq("").any():
            raise ValueError("Missing EIA-923 source identity")
    p["plant_id"]=p.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
    p=p.loc[p.reported_ba.eq(ba)&p.period.eq(period)].copy()
    if p.empty:
        raise ValueError("No requested EIA-923 BA-month records")
    p["net_generation_mwh"]=pd.to_numeric(p.net_generation_mwh,errors="coerce")
    if not np.isfinite(p.net_generation_mwh.to_numpy(dtype=float)).all():
        raise ValueError("Missing/nonfinite EIA-923 signed net generation")
    q=eia930_fuels.copy()
    if q.eia930_fuel.duplicated().any():
        raise ValueError("Duplicate EIA-930 fuel group")
    for col in ("reported_hours","blank_hours"):
        q[col]=pd.to_numeric(q[col],errors="raise")
        if not np.isfinite(q[col].to_numpy(dtype=float)).all() or (q[col]<0).any():
            raise ValueError("Invalid EIA-930 coverage")
    q["signed_reported_mwh"]=pd.to_numeric(q.signed_reported_mwh,errors="coerce")
    group_map={"NG":"Natural Gas","SUB":"Coal"}
    plant=p.loc[p.reported_fuel.isin(group_map)].groupby(
        ["reported_fuel","plant_id"],as_index=False).agg(
        page1_source_rows=("net_generation_mwh","size"),
        page1_signed_mwh=("net_generation_mwh","sum")
    )
    plant["candidate_eia930_heading"]=plant.reported_fuel.map(group_map)
    totals=p.groupby("reported_fuel").net_generation_mwh.sum()
    diagnostics=[]
    for fuel,heading in group_map.items():
        subset=q.loc[q.eia930_fuel.eq(heading)]
        if len(subset)!=1:
            raise ValueError("Missing or duplicate EIA-930 comparison heading "+heading)
        obs=subset.iloc[0]
        n=int(obs.reported_hours);missing=int(obs.blank_hours)
        eia930=float(obs.signed_reported_mwh) if pd.notna(obs.signed_reported_mwh) else None
        page1_mwh=float(totals.get(fuel,0.0))
        fully_reported=(n>0 and missing==0 and eia930 is not None)
        plants=plant.loc[plant.reported_fuel.eq(fuel)]
        diagnostics.append({
            "eia923_original_fuel_code":fuel,
            "eia930_heading_for_descriptive_comparison":heading,
            "eia923_page1_source_rows":int(p.reported_fuel.eq(fuel).sum()),
            "eia923_distinct_plants":int(plants.plant_id.nunique()),
            "eia923_page1_signed_mwh":page1_mwh,
            "eia930_nonblank_hours":n,
            "eia930_blank_hours":missing,
            "eia930_reported_mwh":eia930,
            "numeric_source_difference_mwh":page1_mwh-eia930 if fully_reported else None,
            "numerically_comparable_coverage":bool(fully_reported),
            "equivalent_plant_ba_fuel_scope_certified":False,
            "historical_calibration_certified":False,
        })
    if len(plant):
        den=plant.groupby("reported_fuel").page1_signed_mwh.transform("sum")
        plant["share_of_page1_signed_fuel_total"]=np.where(
            den.abs()>1e-12,plant.page1_signed_mwh/den,np.nan)
    summary={"ba":ba,"period":period,
             "source_rows":int(len(p)),
             "ng_distinct_plants":int(plant.loc[plant.reported_fuel.eq("NG"),"plant_id"].nunique()),
             "sub_distinct_plants":int(plant.loc[plant.reported_fuel.eq("SUB"),"plant_id"].nunique()),
             "cross_source_generation_difference_is_model_error":False,
             "eia930_plant_allocation_certified":False,
             "historical_calibration_certified":False,
             "caution":"EIA-923 source code and EIA-930 fuel heading are distinct reporting scopes; "
                       "fuel-code comparisons are diagnostic only."}
    return plant.sort_values(["reported_fuel","page1_signed_mwh"],ascending=[True,False]),pd.DataFrame(diagnostics),summary


def main():
    p=argparse.ArgumentParser()
    for name in ("page1","eia930-fuel-coverage","output"):
        p.add_argument("--"+name,required=True)
    p.add_argument("--ba",default="SRP");p.add_argument("--period",default="2024-01")
    a=p.parse_args()
    rows,diag,summary=attribute(
        pd.read_csv(a.page1,dtype={"plant_id":"string"}),
        pd.read_csv(a.eia930_fuel_coverage),
        ba=a.ba,period=a.period)
    target=Path(a.output);target.mkdir(parents=True,exist_ok=True)
    rows.to_csv(target/"page1_ng_sub_plant_attribution.csv",index=False)
    diag.to_csv(target/"ng_coal_cross_source_differences.csv",index=False)
    (target/"ng_coal_source_diagnostic_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
