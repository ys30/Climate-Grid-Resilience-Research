"""BPAT July 2024: non-calibrated HY power × energy optimistic bounds.

The observed EIA923 Page1 monthly HY *net production* is only a
reference scale, NOT available reservoir energy, hourly hydro output,
firm capacity or verified BPAT operational dispatch. This module does
NOT modify the original PyPSA model. It tests what could possibly be
mitigated in the existing isolated BPAT shortage if an expressly
hypothetical additional nonstorage hydro resource had both a power
ceiling (MW) and one shared 28-day energy allocation ceiling (MWh).
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

POWER_MW=(500.,2000.,5000.,10000.)
ENERGY_FRACTIONS=(0.10,0.25,0.50,1.00)

def audit(hydro_month,original_solutions,monthly_reference,weekly_coverage):
    needed={"reported_ba","prime_mover","period","net_generation_mwh","coverage_status"}
    if not needed.issubset(hydro_month):
        raise ValueError("Missing EIA923 source HY monthly fields")
    source=hydro_month.loc[
       hydro_month.reported_ba.eq("BPAT")&
       hydro_month.prime_mover.eq("HY")&
       hydro_month.period.eq("2024-07")]
    if len(source)!=1 or source.iloc[0].coverage_status!="observed_source_rows":
        raise ValueError("Real July conventional HY source missing or duplicated")
    hy_mwh=float(source.iloc[0].net_generation_mwh)
    if not np.isfinite(hy_mwh) or hy_mwh<=0:
        raise ValueError("Invalid observed monthly HY scale reference")
    reference=monthly_reference.copy()
    if len(reference)!=1 or reference.iloc[0]["official_eia930_complete_july_hour_count"]!=744:
        raise ValueError("Missing source-verified full EIA930 July observational scope")
    if not np.isclose(hy_mwh,float(reference.iloc[0]["eia923_observed_hy_mwh"]),atol=1e-8,rtol=0):
        raise ValueError("Conflicting original EIA923 monthly HY evidence")
    if bool(reference.iloc[0]["source_reporting_grains_equivalent_certified"]):
        raise ValueError("Unjustified EIA923-EIA930 reported BA equivalence")
    if not {"event_id","network_variant","scenario","ba","unserved_energy_mwh"}.issubset(original_solutions):
        raise ValueError("Missing real-source PyPSA scenario outcomes")
    s=original_solutions.loc[
        original_solutions.ba.eq("BPAT")&
        original_solutions.scenario.eq("baseline")&
        original_solutions.network_variant.eq("isolated")].copy()
    s["week"]=pd.to_numeric(s.event_id.astype(str).str.extract(r"WEEK_(\d+)")[0],errors="coerce")
    if len(s)!=4 or s.week.isna().any() or set(s.week)!={1,2,3,4} or s.week.duplicated().any():
        raise ValueError("Missing real four-week isolated BPAT baseline")
    s["unserved_energy_mwh"]=pd.to_numeric(s.unserved_energy_mwh,errors="coerce")
    if not np.isfinite(s.unserved_energy_mwh).all() or s.unserved_energy_mwh.lt(-1e-6).any():
        raise ValueError("Invalid archived PyPSA scenario shortage")
    if not {"week","distinct_hours"}.issubset(weekly_coverage):
        raise ValueError("Missing original four-week source coverage")
    w=weekly_coverage.copy()
    if len(w)!=4 or set(w.week)!={1,2,3,4} or w.week.duplicated().any() or not w.distinct_hours.eq(168).all():
        raise ValueError("Four verified nonoverlapping 168h source windows required")
    s=s.merge(w[["week","distinct_hours"]],on="week",validate="one_to_one")
    total_shortfall=float(s.unserved_energy_mwh.sum())
    rows=[]
    for power in POWER_MW:
        for fraction in ENERGY_FRACTIONS:
            energy=hy_mwh*fraction
            # These ceilings are necessary but NOT sufficient for feasible
            # dispatch. In particular hydro cannot necessarily serve all
            # BA demand in the matching hours and we do not model water flow.
            max_possible=min(total_shortfall,power*672.,energy)
            remaining_floor=max(0.,total_shortfall-max_possible)
            row={"hypothetical_incremental_hydro_power_mw":power,
                 "assumed_fraction_of_2024_july_observed_hy_mwh":fraction,
                 "assumed_28day_hydro_energy_budget_mwh":energy,
                 "existing_isolated_partial_model_baseline_shortage_mwh":total_shortfall,
                 "optimistic_total_shortfall_mitigation_ceiling_mwh":max_possible,
                 "residual_original_model_shortage_floor_mwh":remaining_floor,
                 "hourly_power_capacity_28day_ceiling_mwh":power*672.,
                 "limiting_ceiling":("current_shortage" if max_possible==total_shortfall else
                                    "power" if max_possible==power*672. else "energy"),
                 "actual_source_measured_monthly_generation_is_available_energy":False,
                 "physically_feasible_hydro_dispatch_inferred":False}
            rows.append(row)
    out=pd.DataFrame(rows)
    if len(out)!=16:
        raise ValueError("Wrong hypothetical power-energy grid size")
    if out.residual_original_model_shortage_floor_mwh.lt(-1e-9).any():
        raise ValueError("Nonphysical mathematically calculated residual")
    meta={
       "reference_eia923_run":41263007401,
       "source_2024_july_eia923_hy_reported_net_mwh":hy_mwh,
       "comparison_existing_pypsa_fourweek_run":42104106361,
       "source_month_days":31,"model_overlap_days":28,
       "actual_source_hours_modelled":672,"eia923_monthly_source_is_not_hourly":True,
       "monthly_observed_net_generation_not_a_physical_water_budget":True,
       "all_power_points_hypothetical_not_eia860_nameplate":True,
       "hypothetical_power_points_mw":list(POWER_MW),
       "hypothetical_energy_fractions":list(ENERGY_FRACTIONS),
       "existing_model_isolated_baseline_shortage_only":True,
       "optimistic_bounds_not_feasible_generation_or_solver_results":True,
       "candidate_ba_demand_coverage_verified_from_prior_workflow":True,
       "PS_assumed_absent_separate_SOC_constraints_not_inferred":True,
       "cross_ba_transmission_rating_calibration":False,
       "historical_eens_or_real_outage_inference":False}
    return out,meta


def main():
    parser=argparse.ArgumentParser()
    for x in ("eia923-month","pypsa-scenarios","hydro-source-scope","weekly-coverage","output"):
        parser.add_argument("--"+x,required=True)
    a=parser.parse_args()
    out,meta=audit(pd.read_csv(a.eia923_month),
        pd.read_csv(a.pypsa_scenarios),
        pd.read_csv(a.hydro_source_scope),
        pd.read_csv(a.weekly_coverage))
    path=Path(a.output);path.mkdir(parents=True,exist_ok=True)
    out.to_csv(path/"bpat_july_2024_hypothetical_hydro_power_energy_optimistic_bound.csv",index=False)
    (path/"bpat_july_2024_hydro_envelope_scope_manifest.json").write_text(
       json.dumps(meta,indent=2)+"\n")
    print("BPAT FOUR-WEEK HYDRO NECESSARY-CONDITION BOUNDS; NOT PYPSA DISPATCH")
    print(out.to_string(index=False))
    print(json.dumps(meta,indent=2))

if __name__=="__main__":
    main()
