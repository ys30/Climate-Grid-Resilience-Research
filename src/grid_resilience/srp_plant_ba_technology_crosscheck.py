"""Cross-check EIA-860 Plant BA source-scope generator candidates by technology.

This is an independent *roster* crosswalk, not hourly availability or dispatch.
The reference CSV is an archived independent earlier workflow aggregate.
Mismatch is reported rather than silently changing the model's input fleet.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

FUEL={"NG":"gas","SUB":"coal","BIT":"coal","NUC":"nuclear",
      "WAT":"hydro","SUN":"solar","WND":"wind"}
EMPTY={"","NA","NONE","."}
MULTI={"Y","YES","1","TRUE"}

def classify(roster,reference,*,ba="SRP"):
    fields={"plant_id","generator_id","nameplate_capacity_mw","energy_source_1",
            "energy_source_2","multiple_fuels","prime_mover","plant_reported_ba"}
    if not fields.issubset(roster.columns):raise ValueError("Missing EIA-860 source scope fields")
    if not {"technology","nameplate_capacity_mw","generator_count"}.issubset(reference.columns):
        raise ValueError("Reference fields missing")
    d=roster.copy()
    if not isinstance(ba,str) or not ba.strip():
        raise ValueError("Target BA must be nonempty")
    for key in ("plant_id","generator_id","plant_reported_ba"):
        d[key]=d[key].astype("string").str.strip()
        if d[key].isna().any() or d[key].eq("").any():
            raise ValueError("Missing roster identity or BA assignment")
    d["plant_id"]=d.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
    if not d.plant_reported_ba.eq(ba).all():
        raise ValueError("Plant BA roster contains records outside the requested BA")
    if "ba" in reference.columns:
        if not reference.ba.astype("string").str.strip().eq(ba).all():
            raise ValueError("Independent reference contains another BA")
    if d[["plant_id","generator_id"]].duplicated().any():raise ValueError("Duplicate roster identity")
    d["nameplate_capacity_mw"]=pd.to_numeric(d.nameplate_capacity_mw,errors="raise")
    if not np.isfinite(d.nameplate_capacity_mw.to_numpy(dtype=float)).all() or (d.nameplate_capacity_mw<0).any():
        raise ValueError("Invalid source nameplate")
    for k in ("energy_source_1","energy_source_2","multiple_fuels","prime_mover"):
        d[k]=d[k].fillna("").astype(str).str.strip().str.upper()
    is_multi=d.multiple_fuels.isin(MULTI)|~d.energy_source_2.isin(EMPTY)
    # Keep attrition codes consistent with the archived 2024 official BA audit:
    # PS pumped-hydro is storage; MWH remains an unmapped energy-source code.
    storage=d.prime_mover.eq("PS")
    mapped=d.energy_source_1.map(FUEL)
    valid=d.nameplate_capacity_mw.gt(0)&~is_multi&~storage&mapped.notna()
    d["candidate_class"]=np.select(
       [~d.nameplate_capacity_mw.gt(0),storage,is_multi,mapped.isna()],
       ["nonpositive_nameplate","storage_excluded","multifuel_or_secondary_fuel","unmapped_primary_energy_source"],
       default="included")
    d["technology_group"]=mapped
    selected=d.loc[valid]
    groups=selected.groupby("technology_group").agg(
      observed_candidate_generator_count=("generator_id","size"),
      observed_candidate_nameplate_mw=("nameplate_capacity_mw","sum")).reset_index()
    ref=reference.copy()
    if ref.empty:
        raise ValueError("Empty independent reference")
    ref["technology"]=ref.technology.astype("string").str.strip()
    if ref.technology.isna().any() or ref.technology.eq("").any():
        raise ValueError("Missing reference technology category")
    if ref.technology.duplicated().any():
        raise ValueError("Duplicate reference fuel categories")
    for key in ("nameplate_capacity_mw","generator_count"):
        ref[key]=pd.to_numeric(ref[key],errors="raise")
    if not np.isfinite(ref[["nameplate_capacity_mw","generator_count"]].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite independent reference")
    if (ref[["nameplate_capacity_mw","generator_count"]]<0).any().any():
        raise ValueError("Negative independent reference totals")
    if not np.allclose(ref.generator_count,np.round(ref.generator_count)):
        raise ValueError("Noninteger reference generator count")
    merged=groups.merge(ref,left_on="technology_group",right_on="technology",how="outer")
    # Fill only fields absent due to a legitimate outer join. Malformed
    # source reference values are rejected above rather than imputed to zero.
    for k in ("observed_candidate_generator_count","observed_candidate_nameplate_mw","generator_count","nameplate_capacity_mw"):
        merged[k]=merged[k].fillna(0)
    merged["generator_count_difference"]=merged.observed_candidate_generator_count-merged.generator_count
    merged["nameplate_difference_mw"]=merged.observed_candidate_nameplate_mw-merged.nameplate_capacity_mw
    class_agg=d.groupby("candidate_class").agg(
        generator_count=("generator_id","size"),
        nameplate_mw=("nameplate_capacity_mw","sum"))
    class_details={
        str(key):{
            "generator_count":int(values.generator_count),
            "nameplate_mw":float(values.nameplate_mw)
        }
        for key,values in class_agg.iterrows()
    }
    summary={
       "roster_class_capacity_mw":{
          str(key):float(values.nameplate_mw) for key,values in class_agg.iterrows()
       },
       "roster_class_details":class_details,
       "input_roster_generator_count":len(d),
       "eligible_selected_generator_count":len(selected),
       "eligible_selected_nameplate_mw":float(selected.nameplate_capacity_mw.sum()),
       "reference_generator_count":int(ref.generator_count.sum()),
       "reference_nameplate_mw":float(ref.nameplate_capacity_mw.sum()),
       "matched_reference_counts_and_capacities":bool((merged.generator_count_difference.abs()<1e-9).all() and (merged.nameplate_difference_mw.abs()<1e-3).all()),
       "roster_class_counts":{str(k):int(v) for k,v in d.candidate_class.value_counts().items()},
       "historical_availability_verified":False,
       "historical_calibration_certified":False,
       "note":"Independent archived Plant BA aggregate is a comparison reference, not a required physical calibration target."
    }
    return d,merged,summary

def main():
    p=argparse.ArgumentParser()
    for k in ("roster","reference","output"):p.add_argument("--"+k,required=True)
    p.add_argument("--ba",default="SRP")
    a=p.parse_args()
    roster,groups,summary=classify(pd.read_csv(a.roster,dtype={"plant_id":"string","generator_id":"string"}),
                                   pd.read_csv(a.reference),ba=a.ba)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    roster.to_csv(out/"plant_ba_technology_scope_rows.csv",index=False)
    groups.to_csv(out/"plant_ba_technology_reference_comparison.csv",index=False)
    (out/"plant_ba_technology_reference_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    print(groups.to_string(index=False))
if __name__=="__main__":main()
