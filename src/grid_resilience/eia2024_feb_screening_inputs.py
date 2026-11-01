"""Build a clearly labeled historical-demand / EIA-860-capacity screening dispatch.

Historical hourly demand and reported nameplate capacity are observed.
Constant technology availability and costs are assumptions, never calibration.
"""
import argparse,json
from pathlib import Path
import pandas as pd

TECH={"gas","coal","nuclear","hydro","solar","wind","geothermal","oil","biomass"}
BAS={"AZPS","BPAT","CISO","SRP"}
COST={"gas":50,"coal":70,"nuclear":12,"hydro":5,"solar":0,"wind":0,
      "geothermal":10,"oil":180,"biomass":80}

def build(demand_csv, capacity_csv, output):
    demand=pd.read_csv(demand_csv)
    capacity=pd.read_csv(capacity_csv)
    if not {"timestamp","ba","demand_mw"}.issubset(demand):raise ValueError("Demand columns missing")
    if not {"ba","technology","nameplate_capacity_mw"}.issubset(capacity):
        raise ValueError("EIA-860 capacity columns missing")
    if demand.empty or capacity.empty:raise ValueError("Missing empirical inputs")
    demand["timestamp"]=pd.to_datetime(demand.timestamp,utc=True,errors="raise")
    if demand.duplicated(["timestamp","ba"]).any():raise ValueError("Duplicate demand BA-hour")
    if not demand.ba.isin(BAS).all() or set(demand.ba)!=BAS:
        raise ValueError("Incomplete four-BA demand coverage")
    expected=pd.date_range("2024-02-01",periods=696,freq="h",tz="UTC")
    if set(demand.timestamp.unique())!=set(expected):
        raise ValueError("Not a complete February 2024 hourly demand period")
    if any(set(g.timestamp)!=set(expected) for _,g in demand.groupby("ba")):
        raise ValueError("Incomplete demand BA-hour grid")
    demand["demand_mw"]=pd.to_numeric(demand.demand_mw,errors="raise")
    if not demand.demand_mw.map(lambda v:0<=float(v)<float("inf")).all():raise ValueError("Invalid demand")
    if capacity.duplicated(["ba","technology"]).any():raise ValueError("Duplicate capacity BA/technology")
    if not capacity.ba.isin(BAS).all():raise ValueError("Unknown capacity BA")
    if not capacity.technology.isin(TECH).all():
        raise ValueError("Unsupported EIA860 technology in screening; reconcile classification")
    capacity["capacity_mw"]=pd.to_numeric(capacity.nameplate_capacity_mw,errors="raise")
    if not capacity.capacity_mw.map(lambda v:0<float(v)<float("inf")).all():
        raise ValueError("Nonpositive or invalid nameplate capacity")
    missing=sorted(BAS-set(capacity.ba))
    if missing:raise ValueError(f"Missing capacity for BAs: {missing}")
    capacity["marginal_cost"]=capacity.technology.map(COST)
    availability=demand[["timestamp","ba"]].merge(capacity[["ba","technology"]],on="ba",validate="many_to_many")
    availability["availability_pu"]=1.0
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    demand.assign(timestamp=demand.timestamp.map(lambda t:t.isoformat())).sort_values(
        ["timestamp","ba"]).to_csv(out/"demand.csv",index=False)
    capacity[["ba","technology","capacity_mw","marginal_cost"]].sort_values(
        ["ba","technology"]).to_csv(out/"capacity.csv",index=False)
    availability.assign(timestamp=availability.timestamp.map(lambda t:t.isoformat())).sort_values(
        ["timestamp","ba","technology"]).to_csv(out/"availability.csv",index=False)
    manifest={"status":"historical_demand_and_reported_nameplate_screening",
              "demand_provenance":"EIA-930 official reported raw hourly demand; 2024-02 UTC hour-start",
              "capacity_provenance":"EIA-860 2024 reported Plant BA and single-fuel operable nameplate candidates",
              "demand_hours_per_ba":696,"bas":sorted(BAS),
              "technology_count":int(len(capacity)),
              "availability_assumption":"Every included generator has constant 100% availability; not measured",
              "marginal_cost_assumption":"Static illustrative dispatch costs, USD/MWh; not observed",
              "excluded_fleet_warning":"EIA-860 candidate filter excludes some generators; does not certify complete BA fleet",
              "historical_inputs_verified":False,"modeled_generation_is_net_mwh":False,
              "historical_calibration_certified":False}
    (out/"screening_input_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    for k in ("demand","capacity","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args();print(json.dumps(build(a.demand,a.capacity,a.output),indent=2))
if __name__=="__main__":main()
