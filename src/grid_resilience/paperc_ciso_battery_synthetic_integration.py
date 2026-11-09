"""Synthetic PyPSA integration smoke for empirically scaled but uncalibrated CISO storage CSV.

The synthetic 3-hour demand is entirely fabricated and explicitly unrelated to
real July 2023 or July 2024 CAISO adequacy, outages or actual EENS.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

from .multi_technology_dispatch import solve


def verify_config(source):
    d=pd.read_csv(source)
    fields={"ba","power_mw","energy_mwh","efficiency_store",
            "efficiency_dispatch","initial_soc_fraction"}
    if not fields.issubset(d) or len(d)!=1 or d.ba.iloc[0]!="CISO":
        raise ValueError("Expected only one source-derived hypothetical CISO StorageUnit row")
    v=d.iloc[0]
    if not (v.power_mw>0 and v.energy_mwh>0 and
            abs(v.energy_mwh/v.power_mw-2)<1e-7 and
            abs(v.initial_soc_fraction-.25)<1e-7):
        raise ValueError("Unexpected synthetic smoke source candidate")
    return v


def run(source,output):
    row=verify_config(source)
    target=Path(output)
    target.mkdir(parents=True,exist_ok=True)
    ts=pd.date_range("2026-01-01T00:00:00Z",periods=3,freq="h")
    pd.DataFrame({"timestamp":ts,"ba":["CISO"]*3,
                  "demand_mw":[1000.]*3}).to_csv(target/"synthetic_demand.csv",index=False)
    pd.DataFrame([{"ba":"CISO","technology":"gas","capacity_mw":0.,
                   "marginal_cost":100.}]).to_csv(target/"synthetic_capacity.csv",index=False)
    pd.DataFrame({"timestamp":ts,"ba":["CISO"]*3,
                  "technology":["gas"]*3,"availability_pu":[1.]*3
                  }).to_csv(target/"synthetic_availability.csv",index=False)
    baseline=solve(target/"synthetic_demand.csv",target/"synthetic_capacity.csv",
                   target/"synthetic_availability.csv",target/"synthetic_baseline")
    modeled=solve(target/"synthetic_demand.csv",target/"synthetic_capacity.csv",
                  target/"synthetic_availability.csv",target/"synthetic_with_storage",
                  storage_csv=source)
    no=float(baseline.unserved_energy_mwh.iloc[0])
    yes=float(modeled.unserved_energy_mwh.iloc[0])
    if abs(no-3000)>1e-3:
        raise AssertionError("Synthetic dispatch baseline incorrect")
    if not 0<=yes<no:
        raise AssertionError("Hypothetical StorageUnit did not change synthetic dispatch")
    soc=pd.read_csv(target/"synthetic_with_storage"/"storage_soc_mwh.csv")
    if len(soc)!=3 or soc["CISO_battery"].lt(-1e-4).any() or (
        soc["CISO_battery"]>row.energy_mwh+1e-4).any():
        raise AssertionError("Simulated SOC violated explicit hypothetical bounds")
    manifest={"purpose":"software interface integration of source-scaled hypothetical CISO battery",
       "simulation_dates":"2026-01-01 00:00 to 03:00 UTC (synthetic only)",
       "synthetic_demand_mw_per_hour":1000,
       "synthetic_gas_capacity_mw":0,
       "hypothetical_storage_power_mw":float(row.power_mw),
       "hypothetical_storage_energy_mwh":float(row.energy_mwh),
       "hypothetical_initial_soc_fraction":float(row.initial_soc_fraction),
       "solver_zero_storage_synthetic_unserved_mwh":no,
       "solver_storage_synthetic_unserved_mwh":yes,
       "uses_real_historical_demand":False,
       "uses_real_historical_generator_availability":False,
       "real_battery_SoC_or_ratings_calibrated":False,
       "synthetic_shortfall_is_not_observed_EENS":True}
    (target/"synthetic_ciso_storageunit_integration_scope.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print("SYNTHETIC-ONLY STORAGE UNIT INTERFACE VERIFIED",json.dumps(manifest))
    return manifest


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--storage",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    run(a.storage,a.output)
