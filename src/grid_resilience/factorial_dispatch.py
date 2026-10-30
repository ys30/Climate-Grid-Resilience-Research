"""Matched four-way PyPSA dispatch experiment with explicitly hypothetical interties.

All input tables must be provided; no observed datasets are fabricated by this module.
"""
import argparse
from pathlib import Path
import pandas as pd

SCENARIOS = {"baseline": (0., 0.), "heat_only": (4., 0.),
             "wind_only": (0., .30), "heat_wind": (4., .30)}

def solve(demand_path, weather_path, capacity_path, links_path, output,
          event_id, network_variant="illustrative", heat_load_coefficient=.012):
    import pypsa
    demand=pd.read_csv(demand_path)
    weather=pd.read_csv(weather_path)
    capacity=pd.read_csv(capacity_path)
    links=pd.read_csv(links_path)
    for data,cols in [(demand,{"timestamp","ba","demand_mw"}),
                       (weather,{"timestamp","ba","temperature_c","wind_availability"}),
                       (capacity,{"ba","gas_mw","wind_mw"}),
                       (links,{"from_ba","to_ba","capacity_mw"})]:
        if not cols.issubset(data.columns):
            raise ValueError(f"Input columns missing: {cols-set(data.columns)}")
    for df in (demand,weather):
        df["timestamp"]=pd.to_datetime(df.timestamp,utc=True)
        if df.duplicated(["timestamp","ba"]).any():
            raise ValueError("Duplicate BA-hour input")
    if capacity.ba.duplicated().any() or capacity.empty:
        raise ValueError("Duplicate or empty BA capacities")
    bas=set(capacity.ba)
    if set(demand.ba)!=bas or set(weather.ba)!=bas:
        raise ValueError("BA inventory mismatch")
    timestamps=pd.DatetimeIndex(sorted(demand.timestamp.unique()))
    expected=pd.MultiIndex.from_product([timestamps,sorted(bas)],names=["timestamp","ba"])
    if not pd.MultiIndex.from_frame(demand[["timestamp","ba"]]).unique().equals(expected):
        if set(map(tuple,demand[["timestamp","ba"]].itertuples(index=False,name=None)))!=set(expected):
            raise ValueError("Incomplete BA-hour demand")
    if set(map(tuple,weather[["timestamp","ba"]].itertuples(index=False,name=None)))!=set(expected):
        raise ValueError("Incomplete BA-hour weather")
    if len(timestamps)<1 or (len(timestamps)>1 and not (timestamps[1:]-timestamps[:-1]==pd.Timedelta(hours=1)).all()):
        raise ValueError("Expected consecutive hourly observations")
    for df,cols in [(demand,["demand_mw"]),(weather,["temperature_c","wind_availability"]),
                    (capacity,["gas_mw","wind_mw"]),(links,["capacity_mw"])]:
        for col in cols:
            df[col]=pd.to_numeric(df[col],errors="raise")
            if df[col].isna().any():raise ValueError(f"Missing {col}")
    if (demand.demand_mw<0).any() or (capacity[["gas_mw","wind_mw"]]<0).any().any() or (links.capacity_mw<0).any():
        raise ValueError("Negative demand/capacity")
    if not weather.wind_availability.between(0,1).all():raise ValueError("Wind availability outside 0..1")
    if not set(links.from_ba).union(links.to_ba).issubset(bas):
        raise ValueError("Link endpoint outside BA inventory")
    if (links.from_ba==links.to_ba).any():raise ValueError("Self links unsupported")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    load=demand.set_index(["timestamp","ba"]).demand_mw
    climate=weather.set_index(["timestamp","ba"])
    rows=[]
    generation_rows=[]
    for scenario,(heat,wind_penalty) in SCENARIOS.items():
        n=pypsa.Network()
        n.set_snapshots(timestamps.tz_localize(None))
        for ba in sorted(bas):
            c=capacity.set_index("ba").loc[ba]
            d=load.xs(ba,level="ba").reindex(timestamps)
            w=climate.xs(ba,level="ba").reindex(timestamps)
            baseline_excess=(w.temperature_c-30).clip(lower=0)
            shocked_excess=(w.temperature_c+heat-30).clip(lower=0)
            additional_load=heat_load_coefficient*(shocked_excess-baseline_excess)
            n.add("Bus",ba)
            n.add("Load",f"{ba}_load",bus=ba,p_set=(d*(1+additional_load)).to_numpy())
            n.add("Generator",f"{ba}_gas",bus=ba,p_nom=float(c.gas_mw),marginal_cost=70)
            n.add("Generator",f"{ba}_wind",bus=ba,p_nom=float(c.wind_mw),
                  p_max_pu=(w.wind_availability*(1-wind_penalty)).to_numpy(),marginal_cost=0)
            n.add("Generator",f"{ba}_unserved",bus=ba,p_nom=1e8,marginal_cost=10000)
        for i,row in links.iterrows():
            n.add("Link",f"intertie_{i}",bus0=row.from_ba,bus1=row.to_ba,
                  p_nom=float(row.capacity_mw),p_min_pu=-1,efficiency=1)
        status,condition=n.optimize(solver_name="highs")
        if (status,condition)!=("ok","optimal"):
            raise RuntimeError(f"{scenario}: {status}/{condition}")
        for ba in sorted(bas):
            for tech, suffix in (("generic_thermal_proxy", "gas"), ("wind", "wind")):
                production = n.generators_t.p[f"{ba}_{suffix}"]
                for stamp, mw in zip(timestamps, production.to_numpy()):
                    generation_rows.append({
                        "event_id": event_id, "network_variant": network_variant,
                        "scenario": scenario, "timestamp": stamp.isoformat(),
                        "ba": ba, "technology": tech, "generation_mwh": float(mw)
                    })
            series=n.generators_t.p[f"{ba}_unserved"].clip(lower=0)
            rows.append(dict(event_id=event_id,network_variant=network_variant,scenario=scenario,ba=ba,
                             unserved_energy_mwh=float(series.sum()),
                             shortage_hours=int((series>1e-4).sum()),
                             peak_shortfall_mw=float(series.max())))
    result=pd.DataFrame(rows)
    result.to_csv(out/"factorial_dispatch.csv",index=False)
    hourly = pd.DataFrame(generation_rows)
    hourly.to_csv(out/"factorial_generation_hourly.csv", index=False)
    # The observed-comparison adapter expects monthly BA/technology values.
    # Keep baseline and the partial-fleet mapping explicit; never combine
    # counterfactual scenarios or assign omitted technologies zero generation.
    baseline = hourly.loc[hourly.scenario == "baseline"].copy()
    baseline["period"] = pd.to_datetime(baseline.timestamp, utc=True).dt.strftime("%Y-%m")
    monthly = baseline.groupby(["ba", "technology", "period"], as_index=False).generation_mwh.sum()
    monthly.to_csv(out/"baseline_generation_monthly_partial_fleet.csv", index=False)
    from .factorial_interactions import decompose
    decompose(result).to_csv(out/"factorial_interactions.csv",index=False)
    return result

def main():
    p=argparse.ArgumentParser()
    for arg in ("demand","weather","capacity","links","output","event-id"):
        p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    solve(a.demand,a.weather,a.capacity,a.links,a.output,a.event_id)

if __name__=="__main__":main()
