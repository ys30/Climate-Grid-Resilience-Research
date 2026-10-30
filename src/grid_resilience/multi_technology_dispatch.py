"""Isolated multi-technology PyPSA dispatch proof of concept (synthetic-ready only).

No weather shock, storage operation, historical calibration or firm intertie
ratings are inferred. Demand and availability must be supplied explicitly.
"""
from pathlib import Path
import argparse
import pandas as pd

DISPATCH_TECH = {"gas", "coal", "nuclear", "hydro", "solar", "wind", "geothermal", "oil", "biomass"}

def solve(demand_csv, capacity_csv, availability_csv, output_dir, links_csv=None, storage_csv=None):
    import pypsa
    demand = pd.read_csv(demand_csv)
    capacity = pd.read_csv(capacity_csv)
    avail = pd.read_csv(availability_csv)
    for name, df, fields in [
        ("demand", demand, {"timestamp", "ba", "demand_mw"}),
        ("capacity", capacity, {"ba", "technology", "capacity_mw", "marginal_cost"}),
        ("availability", avail, {"timestamp", "ba", "technology", "availability_pu"})]:
        if not fields.issubset(df):
            raise ValueError(f"{name} missing {sorted(fields - set(df))}")
        if df.empty or df[list(fields)].isna().any().any():
            raise ValueError(f"{name} contains empty/null input")
    if demand.duplicated(["timestamp", "ba"]).any() or capacity.duplicated(["ba", "technology"]).any() or avail.duplicated(["timestamp", "ba", "technology"]).any():
        raise ValueError("Duplicate demand, capacity, or availability keys")
    if not set(capacity.technology).issubset(DISPATCH_TECH):
        raise ValueError("Unsupported technology: storage requires SOC-aware modeling")
    for df in (demand, avail):
        df["timestamp"] = pd.to_datetime(df.timestamp, utc=True, errors="raise")
    times = pd.DatetimeIndex(sorted(demand.timestamp.unique()))
    if len(times) > 1 and not (times[1:] - times[:-1] == pd.Timedelta(hours=1)).all():
        raise ValueError("Demand timestamps not consecutive hours")
    bas = sorted(capacity.ba.unique())
    expected_d = pd.MultiIndex.from_product([times, bas], names=["timestamp", "ba"])
    if set(map(tuple, demand[["timestamp", "ba"]].itertuples(index=False, name=None))) != set(expected_d):
        raise ValueError("Incomplete demand BA-hour matrix")
    keys = list(capacity[["ba", "technology"]].itertuples(index=False, name=None))
    expected_a = {(t, ba, tech) for t in times for ba, tech in keys}
    actual_a = set(map(tuple, avail[["timestamp", "ba", "technology"]].itertuples(index=False, name=None)))
    if actual_a != expected_a:
        raise ValueError("Incomplete or extra technology availability matrix")
    for df, field, lower, upper in [
        (demand, "demand_mw", 0, None),
        (capacity, "capacity_mw", 0, None),
        (capacity, "marginal_cost", 0, None),
        (avail, "availability_pu", 0, 1)]:
        df[field] = pd.to_numeric(df[field], errors="raise")
        if not df[field].map(lambda x: float("-inf") < float(x) < float("inf")).all():
            raise ValueError(f"Nonfinite {field}")
        if (df[field] < lower).any() or (upper is not None and (df[field] > upper).any()):
            raise ValueError(f"Invalid {field} bounds")
    links = None
    if links_csv is not None:
        links = pd.read_csv(links_csv)
        required_links = {"from_ba", "to_ba", "capacity_mw"}
        if not required_links.issubset(links):
            raise ValueError("Link input missing required fields")
        if links[["from_ba", "to_ba", "capacity_mw"]].isna().any().any():
            raise ValueError("Null link fields")
        if (links.from_ba == links.to_ba).any():
            raise ValueError("Self-links not allowed")
        if not set(links.from_ba).union(links.to_ba).issubset(bas):
            raise ValueError("Link endpoint outside BA inventory")
        normalized = links.apply(
            lambda row: tuple(sorted((row.from_ba, row.to_ba))), axis=1
        )
        if normalized.duplicated().any():
            raise ValueError("Duplicate undirected BA links")
        links["capacity_mw"] = pd.to_numeric(links.capacity_mw, errors="raise")
        if not links.capacity_mw.map(lambda x: 0 <= float(x) < float("inf")).all():
            raise ValueError("Link capacity must be finite and nonnegative")
    storage = None
    if storage_csv is not None:
        storage = pd.read_csv(storage_csv)
        required_storage = {"ba", "power_mw", "energy_mwh", "efficiency_store",
                            "efficiency_dispatch", "initial_soc_fraction"}
        if not required_storage.issubset(storage):
            raise ValueError("Storage missing required columns")
        if storage.empty or storage[list(required_storage)].isna().any().any():
            raise ValueError("Empty or null storage configuration")
        if storage.ba.duplicated().any() or not set(storage.ba).issubset(bas):
            raise ValueError("Duplicate or unknown storage BA")
        for col in required_storage - {"ba"}:
            storage[col] = pd.to_numeric(storage[col], errors="raise")
            if not storage[col].map(lambda v: float("-inf") < float(v) < float("inf")).all():
                raise ValueError(f"Nonfinite storage {col}")
        if (storage[["power_mw", "energy_mwh"]] < 0).any().any():
            raise ValueError("Storage power and energy must be nonnegative")
        for col in ("efficiency_store", "efficiency_dispatch"):
            if not storage[col].between(0.000001, 1).all():
                raise ValueError(f"Storage {col} must be in (0, 1]")
        if not storage.initial_soc_fraction.between(0, 1).all():
            raise ValueError("Storage initial SOC fraction must be in [0, 1]")
    n = pypsa.Network()
    n.set_snapshots(times.tz_localize(None))
    for ba in bas:
        n.add("Bus", ba)
        series = demand[demand.ba == ba].set_index("timestamp").demand_mw.reindex(times)
        n.add("Load", f"{ba}_load", bus=ba, p_set=series.to_numpy())
        n.add("Generator", f"{ba}_shortfall", bus=ba, p_nom=1e8, marginal_cost=10000)
    for row in capacity.itertuples(index=False):
        profile = avail[(avail.ba == row.ba) & (avail.technology == row.technology)]
        profile = profile.set_index("timestamp").availability_pu.reindex(times)
        n.add("Generator", f"{row.ba}__{row.technology}", bus=row.ba,
              p_nom=float(row.capacity_mw), marginal_cost=float(row.marginal_cost),
              p_max_pu=profile.to_numpy())
    if storage is not None:
        for row in storage.itertuples(index=False):
            # Fixed installed power/energy with fixed initial SOC, no cyclic
            # artificial recharge. PyPSA StorageUnit couples consecutive hours.
            hours = float(row.energy_mwh) / float(row.power_mw) if row.power_mw > 0 else 0.
            if row.power_mw == 0 and row.energy_mwh != 0:
                raise ValueError("Zero storage power requires zero energy")
            n.add("StorageUnit", f"{row.ba}_battery", bus=row.ba,
                  p_nom=float(row.power_mw), max_hours=hours,
                  efficiency_store=float(row.efficiency_store),
                  efficiency_dispatch=float(row.efficiency_dispatch),
                  state_of_charge_initial=float(row.energy_mwh * row.initial_soc_fraction),
                  cyclic_state_of_charge=False, marginal_cost=0)
    if links is not None:
        for i, link in links.iterrows():
            # A transport Link represents a hypothetical bidirectional transfer
            # bound, NOT AC impedance-based line flow or verified physical rating.
            n.add("Link", f"transfer_{i}", bus0=link.from_ba, bus1=link.to_ba,
                  p_nom=float(link.capacity_mw), p_min_pu=-1, efficiency=1)
    status, condition = n.optimize(solver_name="highs")
    if (status, condition) != ("ok", "optimal"):
        raise RuntimeError(f"Optimization failed: {status}/{condition}")
    rows = []
    for row in capacity.itertuples(index=False):
        production = n.generators_t.p[f"{row.ba}__{row.technology}"]
        for time, mw in zip(times, production.to_numpy()):
            rows.append({"timestamp": time.isoformat(), "ba": row.ba,
                         "technology": row.technology, "generation_mwh": float(mw)})
    shortages = [{"ba": ba,
                  "unserved_energy_mwh": float(n.generators_t.p[f"{ba}_shortfall"].clip(lower=0).sum())}
                 for ba in bas]
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "generation_hourly.csv", index=False)
    pd.DataFrame(shortages).to_csv(out / "shortfall_by_ba.csv", index=False)
    if storage is not None:
        soc = n.storage_units_t.state_of_charge.copy()
        soc.index.name = "timestamp"
        soc.to_csv(out / "storage_soc_mwh.csv")
    return pd.DataFrame(shortages)

def main():
    p = argparse.ArgumentParser()
    for key in ("demand", "capacity", "availability", "output"):
        p.add_argument("--" + key, required=True)
    p.add_argument("--links", default=None)
    p.add_argument("--storage", default=None)
    a = p.parse_args()
    print(solve(a.demand, a.capacity, a.availability, a.output, links_csv=a.links, storage_csv=a.storage).to_string(index=False))

if __name__ == "__main__":
    main()
