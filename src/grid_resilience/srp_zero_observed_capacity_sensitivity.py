"""Optional zero-observed-output *availability* sensitivity; not a factual outage.

The scenario removes the assumed derated capacity of screened generators
whose matching EIA-923 Page4 monthly net generation happens to be exactly 0.
Zero monthly output is NOT proof of unavailability; this is a stress test.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from grid_resilience.srp_hourly_oracle_audit import audit

def scenario(hourly, review, observed, capacity, *, ba="SRP",year=2024,month=1):
    baseline=audit(hourly,capacity,ba=ba,year=year,month=month)
    keys=["plant_id","generator_id"]
    for d in (review,observed):
        if not set(keys).issubset(d):raise ValueError("Generator keys missing")
    if not {"screening_candidate","nameplate_capacity_mw","energy_source_1"}.issubset(review):
        raise ValueError("Missing inventory fields")
    if not {"generation_mwh","identity_scope"}.issubset(observed):
        raise ValueError("Missing observed generator fields")
    r=review.copy();o=observed.copy()
    for df in (r,o):
        for k in keys:
            df[k]=df[k].astype("string").str.strip()
            if k=="plant_id":df[k]=df[k].str.replace(r"^0+(?=[0-9])","",regex=True)
        if df.duplicated(keys).any() or df[keys].isna().any().any():raise ValueError("Invalid generator keys")
    flags=r.screening_candidate.astype(str).str.lower().map({"true":True,"false":False})
    if flags.isna().any():raise ValueError("Ambiguous eligibility")
    r["eligible"]=flags
    r["nameplate_capacity_mw"]=pd.to_numeric(r.nameplate_capacity_mw,errors="raise")
    o["generation_mwh"]=pd.to_numeric(o.generation_mwh,errors="raise")
    if not np.isfinite(r.nameplate_capacity_mw).all() or not np.isfinite(o.generation_mwh).all():
        raise ValueError("Nonfinite generator source")
    join=r.merge(o[keys+["generation_mwh","identity_scope"]],on=keys,validate="one_to_one",how="outer",indicator=True)
    if not join._merge.eq("both").all():raise ValueError("Incomplete source identity join")
    selected=join.loc[join.eligible & join.generation_mwh.eq(0)].copy()
    if not selected.identity_scope.eq("exact_screened_generator").all():raise ValueError("Invalid observed source-scope identity")
    c=capacity[capacity.ba.eq(ba)].copy()
    if not {"technology","capacity_mw","original_nameplate_mw"}.issubset(c.columns):
        raise ValueError("Missing derating assumptions")
    c["capacity_mw"]=pd.to_numeric(c.capacity_mw,errors="raise")
    c["original_nameplate_mw"]=pd.to_numeric(c.original_nameplate_mw,errors="raise")
    if (c.original_nameplate_mw<=0).any() or not np.isfinite(c[["capacity_mw","original_nameplate_mw"]]).all().all():
        raise ValueError("Invalid derating inputs")
    if c.empty or c.technology.duplicated().any():
        raise ValueError("Missing or duplicate fuel-level capacities")
    if (r.nameplate_capacity_mw<0).any():
        raise ValueError("Negative reviewed unit nameplate")
    reviewed_fuel=r.loc[r.eligible].copy()
    reviewed_fuel["technology"]=reviewed_fuel.energy_source_1.astype("string").str.strip().str.upper()
    actual_nameplate=reviewed_fuel.groupby("technology").nameplate_capacity_mw.sum()
    model_nameplate=c.set_index("technology").original_nameplate_mw
    if set(actual_nameplate.index)!=set(model_nameplate.index):
        raise ValueError("Capacity fuel populations differ from eligible generator inventory")
    if not np.allclose(actual_nameplate.loc[model_nameplate.index].to_numpy(dtype=float),
                       model_nameplate.to_numpy(dtype=float),atol=1e-5,rtol=0):
        raise ValueError("Fuel-level model nameplate does not reconcile to screened identities")
    expected_scopes=np.where(join.eligible,"exact_screened_generator","reviewed_but_excluded")
    if not (join.identity_scope.to_numpy()==expected_scopes).all():
        raise ValueError("Inconsistent generator eligibility scope")
    if (c.capacity_mw<0).any() or (c.capacity_mw>c.original_nameplate_mw+1e-5).any():
        raise ValueError("Invalid model derating assumptions")
    derating=dict(zip(c.technology.astype(str),c.capacity_mw/c.original_nameplate_mw))
    selected["technology"]=selected.energy_source_1.astype(str)
    if not selected.technology.isin(derating).all():raise ValueError("Unmapped zero-output fuel")
    removal=float(sum(float(x.nameplate_capacity_mw)*derating[x.technology] for x in selected.itertuples()))
    cap=float(baseline["screened_dispatchable_capacity_mw"])
    required=hourly.demand_mw.to_numpy(dtype=float)+hourly.observed_export_mw.to_numpy(dtype=float)-hourly.observed_import_mw.to_numpy(dtype=float)
    new_cap=cap-removal
    if new_cap<0:raise ValueError("Removal exceeds capacity")
    new_gap=np.maximum(required-new_cap,0)
    return {
       "period":f"{year}-{month:02d}",
       "source_matched_screened_zero_output_units":len(selected),
       "source_matched_screened_zero_output_nameplate_mw":float(selected.nameplate_capacity_mw.sum()),
       "baseline_hypothetical_available_mw":cap,
       "scenario_capacity_removed_after_original_deratings_mw":removal,
       "scenario_available_mw":new_cap,
       "baseline_modeled_unserved_mwh":baseline["modeled_unserved_mwh"],
       "scenario_modeled_unserved_mwh":float(new_gap.sum()),
       "scenario_gap_hours":int((new_gap>1e-6).sum()),
       "historical_availability_inferred":False,
       "historical_calibration_certified":False,
       "warning":"Hypothetical removing zero-OBSERVED-output units; monthly zero reported net generation does not prove historical unavailability."
    }

def main():
    p=argparse.ArgumentParser()
    for key in ("hourly","review","observed","capacity","output"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    result=scenario(pd.read_csv(a.hourly),pd.read_csv(a.review),pd.read_csv(a.observed),pd.read_csv(a.capacity))
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
