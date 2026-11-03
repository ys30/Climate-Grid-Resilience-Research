"""Independently verify the 744-hour SRP no-HY/PS baseline against its LP oracle.

This verifies a *screening* model, not measured historical load shedding.
Requires dispatchable, nonnegative-cost fuel capacity, no unit commitment,
and fixed exogenous import/export data. Fail closed if these change.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from grid_resilience.exchange_analytical_reference import reference

REQUIRED={
 "timestamp_utc","demand_mw","observed_export_mw","observed_import_mw",
 "screened_fleet_generation_mw","modeled_unserved_mw",
 "boundary_spill_mw","hydro_dispatch_mw","ps_charge_mw",
 "ps_discharge_mw","bus_balance_residual_mw"
}

def audit(hourly, capacity, *, ba="SRP", year=2024, month=1, tol=1e-5):
    if not REQUIRED.issubset(hourly.columns):
        raise ValueError("Missing diagnostic fields: "+str(sorted(REQUIRED-set(hourly.columns))))
    if not {"ba","technology","capacity_mw","marginal_cost"}.issubset(capacity.columns):
        raise ValueError("Missing capacity fields")
    d=hourly.copy()
    timestamps=pd.to_datetime(d.timestamp_utc,utc=True,errors="raise")
    start=pd.Timestamp(f"{year}-{month:02d}-01",tz="UTC")
    stop=start+pd.offsets.MonthBegin(1)
    expected=pd.date_range(start,stop,freq="h",inclusive="left")
    if len(d)!=len(expected) or timestamps.duplicated().any() or not pd.DatetimeIndex(timestamps).equals(expected):
        raise ValueError("Incomplete or unsorted UTC baseline hours")
    numeric=list(REQUIRED-{"timestamp_utc"})
    for k in numeric:d[k]=pd.to_numeric(d[k],errors="raise")
    if not np.isfinite(d[numeric].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite hourly diagnostics")
    if (d[["demand_mw","observed_import_mw","observed_export_mw"]]<0).any().any():
        raise ValueError("Negative local demand or unsigned boundary component")
    if not np.allclose(d[["hydro_dispatch_mw","ps_charge_mw","ps_discharge_mw"]],0,atol=tol,rtol=0):
        raise ValueError("This oracle is for a baseline without HY/PS dispatch")
    if ((d.observed_import_mw>tol)&(d.observed_export_mw>tol)).any():
        raise ValueError("Observed signed interchange split is inconsistent")
    c=capacity[capacity.ba.eq(ba)].copy()
    if c.empty or c.technology.duplicated().any():
        raise ValueError("Empty or duplicate screened fuel inventory")
    for field in ("capacity_mw","marginal_cost"):
        c[field]=pd.to_numeric(c[field],errors="raise")
    if not np.isfinite(c[["capacity_mw","marginal_cost"]].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite capacity or cost")
    if (c.capacity_mw<0).any() or (c.marginal_cost<=0).any() or (c.marginal_cost>=100000).any():
        raise ValueError("Oracle requires positive local generation costs below shortage penalty")
    cap=float(c.capacity_mw.sum())
    signed=d.observed_export_mw-d.observed_import_mw
    target=reference(d.demand_mw.to_numpy(),signed.to_numpy(),cap)
    target_hour=d.demand_mw+d.observed_export_mw-d.observed_import_mw
    modeled_generation=target_hour.clip(lower=0,upper=cap)
    modeled_shortage=(target_hour-modeled_generation).clip(lower=0)
    modeled_spill=(-target_hour).clip(lower=0)
    errors={
      "generation":float((d.screened_fleet_generation_mw-modeled_generation).abs().max()),
      "unserved":float((d.modeled_unserved_mw-modeled_shortage).abs().max()),
      "spill":float((d.boundary_spill_mw-modeled_spill).abs().max()),
      "bus_balance":float(d.bus_balance_residual_mw.abs().max()),
    }
    if max(errors.values())>tol:
        raise RuntimeError(f"Analytic dispatch disagreement: {errors}")
    result={
      "ba":ba,"period":f"{year}-{month:02d}","source_hour_count":len(d),
      "screened_dispatchable_capacity_mw":cap,
      "modeled_unserved_mwh":target["unserved_mwh"],
      "hours_with_modeled_unserved":target["hours_with_unserved"],
      "maximum_hourly_unserved_mw":float(modeled_shortage.max()),
      "largest_hourly_error_mw_by_component":errors,
      "historical_shortage_observed":False,
      "historical_calibration_certified":False,
      "oracle_scope":"single BA aggregate capacity, constant p_nom, positive costs, fixed observed exchange; no HY/PS or topology"
    }
    return result

def main():
    p=argparse.ArgumentParser()
    for k in ("hourly","capacity","output"):p.add_argument("--"+k,required=True)
    p.add_argument("--ba",default="SRP");p.add_argument("--year",type=int,default=2024)
    p.add_argument("--month",type=int,default=1)
    a=p.parse_args()
    result=audit(pd.read_csv(a.hourly),pd.read_csv(a.capacity),ba=a.ba,year=a.year,month=a.month)
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
