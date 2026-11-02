"""Full-calendar-month isolated-BA PyPSA adequacy screen.

Inputs: hourly UTC demand (timestamp, ba, demand_mw) and technology capacities
(ba, technology, capacity_mw, marginal_cost). Availability is constant at 1,
unless independently provided; this is NOT historical generation calibration.
"""
import argparse,calendar,json
from pathlib import Path
import pandas as pd

def run(demand,capacity,year,month):
    import pypsa
    expected=calendar.monthrange(year,month)[1]*24
    d=demand.copy();c=capacity.copy()
    if not {"timestamp","ba","demand_mw"}.issubset(d) or not {"ba","technology","capacity_mw","marginal_cost"}.issubset(c):
        raise ValueError("Missing monthly screen fields")
    d["timestamp"]=pd.to_datetime(d.timestamp,utc=True,errors="raise")
    d["demand_mw"]=pd.to_numeric(d.demand_mw,errors="raise")
    for k in ("capacity_mw","marginal_cost"):c[k]=pd.to_numeric(c[k],errors="raise")
    if d[["timestamp","ba","demand_mw"]].isna().any().any() or c.isna().any().any():raise ValueError("Missing values")
    if d.duplicated(["timestamp","ba"]).any() or c.duplicated(["ba","technology"]).any():raise ValueError("Duplicate keys")
    if (d.demand_mw<0).any() or (c.capacity_mw<0).any():raise ValueError("Negative values")
    if set(d.ba)!=set(c.ba):raise ValueError("BA coverage mismatch")
    timestamps=pd.date_range(f"{year}-{month:02d}-01",periods=expected,freq="h",tz="UTC")
    for ba,g in d.groupby("ba"):
        if len(g)!=expected or not pd.DatetimeIndex(g.timestamp.sort_values()).equals(timestamps):
            raise ValueError(f"Incomplete calendar month for {ba}")
    n=pypsa.Network();n.set_snapshots(timestamps.tz_localize(None))
    for ba in sorted(c.ba.unique()):
        n.add("Bus",ba)
        load=d[d.ba==ba].set_index("timestamp").reindex(timestamps).demand_mw
        n.add("Load",f"{ba}_demand",bus=ba,p_set=load.to_numpy())
        for r in c[c.ba==ba].itertuples(index=False):
            n.add("Generator",f"{ba}__{r.technology}",bus=ba,p_nom=float(r.capacity_mw),
                  marginal_cost=float(r.marginal_cost),carrier=r.technology)
        n.add("Generator",f"{ba}__UNSERVED",bus=ba,p_nom=float(d[d.ba==ba].demand_mw.max())+1,
              marginal_cost=100000.0,carrier="UNSERVED")
    n.optimize(solver_name="highs")
    gen=n.generators_t.p
    if gen.empty:raise ValueError("No optimized generation")
    records=[]
    for ba in sorted(c.ba.unique()):
        for r in c[c.ba==ba].itertuples(index=False):
            records.append({"year":year,"month":month,"ba":ba,"technology":r.technology,
                            "modeled_generation_mwh":float(gen[f"{ba}__{r.technology}"].sum())})
    shortage={ba:float(gen[f"{ba}__UNSERVED"].sum()) for ba in sorted(c.ba.unique())}
    return pd.DataFrame(records),shortage

def main():
    p=argparse.ArgumentParser()
    for key in ("demand","capacity","output"):p.add_argument("--"+key,required=True)
    p.add_argument("--year",type=int,required=True);p.add_argument("--month",type=int,required=True)
    a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    values,shortage=run(pd.read_csv(a.demand),pd.read_csv(a.capacity),a.year,a.month)
    values.to_csv(out/"modeled_monthly_generation.csv",index=False)
    (out/"screening_manifest.json").write_text(json.dumps({"year":a.year,"month":a.month,
       "modeled_unserved_mwh_by_ba":shortage,"historical_calibration_certified":False,
       "limitations":"Unconstrained isolated BA, constant available generation, hypothetical capacities and no observed plant dispatch or transfers."},indent=2)+"\n")
if __name__=="__main__":main()
