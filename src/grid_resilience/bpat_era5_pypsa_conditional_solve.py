"""Solve four-BA PyPSA with independent BPAT 29-site ERA5 wind proxy.

Only BPAT wind changes versus a constant 100%-wind control. Other availability
is deliberately assumed (including all other BAs); transmission is absent.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .bpat_era5_pypsa_availability import inject
from .multi_technology_dispatch import solve

def run(demand,capacity,availability,weather,observed_wind,output):
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    audit=inject(availability,weather,root)
    base=solve(demand,capacity,availability,root/"synthetic_full_wind_dispatch")
    met=solve(demand,capacity,root/"era5_29site_wind_availability.csv",root/"era5_wind_dispatch")
    # Historical net generation is a *replay ceiling*, never independent weather.
    obs=pd.read_csv(observed_wind)
    if not {"timestamp","reported_wind_mw"}.issubset(obs):raise ValueError("Invalid observation input")
    obs["timestamp"]=pd.to_datetime(obs.timestamp,utc=True)
    if len(obs)!=696 or obs.timestamp.duplicated().any():raise ValueError("Incomplete EIA-930 wind hours")
    cap=pd.read_csv(capacity)
    wind=cap[(cap.ba=="BPAT")&(cap.technology=="wind")]
    if len(wind)!=1:raise ValueError("Missing BPAT wind capacity")
    mw=float(wind.capacity_mw.iloc[0])
    observed_avail=pd.read_csv(availability)
    observed_avail["time_utc"]=pd.to_datetime(observed_avail.timestamp,utc=True)
    mask=(observed_avail.ba=="BPAT")&(observed_avail.technology=="wind")
    if mask.sum()!=696 or set(observed_avail.loc[mask,"time_utc"])!=set(obs.timestamp):
        raise ValueError("Mismatch in observed wind UTC hours")
    ceiling=pd.Series(obs.reported_wind_mw.clip(lower=0,upper=mw).to_numpy()/mw,index=obs.timestamp)
    observed_avail.loc[mask,"availability_pu"]=observed_avail.loc[mask,"time_utc"].map(ceiling).to_numpy()
    observed_avail.drop(columns="time_utc").to_csv(root/"observed_wind_replay_availability.csv",index=False)
    replay=solve(demand,capacity,root/"observed_wind_replay_availability.csv",root/"observed_wind_dispatch")
    compare=base.rename(columns={"unserved_energy_mwh":"full_wind_shortfall_mwh"}).merge(
      met.rename(columns={"unserved_energy_mwh":"era5_proxy_shortfall_mwh"}),on="ba",validate="one_to_one")
    compare=compare.merge(replay.rename(columns={"unserved_energy_mwh":"observed_replay_shortfall_mwh"}),on="ba",validate="one_to_one")
    compare["era5_minus_observed_replay_shortfall_mwh"]=compare.era5_proxy_shortfall_mwh-compare.observed_replay_shortfall_mwh
    compare["incremental_shortfall_mwh"]=compare.era5_proxy_shortfall_mwh-compare.full_wind_shortfall_mwh
    if (compare.incremental_shortfall_mwh < -0.1).any():
        raise AssertionError("Wind ceiling reduction improved shortage unexpectedly")
    compare.to_csv(root/"bpat_era5_pypsa_conditional_shortfall.csv",index=False)
    meta={"weather":"29 BPAT wind plant ERA5 100-m hourly, uncalibrated idealized turbine curve",
      "replaced_hours":audit["replaced_bpat_wind_hours"],
      "control":"synthetic 100% generator availability for all modeled technologies",
      "observed_replay":"EIA-930 reported wind net generation is clipped and used as hourly cap, not weather potential",
      "other_technologies_availability_assumed":True,
      "inter_ba_transmission_enabled":False,
      "hydro_and_other_missing_technology_fleet_calibrated":False,
      "historical_shortfall_claim":False}
    (root/"bpat_era5_pypsa_conditional_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    return compare
def main():
    p=argparse.ArgumentParser()
    for key in ("demand","capacity","availability","weather","observed-wind","output"):p.add_argument("--"+key,required=True)
    a=p.parse_args();print(run(a.demand,a.capacity,a.availability,a.weather,a.observed_wind,a.output).to_string(index=False))
if __name__=="__main__":main()
