"""Prepare explicit, uncalibrated CISO PyPSA storage sensitivity from observed power scale.

Source observational percentiles are NOT generator nameplate or certified
deliverable physical power. A symmetric StorageUnit scenario uses the smaller
of positive discharge/charge empirical quantiles; duration, initial SOC,
per-direction efficiencies and BA dispatch are purely counterfactual.
No historical adequacy/EENS claim follows from the scenario CSV.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

SCOPE=("total","standalone")
QUANTILES=(95,99)
DURATIONS=(2.,4.)
INITIAL_SOC=(.25,.75)
EFFICIENCY=0.90
YEAR=(2023,2024)


def scenario_matrix(source):
    required={"year","series","source_points",
        "certified_storage_power_rating_mw_inferred",
        "matched_battery_soc_mwh_inferred"}
    for n in QUANTILES:
        required.update({
            f"discharge_positive_only_p{n}_mw",
            f"charge_positive_magnitude_only_p{n}_mw",
        })
    if not required.issubset(source):
        raise ValueError("Missing source-audited empirical power distribution")
    if source.duplicated(["year","series"]).any():
        raise ValueError("Repeated original source envelope key")
    if source.certified_storage_power_rating_mw_inferred.any() or (
        source.matched_battery_soc_mwh_inferred.any()
    ):
        raise ValueError("Unjustified physical storage rating or SOC claim")
    if set(source.year)!={2023,2024} or not set(SCOPE).issubset(set(source.series)):
        raise ValueError("Missing original year / resource cohort")
    configs=[]
    for year in YEAR:
        for scope in SCOPE:
            row=source[(source.year==year)&source.series.eq(scope)].iloc[0]
            if row.source_points!=2016:
                raise ValueError("Incomplete original five-minute source window")
            for q in QUANTILES:
                discharge=float(getattr(row,f"discharge_positive_only_p{q}_mw"))
                charge=float(getattr(row,f"charge_positive_magnitude_only_p{q}_mw"))
                if not np.isfinite([discharge,charge]).all() or min(discharge,charge)<=0:
                    raise ValueError("Invalid source nonzero empirical charging/discharging quantile")
                # PyPSA StorageUnit assumes symmetric power: scale both directions
                # down to weaker of the observed empirical charge/discharge quantiles.
                symmetric=min(discharge,charge)
                for hours in DURATIONS:
                    for soc in INITIAL_SOC:
                        label=f"Y{year}_{scope}_p{q}_{int(hours)}h_soc{int(soc*100)}"
                        configs.append({
                            "scenario_id":label,
                            "observed_source_data_year":year,
                            "source_series":scope,
                            "observed_percentile_positive_only":q,
                            "observed_discharge_percentile_mw":discharge,
                            "observed_charge_percentile_mw":charge,
                            "ba":"CISO",
                            "power_mw":symmetric,
                            "energy_mwh":symmetric*hours,
                            "efficiency_store":EFFICIENCY,
                            "efficiency_dispatch":EFFICIENCY,
                            "initial_soc_fraction":soc,
                            "assumed_storage_duration_h":hours,
                            "observed_quantile_is_not_technical_power_rating":True,
                            "energy_mwh_assumed_not_source_measured":True,
                            "initial_soc_and_efficiency_counterfactual":True,
                            "historical_dispatch_reconstructed":False,
                            "observed_EENS_inferred":False,
                        })
    scenarios=pd.DataFrame(configs)
    if len(scenarios)!=32 or scenarios.scenario_id.duplicated().any():
        raise ValueError("Counterfactual scenario Cartesian product incomplete")
    assert scenarios.energy_mwh.gt(0).all()
    return scenarios


def save(source,out):
    path=Path(out)
    path.mkdir(parents=True,exist_ok=True)
    table=scenario_matrix(source)
    table.to_csv(path/"paper_c_ciso_battery_counterfactual_storageunit_matrix.csv",index=False)
    for row in table.itertuples(index=False):
        folder=path/"storageunit_csv"
        folder.mkdir(exist_ok=True)
        pd.DataFrame([{"ba":"CISO","power_mw":row.power_mw,
                       "energy_mwh":row.energy_mwh,
                       "efficiency_store":row.efficiency_store,
                       "efficiency_dispatch":row.efficiency_dispatch,
                       "initial_soc_fraction":row.initial_soc_fraction}]
                     ).to_csv(folder/(row.scenario_id+".csv"),index=False)
    manifest={"source_bas":["CISO"],
        "input_generator":"paperc_caiso_battery_observed_envelope.py",
        "scenario_count":len(table),"source_q":[95,99],
        "assumed_storage_duration_hours":[2,4],
        "assumed_initial_soc_fraction":[.25,.75],
        "assumed_per_direction_efficiency":EFFICIENCY,
        "source_quantile_used_only_as_hypothetical_symmetric_power_scale":True,
        "not_measured_plant_nameplate_or_usable_energy":True,
        "current_partial_fleet_pypsa_not_physically_calibrated":True,
        "no_historical_unserved_energy_or_EENS_claim":True}
    (path/"paper_c_ciso_battery_counterfactual_scenario_scope.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print("CISO BATTERY EXPLICIT COUNTERFACTUALS",
          table.groupby(["observed_source_data_year","source_series",
                         "observed_percentile_positive_only"]).power_mw.first().to_string())
    return table


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    save(pd.read_csv(a.source),a.output)


if __name__=="__main__":
    main()
