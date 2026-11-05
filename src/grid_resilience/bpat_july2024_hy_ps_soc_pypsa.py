"""Contiguous 672h BPAT HY plus separate finite-energy pumped-storage scenario.

Original source demand/ERA5 and partial 2024 EIA860 gas+wind remain
unchanged. Nonstorage hydro is an *incremental hypothetical* BPAT
resource: one energy-limited Store with no replenishment across all 672
hours, plus one hourly MW-limited Link. PS initial and terminal SOC both zero; efficiency and MW/MWh are assumptions.
Not historical available hydro, observed outage/EENS or calibrated adequacy.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from grid_resilience.factorial_dispatch import SCENARIOS

BAS=("AZPS","BPAT","CISO","SRP")
SETTINGS=((0.,0.,1.),(500.,2000.,.80),(1000.,4000.,.80),(1000.,4000.,.90))
HY_POWER=2000.
HY_BUDGET=598947.6
T0=pd.Timestamp("2024-07-01T00:00:00Z")


def validate_source(demand,weather,capacity,hydro_scale):
    needed=((demand,{"timestamp","ba","demand_mw"}),
            (weather,{"timestamp","ba","temperature_c","wind_availability"}),
            (capacity,{"ba","gas_mw","wind_mw","capacity_source"}))
    for x,keys in needed:
        if not keys.issubset(x):
            raise ValueError(f"Missing original data fields: {keys-set(x.columns)}")
    d,w,c=demand.copy(),weather.copy(),capacity.copy()
    idx=pd.date_range(T0,periods=672,freq="h")
    for x in (d,w):
        x["timestamp"]=pd.to_datetime(x.timestamp,utc=True,errors="raise")
        if len(x)!=2688 or x.duplicated(["timestamp","ba"]).any() or set(x.ba)!=set(BAS):
            raise ValueError("Expected 672 source hours × 4 distinct BA")
        for ba,g in x.groupby("ba"):
            if not pd.DatetimeIndex(g.timestamp.sort_values()).equals(idx):
                raise ValueError("Noncontiguous correct source UTC calendar")
    if len(c)!=4 or c.ba.duplicated().any() or set(c.ba)!=set(BAS) or not c.capacity_source.astype(str).str.contains("GENERIC_THERMAL_PROXY").all():
        raise ValueError("Unverified/changed partial 2024 EIA860 fleet")
    for x,fields in ((d,["demand_mw"]),(w,["temperature_c","wind_availability"]),(c,["gas_mw","wind_mw"])):
        for field in fields:
            x[field]=pd.to_numeric(x[field],errors="coerce")
            if not np.isfinite(x[field]).all():
                raise ValueError(f"Missing original {field}")
    if (d.demand_mw<0).any() or (c[["gas_mw","wind_mw"]]<0).any().any() or not w.wind_availability.between(0,1).all():
        raise ValueError("Invalid original source physical domain")
    if not np.isfinite(hydro_scale) or not np.isclose(hydro_scale,5989476.,rtol=0,atol=.01):
        raise ValueError("Expected independently verified EIA923 July 2024 BPAT HY Page1 monthly scale")
    return d,w,c,idx


def run(demand,weather,capacity,hydro_scale,output):
    import pypsa
    d,w,c,times=validate_source(demand,weather,capacity,hydro_scale)
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    loads=d.set_index(["timestamp","ba"]).demand_mw
    climate=w.set_index(["timestamp","ba"])
    fleet=c.set_index("ba")
    records=[]
    hourly=[]
    resource=[]
    for ps_power,ps_energy,ps_roundtrip in SETTINGS:
        if HY_BUDGET>hydro_scale:
            raise ValueError("Observed EIA923 reference scale mismatch")
        label=f"PS_{int(ps_power)}MW_{int(ps_energy)}MWh_eta{int(ps_roundtrip*100)}"
        for scenario,(heat,wind_penalty) in SCENARIOS.items():
            n=pypsa.Network()
            n.set_snapshots(times.tz_localize(None))
            for ba in BAS:
                s=climate.xs(ba,level="ba").reindex(times)
                x=loads.xs(ba,level="ba").reindex(times)
                extra=(s.temperature_c.add(heat).sub(30).clip(lower=0)-
                       s.temperature_c.sub(30).clip(lower=0))*.012
                n.add("Bus",ba)
                n.add("Load",f"{ba}_load",bus=ba,
                      p_set=(x*(1+extra)).to_numpy(float))
                n.add("Generator",f"{ba}_gas",bus=ba,
                      p_nom=float(fleet.loc[ba,"gas_mw"]),marginal_cost=70)
                n.add("Generator",f"{ba}_wind",bus=ba,
                      p_nom=float(fleet.loc[ba,"wind_mw"]),
                      p_max_pu=(s.wind_availability*(1-wind_penalty)).to_numpy(float),
                      marginal_cost=0)
                n.add("Generator",f"{ba}_unserved",bus=ba,
                      p_nom=1e8,marginal_cost=10000)
            if HY_POWER>0:
                n.add("Bus","BPAT_HY_WATER_ENERGY")
                n.add("Store","BPAT_HY_28DAY_BUDGET",
                      bus="BPAT_HY_WATER_ENERGY",e_nom=float(HY_BUDGET),
                      e_initial=float(HY_BUDGET),e_cyclic=False)
                n.add("Link","BPAT_HY_POWER",
                      bus0="BPAT_HY_WATER_ENERGY",bus1="BPAT",
                      p_nom=float(HY_POWER),efficiency=1)
            if ps_power>0:
                from math import sqrt
                eta=sqrt(ps_roundtrip)
                n.add("Bus","BPAT_PS_RESERVOIR")
                terminal_max=np.ones(len(times))
                terminal_max[-1]=0.
                n.add("Store","BPAT_PS_SOC",bus="BPAT_PS_RESERVOIR",
                      e_nom=float(ps_energy),e_initial=0.,e_cyclic=False,
                      e_min_pu=0.,e_max_pu=terminal_max)
                n.add("Link","BPAT_PS_CHARGE",bus0="BPAT",bus1="BPAT_PS_RESERVOIR",
                      p_nom=float(ps_power),efficiency=eta)
                n.add("Link","BPAT_PS_DISCHARGE",bus0="BPAT_PS_RESERVOIR",bus1="BPAT",
                      p_nom=float(ps_power)/eta,efficiency=eta)
            status,condition=n.optimize(solver_name="highs")
            if (status,condition)!=("ok","optimal"):
                raise RuntimeError(f"Nonoptimal hydro source study: {label} {scenario}: {status}/{condition}")
            hydro=np.maximum(n.links_t.p0["BPAT_HY_POWER"].to_numpy(float),0)
            if hydro.max()>HY_POWER+.02 or hydro.sum()>HY_BUDGET+.1:
                raise ValueError("Hydro power or total 28-day energy limit violated")
            if HY_POWER>0:
                energy=n.stores_t.e["BPAT_HY_28DAY_BUDGET"].to_numpy(float)
                if np.min(energy)<-.1 or np.max(energy)>HY_BUDGET+.1:
                    raise ValueError("Hydro intertemporal stored energy balance invalid")
                if not np.allclose(np.diff(np.r_[HY_BUDGET,energy]),-hydro,atol=.1):
                    raise ValueError("Hydro depletion does not reconcile with discharged energy")
            if ps_power>0:
                eta=np.sqrt(ps_roundtrip)
                ps_charge=np.maximum(n.links_t.p0["BPAT_PS_CHARGE"].to_numpy(float),0)
                ps_input=np.maximum(n.links_t.p0["BPAT_PS_DISCHARGE"].to_numpy(float),0)
                ps_out=np.maximum(-n.links_t.p1["BPAT_PS_DISCHARGE"].to_numpy(float),0)
                ps_soc=n.stores_t.e["BPAT_PS_SOC"].to_numpy(float)
                if (ps_charge.max()>ps_power+.1 or ps_out.max()>ps_power+.1 or
                    np.min(ps_soc)<-.1 or np.max(ps_soc)>ps_energy+.1 or abs(ps_soc[-1])>.1):
                    raise ValueError("PS power, stored energy or terminal SOC invalid")
                if not np.allclose(np.diff(np.r_[0.,ps_soc]),
                                   eta*ps_charge-ps_input,atol=.1):
                    raise ValueError("PS Store hourly SOC conservation violated")
                if not np.allclose(ps_out,eta*ps_input,atol=.1):
                    raise ValueError("PS discharge efficiency violated")
                if not np.isclose(ps_out.sum(),ps_charge.sum()*ps_roundtrip,atol=.1):
                    raise ValueError("PS closed-cycle roundtrip energy accounting violated")
            else:
                ps_charge=np.zeros(len(times))
                ps_out=np.zeros(len(times))
                ps_soc=np.zeros(len(times))
            for ba in BAS:
                shed=n.generators_t.p[f"{ba}_unserved"].clip(lower=0).to_numpy(float)
                for wk in range(4):
                    hours=slice(168*wk,168*(wk+1))
                    records.append({
                        "resource_scenario":label,"scenario":scenario,"week":wk+1,"ba":ba,
                        "modeled_unserved_mwh":float(shed[hours].sum()),
                        "hydro_power_assumption_mw":HY_POWER,
                        "hydro_energy_budget_assumption_28d_mwh":HY_BUDGET,
                        "ps_power_assumed_mw":ps_power,"ps_energy_assumed_mwh":ps_energy,
                        "ps_roundtrip_assumed":ps_roundtrip})
            for wk in range(4):
                hours=slice(168*wk,168*(wk+1))
                resource.append({"resource_scenario":label,"scenario":scenario,"week":wk+1,
                    "hydro_dispatched_mwh":float(hydro[hours].sum()),
                    "hydro_peak_dispatch_mw":float(hydro[hours].max()),
                    "ps_charging_mwh":float(ps_charge[hours].sum()),
                    "ps_discharge_delivered_mwh":float(ps_out[hours].sum()),
                    "ps_end_of_week_soc_mwh":float(ps_soc[hours.stop-1])})
            hourly.extend({"resource_scenario":label,"scenario":scenario,
                           "timestamp":times[i].isoformat(),
                           "hydro_optimized_mw":float(hydro[i]),
                           "ps_charge_mw":float(ps_charge[i]),
                           "ps_discharge_delivered_mw":float(ps_out[i]),
                           "ps_soc_mwh":float(ps_soc[i])}
                          for i in range(len(times)))
    f=pd.DataFrame(records)
    h=pd.DataFrame(hourly)
    z=pd.DataFrame(resource)
    if len(f)!=len(SETTINGS)*4*4*4 or len(h)!=len(SETTINGS)*4*672:
        raise ValueError("Incomplete source by scenario outputs")
    control=f.loc[f.resource_scenario.eq("PS_0MW_0MWh_eta100")&f.scenario.eq("baseline")]
    if len(control)!=16:
        raise ValueError("Missing 4-week original hydro-free controls")
    for label in f.resource_scenario.unique():
        g=f.loc[f.resource_scenario.eq(label)]
        for case in SCENARIOS:
            q=g.loc[g.scenario.eq(case)]
            if len(q)!=16:
                raise ValueError("Incomplete 4-BA four-week factorial")
        if z.loc[z.resource_scenario.eq(label)].groupby("scenario").hydro_dispatched_mwh.sum().gt(
            HY_BUDGET+.1).any():
            raise ValueError("28-day hydro budget reset incorrectly")
    f.to_csv(output/"july_2024_672h_bpat_hy_ps_factorial_by_ba_week.csv",index=False)
    z.to_csv(output/"july_2024_672h_hy_ps_by_week.csv",index=False)
    h.to_csv(output/"july_2024_672h_hy_ps_hourly.csv",index=False)
    summary=(f.groupby(["resource_scenario","scenario"],as_index=False)
             .agg(total_model_shortage_mwh=("modeled_unserved_mwh","sum")))
    summary.to_csv(output/"july_2024_672h_hy_ps_factorial_system.csv",index=False)
    manifest={"source_original_2024_july_four_week_run":42104106361,
              "source_july2024_eia923_hy_page1_net_mwh":hydro_scale,
              "model_hours_single_contiguous_horizon":672,
              "model_weeks":4,
              "source_ba_count":4,
              "model_optimization_scenarios":len(SETTINGS)*4,
              "isolated_only_no_hypothetical_interties":True,
              "supply_base_unchanged_2024_eia860_partial_gas_wind":True,
              "hydro_capacity_all_assumed_not_verified_eia860":True,
              "noncyclic_store_one_28day_budget":True,
              "budget_from_measured_net_mwh_is_assumed_not_measured_water_availability":True,
              "pumped_storage_separate_closed_zero_soc":True,
              "ps_power_energy_efficiencies_only_assumptions":True,
              "physical_ps_eia860_ba_roster_verified":False,
              "source_hydro_hourly_generation_not_known":True,
              "historically_calibrated_capacity_or_outage_or_eens":False}
    (output/"july_2024_672h_hy_ps_scope.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("REAL SOURCE ANCHORED CONTIGUOUS 672H HY PYPSA OPTIMIZATION")
    print(summary.to_string(index=False))
    print("HY BY WEEK")
    print(z.to_string(index=False))
    return f,summary,manifest


def main():
    p=argparse.ArgumentParser()
    for x in ("demand","weather","capacity","source-scope","output"):
        p.add_argument("--"+x,required=True)
    a=p.parse_args()
    scope=pd.read_csv(a.source_scope)
    if len(scope)!=1:
        raise ValueError("Missing only-one BPAT July HY source record")
    run(pd.read_csv(a.demand),pd.read_csv(a.weather),pd.read_csv(a.capacity),
        float(scope.iloc[0].eia923_observed_hy_mwh),a.output)


if __name__=="__main__":
    main()
