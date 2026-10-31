"""Solve four-BA PyPSA with independent BPAT 29-site ERA5 wind proxy.

Only BPAT wind changes versus a constant 100%-wind control. Other availability
is deliberately assumed (including all other BAs); transmission is absent.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .bpat_era5_pypsa_availability import inject
from .multi_technology_dispatch import solve

def run(demand,capacity,availability,weather,output):
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    audit=inject(availability,weather,root)
    base=solve(demand,capacity,availability,root/"synthetic_full_wind_dispatch")
    met=solve(demand,capacity,root/"era5_29site_wind_availability.csv",root/"era5_wind_dispatch")
    compare=base.rename(columns={"unserved_energy_mwh":"full_wind_shortfall_mwh"}).merge(
      met.rename(columns={"unserved_energy_mwh":"era5_proxy_shortfall_mwh"}),on="ba",validate="one_to_one")
    compare["incremental_shortfall_mwh"]=compare.era5_proxy_shortfall_mwh-compare.full_wind_shortfall_mwh
    if (compare.incremental_shortfall_mwh < -0.1).any():
        raise AssertionError("Wind ceiling reduction improved shortage unexpectedly")
    compare.to_csv(root/"bpat_era5_pypsa_conditional_shortfall.csv",index=False)
    meta={"weather":"29 BPAT wind plant ERA5 100-m hourly, uncalibrated idealized turbine curve",
      "replaced_hours":audit["replaced_bpat_wind_hours"],
      "control":"synthetic 100% generator availability for all modeled technologies",
      "other_technologies_availability_assumed":True,
      "inter_ba_transmission_enabled":False,
      "hydro_and_other_missing_technology_fleet_calibrated":False,
      "historical_shortfall_claim":False}
    (root/"bpat_era5_pypsa_conditional_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    return compare
def main():
    p=argparse.ArgumentParser()
    for key in ("demand","capacity","availability","weather","output"):p.add_argument("--"+key,required=True)
    a=p.parse_args();print(run(a.demand,a.capacity,a.availability,a.weather,a.output).to_string(index=False))
if __name__=="__main__":main()
