"""Independent daily-source reconciliation of USACE pumping and USBR/USGS lake levels.

Same calendar days, independent observation clocks and physical reporting
scope. USACE Banks Pump MWh is entire irrigation/pumping project; NOT
electric pumping of six 314MW reversible PS generators alone.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from grid_resilience.grand_coulee_pumping_scope_gate import pumping_scope_diagnostic

def audit(usace,banks,roosevelt):
    required={
      "usace":{"date","usace_banks_lake_pumping_electricity_mwh",
               "usace_banks_lake_pump_flow_kcfs",
               "usace_banks_lake_reported_elev_ft",
               "usace_roosevelt_midnight_elev_ft"},
      "banks":{"date","elevation_ft"},
      "roosevelt":{"date","lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29"}}
    for name,x in (("usace",usace),("banks",banks),("roosevelt",roosevelt)):
        if not required[name].issubset(x):
            raise ValueError(f"Source {name} missing observed fields")
        x["date"]=pd.to_datetime(x.date,errors="raise")
        target=pd.date_range("2024-07-01",periods=31,freq="D")
        if len(x)!=31 or x.date.duplicated().any() or not pd.DatetimeIndex(x.date.sort_values()).equals(target):
            raise ValueError(f"Observed {name} has missing/duplicate 2024 July days")
    w=usace.copy()
    w=w.merge(banks[["date","elevation_ft"]],on="date",validate="one_to_one")
    w=w.merge(roosevelt[["date","lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29"]],
             on="date",validate="one_to_one")
    numeric=[x for x in required["usace"] if x!="date"]+[
        "elevation_ft","lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29"]
    for f in numeric:
        w[f]=pd.to_numeric(w[f],errors="coerce")
        if not np.isfinite(w[f].to_numpy(float)).all():
            raise ValueError(f"Original reported {f} contains missing observed records")
    if w.usace_banks_lake_pumping_electricity_mwh.lt(0).any() or w.usace_banks_lake_pump_flow_kcfs.lt(0).any():
        raise ValueError("Negative original reported pump electricity or water duty")
    w["usace_banks_minus_usbr_banks_ft"]=w.usace_banks_lake_reported_elev_ft-w.elevation_ft
    w["usace_roosevelt_minus_usgs_roosevelt_ft"]=w.usace_roosevelt_midnight_elev_ft-w.lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29
    w["in_672h_pypsa_original_july_window"]=w.date.le(pd.Timestamp("2024-07-28"))
    total=float(w.usace_banks_lake_pumping_electricity_mwh.sum())
    first=float(w.loc[w.in_672h_pypsa_original_july_window,"usace_banks_lake_pumping_electricity_mwh"].sum())
    last=float(w.loc[~w.in_672h_pypsa_original_july_window,"usace_banks_lake_pumping_electricity_mwh"].sum())
    if abs(total-175641)>1e-6 or abs(first+last-total)>1e-6:
        raise ValueError("Original July project-wide USACE pump MWh checksum disagrees")
    scope = pumping_scope_diagnostic(w.usace_banks_lake_pumping_electricity_mwh.tolist(), 314.0)
    report={
      "actual_USACE_Banks_pumping_July_2024_complete_31days_MWh":total,
      "actual_USACE_Banks_pumping_July_1_28_2024_28day_MWh":first,
      "actual_USACE_Banks_pumping_July_29_31_2024_3day_MWh":last,
      "actual_USACE_pumping_July_daily_peak_MWh":float(w.usace_banks_lake_pumping_electricity_mwh.max()),
      "observed_project_pumping_complete_days":31,
      "paired_independent_reservoir_observation_days":len(w),
      "USACE_vs_USBR_Banks_max_abs_same_date_ft":float(w.usace_banks_minus_usbr_banks_ft.abs().max()),
      "USACE_vs_USGS_Roosevelt_max_abs_same_date_ft":float(w.usace_roosevelt_minus_usgs_roosevelt_ft.abs().max()),
      "upper_and_lower_site_daily_time_definitions_not_proven_identical":True,
      "USACE_pump_MWh_is_whole_Banks_irrigation_site_not_PG7_PG12_only":True,
      "six_PS_EIA860_nameplate_314MW_is_generator_not_observed_pump_rating":True,
      "observed_daily_site_pump_MWh_is_energy_available_for_PS_discharge":False,
      "USACE_pumping_kcfs_aggregation_and_total_water_volume_not_inferred":True,
      "USACE_pump_project_consumption_is_not_EIA923_signed_PS_net_generation":True,
      "usable_electric_PS_MWh_or_reservoir_water_balance_calibrated":False,
      "real_historical_grid_outages_or_EENS_identified":False,
      "hypothetical_314mw_ps_scope_diagnostic":scope}
    return w,report

def main():
    a=argparse.ArgumentParser()
    for n in ("usace","banks","roosevelt","output"):a.add_argument("--"+n,required=True)
    x=a.parse_args()
    w,m=audit(pd.read_csv(x.usace),pd.read_csv(x.banks),pd.read_csv(x.roosevelt))
    p=Path(x.output);p.mkdir(parents=True,exist_ok=True)
    w.to_csv(p/"grand_coulee_2024_july_31day_usace_usbr_usgs_pumping_lake_observation_reconciliation.csv",index=False)
    (p/"grand_coulee_2024_july_pumping_hydro_source_scope_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print("REAL 2024 GRAND COULEE PUMPING 31 DAYS WITH 28 DAY MODEL COHORT SOURCE RECONCILED")
    print(json.dumps(m,indent=2))
if __name__=="__main__":main()
