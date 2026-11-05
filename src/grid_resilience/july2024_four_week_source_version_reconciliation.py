"""Source reconciliation for old and newly refetched first-week 4-BA factorial.

The two model runs must not be called exact reproductions unless the original
demand/weather/capacity inputs and shock/network assumptions are identical.
Compare BA-hour keys and unrounded input values and publish mismatches.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

BAS={"AZPS","BPAT","CISO","SRP"}


def compare(old,new,fields,name):
    keys=["timestamp","ba"]
    if not set(keys+fields).issubset(old) or not set(keys+fields).issubset(new):
        raise ValueError("Source reconciliation schema missing")
    a,b=old.copy(),new.copy()
    for g in (a,b):
        g["timestamp"]=pd.to_datetime(g.timestamp,utc=True,errors="raise")
        if g.duplicated(keys).any():
            raise ValueError("Duplicated BA hour in input source")
    if len(a)!=len(b) or len(a)!=4*168 or set(a.ba)!=BAS or set(b.ba)!=BAS:
        raise ValueError("Unexpected first-week source window size or BA set")
    merged=a.merge(b,on=keys,how="outer",indicator=True,
                   suffixes=("_original","_refetched"),validate="one_to_one")
    if not merged._merge.eq("both").all():
        raise ValueError("Different first-week original and refreshed source timestamp keys")
    records=[]
    for ba,g in merged.groupby("ba",sort=True):
        for field in fields:
            previous=pd.to_numeric(g[field+"_original"],errors="coerce")
            current=pd.to_numeric(g[field+"_refetched"],errors="coerce")
            if not np.isfinite(previous.to_numpy(float)).all() or not np.isfinite(current.to_numpy(float)).all():
                raise ValueError("Nonfinite value in source comparison")
            delta=current-previous
            changed=~np.isclose(previous,current,rtol=0,atol=1e-8)
            records.append({
                "source_type":name,"ba":ba,"field":field,
                "utc_source_hours_compared":len(g),
                "values_differing_above_1e8_tolerance":int(changed.sum()),
                "max_absolute_change":float(delta.abs().max()),
                "mean_signed_change":float(delta.mean()),
                "original_mean":float(previous.mean()),
                "refetched_mean":float(current.mean()),
                "source_values_identical":bool(not changed.any())
            })
    out=pd.DataFrame(records)
    if len(out)!=4*len(fields):
        raise ValueError("Missing original-source reconciliation results")
    return out


def audit(old_demand,new_demand,old_weather,new_weather):
    r=pd.concat([
        compare(old_demand,new_demand,["demand_mw"],"EIA930_demand"),
        compare(old_weather,new_weather,["temperature_c","wind_availability"],
                "ERA5_site_weather_and_assumed_wind_proxy")
    ],ignore_index=True)
    m={
      "source_comparison":"original archived 168-hour July 2024 four BA inputs versus independently refreshed 28-day 2024 July first 168 hours",
      "source_hour_keys_identical":True,
      "all_numeric_source_values_identical":bool(r.source_values_identical.all()),
      "field_difference_threshold":1e-8,
      "model_interaction_difference_can_be_labeled_exact_reproduction":bool(r.source_values_identical.all()),
      "underlying_weather_is_representative_point_proxy":True,
      "wind_availability_is_assumed_power_curve_not_measured_output":True,
      "generator_or_transmission_physical_calibration_claimed":False,
      "historical_outages_or_eens_estimated":False
    }
    return r,m


def main():
    p=argparse.ArgumentParser()
    for key in ("old-demand","old-weather","new-demand","new-weather","output"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    x,m=audit(pd.read_csv(a.old_demand),pd.read_csv(a.new_demand),
              pd.read_csv(a.old_weather),pd.read_csv(a.new_weather))
    root=Path(a.output);root.mkdir(parents=True,exist_ok=True)
    x.to_csv(root/"july_first_week_original_vs_refetched_source_differences.csv",index=False)
    (root/"july_first_week_original_vs_refetched_manifest.json").write_text(
       json.dumps(m,indent=2)+"\n")
    print(x.to_string(index=False))
    print(json.dumps(m,indent=2))


if __name__=="__main__":
    main()
