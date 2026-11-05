"""Real July 2024 BPAT HY/PS reporting-scope bridge: official EIA923 vs EIA930.

Official Page1 HY and PS plant-month NET MWh are checked separately.
EIA930 hourly mixed hydro+pumped BA group uses hour-ending UTC labels.
Those reporting scopes do not certify identical physical plant boundaries;
a residual is a source comparability diagnostic, NOT lost hydro generation.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

HOURS=pd.date_range("2024-07-01T00:00:00Z",periods=744,freq="h",tz="UTC")
HYFIELD="Net Generation (MW) from Hydropower and Pumped Storage"

def audit(eia923,eia930,partial_capacity):
    required_923={"reported_ba","prime_mover","period","net_generation_mwh",
                  "plant_month_rows","coverage_status"}
    required_930={"Balancing Authority","UTC Time at End of Hour",
                  "Net Generation (MW)"}
    required_cap={"ba","gas_mw","wind_mw","capacity_source"}
    for name,x,needed in [("EIA923",eia923,required_923),
                          ("EIA930",eia930,required_930),
                          ("partial_model",partial_capacity,required_cap)]:
        if not needed.issubset(x):
            raise ValueError(f"Missing original {name} source columns {needed-set(x.columns)}")
    p=eia923.loc[
        eia923.reported_ba.astype("string").str.strip().eq("BPAT")&
        eia923.period.astype("string").str.strip().eq("2024-07")&
        eia923.prime_mover.astype("string").str.strip().isin(["HY","PS"])].copy()
    if len(p)!=2 or p.prime_mover.duplicated().any() or not set(p.prime_mover)=={"HY","PS"}:
        raise ValueError("Missing or duplicate BPAT Page1 July HY and PS source rows")
    if not p.coverage_status.eq("observed_source_rows").all():
        raise ValueError("A missing EIA923 BA/technology/month slot cannot be treated as zero")
    for field in ("net_generation_mwh","plant_month_rows"):
        p[field]=pd.to_numeric(p[field],errors="coerce")
    if not np.isfinite(p[["net_generation_mwh","plant_month_rows"]].to_numpy(float)).all() or p.plant_month_rows.le(0).any():
        raise ValueError("Missing or invalid EIA923 measured plant-month observations")
    b=eia930.loc[eia930["Balancing Authority"].astype("string").str.strip().eq("BPAT")].copy()
    b["timestamp"]=pd.to_datetime(b["UTC Time at End of Hour"],
        format="%m/%d/%Y %I:%M:%S %p",utc=True,errors="raise")-pd.Timedelta(hours=1)
    b=b.loc[b.timestamp.ge(HOURS[0])&b.timestamp.le(HOURS[-1])].copy()
    if b.timestamp.duplicated().any() or not pd.DatetimeIndex(b.timestamp.sort_values()).equals(HOURS):
        raise ValueError("Official EIA930 BPAT July UTC hour-start grid incomplete")
    # EIA930 BALANCE source may expose total BA generation without the
    # separate fuel-group fields. Preserve unavailable rather than inventing
    # a hydro group by subtracting modeled supply from reported totals.
    fuel_group_reported=HYFIELD in b.columns
    if fuel_group_reported:
        b["mixed_hydro_pumped_mw"]=pd.to_numeric(
            b[HYFIELD].astype("string").str.strip().replace("",pd.NA),errors="coerce")
        if b.mixed_hydro_pumped_mw.isna().any() or not np.isfinite(
                b.mixed_hydro_pumped_mw.to_numpy(float)).all():
            raise ValueError("Missing/blank/invalid original EIA930 mixed hydro hourly gen")
    b["total_net_mw"]=pd.to_numeric(b["Net Generation (MW)"],errors="coerce")
    if b.total_net_mw.isna().any() or not np.isfinite(b.total_net_mw.to_numpy(float)).all():
        raise ValueError("Missing/blank/invalid original EIA930 total hourly net gen")
    cap=partial_capacity.loc[partial_capacity.ba.astype("string").str.strip().eq("BPAT")].copy()
    if len(cap)!=1 or not cap.capacity_source.astype(str).str.contains("GENERIC_THERMAL_PROXY").all():
        raise ValueError("Expected original partial gas/wind capacity proxy")
    for field in ("gas_mw","wind_mw"):
        cap[field]=pd.to_numeric(cap[field],errors="coerce")
    if not np.isfinite(cap[["gas_mw","wind_mw"]].to_numpy(float)).all() or cap[["gas_mw","wind_mw"]].lt(0).any().any():
        raise ValueError("Invalid original BPAT partial nameplate")
    values={r.prime_mover:float(r.net_generation_mwh) for r in p.itertuples(index=False)}
    monthly_eia923=float(sum(values.values()))
    eia930_hy=float(b.mixed_hydro_pumped_mw.sum()) if fuel_group_reported else None
    eia930_all=float(b.total_net_mw.sum())
    details={
        "ba":"BPAT","period":"2024-07","eia923_observed_hy_mwh":values["HY"],
        "eia923_observed_ps_signed_net_mwh":values["PS"],
        "eia923_observed_page1_hy_plus_ps_signed_net_mwh":monthly_eia923,
        "eia923_hy_source_plant_month_rows":int(p.loc[p.prime_mover.eq("HY"),"plant_month_rows"].iloc[0]),
        "eia923_ps_source_plant_month_rows":int(p.loc[p.prime_mover.eq("PS"),"plant_month_rows"].iloc[0]),
        "eia930_observed_hydro_plus_pumped_group_net_mwh":eia930_hy,
        "eia930_observed_ba_total_net_generation_mwh":eia930_all,
        "eia930_hydro_pumped_fraction_of_ba_total_net_generation":(
            eia930_hy/eia930_all if fuel_group_reported and eia930_all else None),
        "eia923_minus_eia930_mixed_group_source_scope_difference_mwh":(
            monthly_eia923-eia930_hy if fuel_group_reported else None),
        "eia923_to_eia930_mixed_group_reported_energy_ratio":(
            monthly_eia923/eia930_hy if fuel_group_reported and eia930_hy else None),
        "official_eia930_complete_july_hour_count":len(b),
        "eia930_mixed_hydro_fuel_group_reported_in_supplied_source":fuel_group_reported,
        "eia930_hydro_group_missing_must_not_be_imputed":True,
        "model_partial_gas_nameplate_mw":float(cap.gas_mw.iloc[0]),
        "model_partial_wind_nameplate_mw":float(cap.wind_mw.iloc[0]),
        "source_reporting_grains_equivalent_certified":False,
        "source_residual_is_missing_installed_capacity_mw":False,
        "eia923_page1_hy_is_hourly_deliverable_power":False,
        "eia923_ps_signed_net_is_storage_discharge_energy":False,
        "source_net_generation_is_historically_calibrated_pypsa_supply":False,
        "source_fleet_completeness_certified":False,
        "interties_or_storage_soc_verified":False,
        "historical_blackouts_or_eens_identified":False}
    return pd.DataFrame([details]),details

def main():
    parser=argparse.ArgumentParser()
    for a in ("eia923-month","official-eia930","partial-capacity","output"):
        parser.add_argument("--"+a,required=True)
    args=parser.parse_args()
    df,manifest=audit(
        pd.read_csv(args.eia923_month),
        pd.read_csv(args.official_eia930,dtype="string"),
        pd.read_csv(args.partial_capacity))
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/"bpat_july2024_eia923_page1_hy_ps_vs_eia930_mixed_hydro.csv",index=False)
    (out/"bpat_july2024_hydro_reporting_scope_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print("REAL BPAT JULY HYDRO MONTHLY REPORTING SCOPE DIAGNOSTIC")
    print(df.to_string(index=False))

if __name__=="__main__":
    main()
