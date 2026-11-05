"""Within-unit exploratory OLS with demand, local-hour and local-day controls.

This is NOT a causal heat-derating model. The outcomes are source operating
indicators and conditional source gross load, not generator available net MW.
Separate fits by EPA source unit avoid false independence from shared weather.
No standard errors or inferential significance are asserted.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from grid_resilience.srp_epa_era5_eia930_demand_context import summarize as validate_demand_context

def design(g):
    # Original EPA Part75 clock is local STANDARD time UTC−7 all year in AZ.
    local = g.timestamp_utc.dt.tz_convert("Etc/GMT+7")
    h = pd.get_dummies(local.dt.hour, prefix="hour", dtype=float)
    h = h.reindex(columns=[f"hour_{j}" for j in range(1,24)], fill_value=0.0)
    day = pd.get_dummies(local.dt.day, prefix="day", dtype=float)
    day = day.reindex(columns=[f"day_{j}" for j in range(2,32)], fill_value=0.0)
    controls = np.column_stack([
        np.ones(len(g)),
        g.srp_demand_mw.to_numpy(float) / 1000.0,
        h.to_numpy(float), day.to_numpy(float)
    ])
    temp = g.temperature_2m_c.to_numpy(float)
    return controls, temp

def fit(y, controls, temperature, *, min_n=80):
    valid = np.isfinite(y) & np.isfinite(temperature) & np.isfinite(controls).all(axis=1)
    y, c, t = y[valid], controls[valid], temperature[valid]
    n = len(y)
    if n < min_n:
        return {"n": n, "status": "insufficient_outcome_records", "temp_coef": None, "r2": None}
    base_rank = np.linalg.matrix_rank(c)
    x = np.column_stack([c, t])
    rank = np.linalg.matrix_rank(x)
    if rank <= base_rank or rank >= n:
        return {"n": n, "status": "temperature_unidentified_after_controls", "temp_coef": None, "r2": None}
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    total = np.sum((y - y.mean())**2)
    return {"n": n, "status": "descriptive_ols_only", "temp_coef": float(beta[-1]),
            "r2": float(1-np.sum(residual**2)/total) if total>0 else None}

def audit(epa, eia):
    _, _, validated = validate_demand_context(epa, eia)
    if validated["eia930_july_utc_matched_hours_per_plant"] != 737:
        raise ValueError("Source intersection not admitted")
    x = epa.copy()
    required = {"facility_id", "unit_id", "timestamp_utc", "temperature_2m_c",
                "operating_time", "gross_load_mw"}
    if not required.issubset(x):
        raise ValueError("Missing reported EPA operating fields")
    x["facility_id"] = x.facility_id.astype("string").str.strip()
    x["unit_id"] = x.unit_id.astype("string").str.strip()
    x["timestamp_utc"] = pd.to_datetime(x.timestamp_utc, utc=True, errors="raise")
    for col in ("temperature_2m_c", "operating_time", "gross_load_mw"):
        x[col] = pd.to_numeric(x[col], errors="coerce")
    if x.operating_time.dropna().lt(0).any() or x.operating_time.dropna().gt(1).any():
        raise ValueError("Source operating time out of bounds")
    if not np.isfinite(x.gross_load_mw.dropna().to_numpy(float)).all():
        raise ValueError("Nonfinite reported gross load")
    e = eia.loc[eia["Balancing Authority"].astype("string").str.strip().eq("SRP")].copy()
    e["timestamp_utc"] = pd.to_datetime(e["UTC Time at End of Hour"],
        format="%m/%d/%Y %I:%M:%S %p", utc=True) - pd.Timedelta(hours=1)
    e["srp_demand_mw"] = pd.to_numeric(e["Demand (MW)"], errors="raise")
    x = x.merge(e[["timestamp_utc", "srp_demand_mw"]], how="inner",
        on="timestamp_utc", validate="many_to_one")
    if len(x) != 7370 or x.groupby(["facility_id", "unit_id"]).size().ne(737).any():
        raise ValueError("Expected exactly ten EPA units each with 737 source-matched hours")
    rows=[]
    for (plant,unit),g in x.groupby(["facility_id","unit_id"],sort=True):
        g = g.sort_values("timestamp_utc").reset_index(drop=True)
        controls,temp = design(g)
        # Missing Operating Time is not evidence of zero operation.
        y = np.where(g.operating_time.notna(),(g.operating_time>0).astype(float),np.nan)
        a=fit(y,controls,temp)
        # Do not treat zero/nonoperating gross load as available capacity.
        actual = np.where(g.operating_time.gt(0),g.gross_load_mw,np.nan).astype(float)
        b=fit(actual,controls,temp)
        rows.append({"facility_id":str(plant),"epa_unit_id":str(unit),
            "hours_with_ba_demand_context":len(g),
            "observed_positive_operation_rows":int(np.nansum(y)),
            "reported_gross_load_given_operation_rows":int(np.isfinite(actual).sum()),
            "operation_model_status":a["status"],
            "operation_model_n":a["n"],
            "operation_lpm_temperature_coefficient_per_c":a["temp_coef"],
            "operation_model_r2":a["r2"],
            "gross_load_model_status":b["status"],
            "gross_load_model_n":b["n"],
            "gross_load_temperature_coefficient_mw_per_c":b["temp_coef"],
            "gross_load_model_r2":b["r2"]})
    out=pd.DataFrame(rows)
    manifest={"model":"Within-EPA-source-unit OLS exploratory association",
      "outcomes":["binary reported Operating Time >0 (linear probability)",
                  "source gross load MW conditional on positive reported operation"],
      "predictors":["ERA5 site temperature °C","SRP-wide EIA930 demand GW",
                    "local standard hour fixed effects","local standard date fixed effects"],
      "local_clock":"America/Phoenix / MST UTC-7 year-round",
      "source_matched_hours_per_unit":737,
      "unmatched_source_hours_per_unit":7,
      "no_standard_errors_or_p_values_claimed":True,
      "temporal_dependence_and_dispatch_selection_unresolved":True,
      "causal_temperature_derating_or_eia_generator_net_mw_estimated":False,
      "physical_generator_identity_admitted":False,
      "srp_ba_demand_is_plant_dispatch":False}
    return out,manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--epa-era5-panel",required=True)
    p.add_argument("--eia930-july",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    out,meta=audit(pd.read_csv(a.epa_era5_panel,
        dtype={"facility_id":"string","unit_id":"string"}),
        pd.read_csv(a.eia930_july,dtype="string"))
    root=Path(a.output);root.mkdir(parents=True,exist_ok=True)
    out.to_csv(root/"epa_eia930_hour_day_controlled_exploratory_ols.csv",index=False)
    (root/"epa_eia930_controlled_exploratory_scope.json").write_text(
        json.dumps(meta,indent=2)+"\n")
    print(out.to_string(index=False))

if __name__=="__main__":
    main()
