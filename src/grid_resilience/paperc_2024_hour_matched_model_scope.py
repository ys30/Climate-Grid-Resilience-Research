"""Supplementary model-scope contrast, never an empirical dispatch validation.

Source-observed 2024 EIA-930 BA natural-gas MW is NOT the same plant population
as the hypothetical partial-fleet generic_thermal_proxy dispatch. Metrics are
descriptive mismatch diagnostics, not forecast skill, adequacy or unit calibration.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

BAS={"AZPS","BPAT","CISO","SRP"}


def audit(observed, modeled):
    need_obs={"timestamp","ba","partition","net_mwh","gas_mwh"}
    need_model={"timestamp","ba","scenario","technology","generation_mwh"}
    if not need_obs.issubset(observed) or not need_model.issubset(modeled):
        raise ValueError("Missing observed fuel or model dispatch audit columns")
    o=observed[list(need_obs)].copy()
    o["timestamp"]=pd.to_datetime(o.timestamp,utc=True,errors="raise")
    if len(o)!=672 or o.duplicated(["timestamp","ba"]).any() or set(o.ba)!=BAS:
        raise ValueError("Source BA-hour mismatch")
    t=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    if not pd.DatetimeIndex(sorted(o.timestamp.unique())).equals(t):
        raise ValueError("Source UTC 168-hour calendar mismatch")
    o["gas_mwh"]=pd.to_numeric(o.gas_mwh,errors="coerce")
    o["net_mwh"]=pd.to_numeric(o.net_mwh,errors="coerce")
    if not np.isfinite(o[["gas_mwh","net_mwh"]].to_numpy(float)).all():
        raise ValueError("Missing source-observed natural gas/net generation")
    for ba,g in o.groupby("ba"):
        if g.partition.value_counts().to_dict()!={"2024_Jan_Jun":7,"2024_Jul_Dec":161}:
            raise ValueError("Source partition not independently reconciled")
    m=modeled.loc[modeled.scenario.eq("baseline") &
                  modeled.technology.eq("generic_thermal_proxy")].copy()
    m["timestamp"]=pd.to_datetime(m.timestamp,utc=True,errors="raise")
    if len(m)!=672 or m.duplicated(["timestamp","ba"]).any() or set(m.ba)!=BAS:
        raise ValueError("Model 672 BA-hour proxy records incomplete")
    m["generation_mwh"]=pd.to_numeric(m.generation_mwh,errors="coerce")
    if not np.isfinite(m.generation_mwh.to_numpy(float)).all() or m.generation_mwh.lt(-1e-5).any():
        raise ValueError("Invalid generic model generator output")
    j=o.merge(m[["timestamp","ba","generation_mwh"]],on=["timestamp","ba"],
              how="inner",validate="one_to_one")
    if len(j)!=672:raise ValueError("Observed and model BA-hour keys do not match")
    j=j.rename(columns={"gas_mwh":"eia930_raw_reported_natural_gas_mwh",
                        "generation_mwh":"hypothetical_generic_thermal_proxy_mwh"})
    j["signed_proxy_minus_gas_mwh"]=(
        j.hypothetical_generic_thermal_proxy_mwh-j.eia930_raw_reported_natural_gas_mwh)
    rows=[]
    for ba,g in j.groupby("ba",sort=True):
        err=g.signed_proxy_minus_gas_mwh
        rows.append({"ba":ba,"period":"2024-07-01/07 UTC","matched_hours":len(g),
                     "eia930_raw_ba_natural_gas_mwh":float(g.eia930_raw_reported_natural_gas_mwh.sum()),
                     "eia930_raw_ba_total_net_generation_mwh":float(g.net_mwh.sum()),
                     "model_generic_thermal_proxy_baseline_mwh":
                         float(g.hypothetical_generic_thermal_proxy_mwh.sum()),
                     "descriptive_signed_proxy_minus_gas_mwh":float(err.sum()),
                     "descriptive_absolute_hourly_mismatch_mwh":float(err.abs().sum()),
                     "population_and_technology_equivalence_verified":False,
                     "hourly_plant_dispatch_calibrated":False,
                     "historical_eens_calibrated":False})
    return j,pd.DataFrame(rows)


def main():
    p=argparse.ArgumentParser()
    for x in ("observed","model","output"):p.add_argument("--"+x,required=True)
    args=p.parse_args()
    detail,summary=audit(pd.read_csv(args.observed),pd.read_csv(args.model))
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    detail.to_csv(out/"source_hour_matched_non_equivalent_gas_thermal_diagnostic.csv",index=False)
    summary.to_csv(out/"source_hour_matched_non_equivalent_gas_thermal_by_ba.csv",index=False)
    scope={"matched_ba_hours":len(detail),"each_ba_hours":168,
           "source_observation":"EIA930 original BA natural gas generation, two official 2024 partitions",
           "model_comparison":"PyPSA generic_thermal_proxy, baseline, partial generator representation",
           "generator_population_equivalent":False,"predictive_accuracy_metric_claimed":False,
           "historical_shortage_or_eens_inferred":False}
    (out/"model_vs_observed_fuel_scope_not_equivalent.json").write_text(
        json.dumps(scope,indent=2)+"\n")
    print(summary.to_string(index=False))


if __name__=="__main__":main()
