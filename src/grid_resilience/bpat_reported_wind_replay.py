"""Replay EIA-930 reported BPAT wind as a *generation ceiling*, not weather potential.

Observed net generation is clipped at zero only for the explicit
nonnegative generator bound; negative reported hours are counted and
retained in audit metadata. This is an illustrative conditional replay,
not independent historical validation or a meteorological counterfactual.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .multi_technology_dispatch import solve

def run(demand,capacity,availability,wind_hourly,hydro_capacity,observed_context,output):
    c=pd.read_csv(capacity);a=pd.read_csv(availability);w=pd.read_csv(wind_hourly)
    fleet=pd.read_csv(hydro_capacity)
    h=fleet[(fleet.ba=="BPAT")&(fleet.technology=="hydro")]
    if len(h)!=1:raise ValueError("Missing unique BPAT hydro capacity")
    hydro_mw=float(h.iloc[0].nameplate_capacity_mw)
    wind_row=c[(c.ba=="BPAT")&(c.technology=="wind")]
    if len(wind_row)!=1:raise ValueError("Missing BPAT wind")
    wind_mw=float(wind_row.iloc[0].capacity_mw)
    if not 0<wind_mw<float("inf") or not 0<hydro_mw<float("inf"):raise ValueError("Invalid capacities")
    if w.timestamp.duplicated().any():raise ValueError("Duplicate wind hours")
    values=pd.to_numeric(w.reported_wind_mw,errors="raise")
    if values.isna().any():raise ValueError("Missing reported wind values")
    neg_count=int((values<0).sum())
    exceed_count=int((values>wind_mw).sum())
    clipped_negative_mwh=float((-values.clip(upper=0)).sum())
    clipped_above_capacity_mwh=float((values-wind_mw).clip(lower=0).sum())
    obs=pd.DataFrame({"timestamp":w.timestamp,"availability_pu":values.clip(lower=0,upper=wind_mw)/wind_mw})
    keys=a.loc[(a.ba=="BPAT")&(a.technology=="wind"),["timestamp"]]
    if set(obs.timestamp)!=set(keys.timestamp):raise ValueError("Wind and model timestamps differ")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    energy=0.05*float(json.loads(Path(observed_context).read_text())["reported_mixed_hydro_pumped_net_mwh"])
    c["energy_budget_mwh"]=float("nan")
    c=pd.concat([c,pd.DataFrame([{"ba":"BPAT","technology":"hydro","capacity_mw":hydro_mw,
                                  "marginal_cost":0,"energy_budget_mwh":energy}])],ignore_index=True)
    h_av=pd.DataFrame({"timestamp":keys.timestamp,"ba":"BPAT","technology":"hydro","availability_pu":0.10})
    results=[]
    for name,wind_multiplier in [("reported_wind_ceiling",1.0),("half_reported_wind_ceiling",0.5)]:
        case=out/name;case.mkdir(exist_ok=True)
        aa=a.copy();mask=(aa.ba=="BPAT")&(aa.technology=="wind")
        indexed=obs.set_index("timestamp").availability_pu
        aa.loc[mask,"availability_pu"]=aa.loc[mask,"timestamp"].map(indexed).to_numpy()*wind_multiplier
        aa=pd.concat([aa,h_av],ignore_index=True)
        aa.to_csv(case/"availability.csv",index=False)
        c.to_csv(case/"capacity.csv",index=False)
        short=solve(demand,case/"capacity.csv",case/"availability.csv",case/"dispatch")
        results.append({"scenario":name,"bpat_shortfall_mwh":float(short.loc[short.ba=="BPAT","unserved_energy_mwh"].iloc[0])})
    df=pd.DataFrame(results)
    df["incremental_shortfall_mwh"]=df.bpat_shortfall_mwh-df.iloc[0].bpat_shortfall_mwh
    df.to_csv(out/"bpat_reported_wind_replay_sensitivity.csv",index=False)
    manifest={"reported_negative_wind_hours":neg_count,
       "reported_above_nameplate_hours":exceed_count,
       "negative_net_generation_clipped_mwh":clipped_negative_mwh,
       "above_nameplate_generation_clipped_mwh":clipped_above_capacity_mwh,
       "observed_wind_replay_is_not_weather_validation":True,
       "wind_input":"EIA-930 reported net generation clipped at zero and EIA-860 nameplate ceiling",
       "observed_generation_as_availability_is_not_independent_validation":True,
       "wind_halving_is_hypothetical":True,"hydro_power_availability_assumed":0.1,
       "hydro_monthly_budget_assumed_mwh":energy,"historical_calibration_certified":False}
    (out/"bpat_reported_wind_replay_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return df
def main():
    p=argparse.ArgumentParser()
    for k in ("demand","capacity","availability","wind-hourly","hydro-capacity","observed-context","output"):
        p.add_argument("--"+k,required=True)
    x=p.parse_args()
    print(run(x.demand,x.capacity,x.availability,x.wind_hourly,x.hydro_capacity,x.observed_context,x.output).to_string(index=False))
if __name__=="__main__":main()
