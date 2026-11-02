"""Keep EIA-923 measured energy regardless of EIA-860 retirement status.

Separate observed-energy ledger from eligibility for modeled operable capacity.
"""
import argparse
from pathlib import Path
import pandas as pd

def reconcile(monthly, statuses):
    keys=["plant_id","generator_id"]
    needed=set(keys+["reported_ba","period","generation_mwh"])
    if not needed.issubset(monthly.columns):
        raise ValueError("Missing observed generation fields")
    sn=set(keys+["exact_sheet_matches","exact_reported_statuses"])
    if not sn.issubset(statuses.columns):
        raise ValueError("Missing EIA-860 status triage fields")
    obs=monthly.copy()
    tri=statuses.copy()
    for f in (obs,tri):
        for k in keys:
            f[k]=f[k].astype("string").str.strip()
            if f[k].isna().any() or f[k].eq("").any():
                raise ValueError("Null identity key")
        f["plant_id"]=f.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
    if tri.duplicated(keys).any():
        raise ValueError("Duplicate status identity keys")
    if obs.duplicated(keys+["reported_ba","period"]).any():
        raise ValueError("Duplicate generator BA-month keys")
    obs["generation_mwh"]=pd.to_numeric(obs.generation_mwh,errors="raise")
    if obs.generation_mwh.isna().any() or not obs.generation_mwh.map(lambda x:float("-inf")<float(x)<float("inf")).all():
        raise ValueError("Missing or nonfinite observed energy")
    out=obs.merge(tri[keys+["exact_sheet_matches","exact_reported_statuses"]],
                  on=keys,how="left",validate="many_to_one")
    out["identity_review_group"]=out.exact_sheet_matches.fillna("").map(
        lambda v:"2024_retired_or_canceled_sheet" if "Retired and Canceled" in v else
        ("other_status_sheet" if v else "not_in_status_exceptions"))
    out["observed_mwh_retained"]=out.generation_mwh
    out["eligible_for_2024_operable_capacity"]=False
    out["capacity_eligibility_note"]="Requires date-specific independent generator status audit"
    return out

def main():
    p=argparse.ArgumentParser()
    for name in ("observed","statuses","output"):p.add_argument("--"+name,required=True)
    a=p.parse_args()
    ledger=reconcile(pd.read_csv(a.observed,dtype={"plant_id":"string","generator_id":"string"}),
                     pd.read_csv(a.statuses,dtype={"plant_id":"string","generator_id":"string"}))
    path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True)
    ledger.to_csv(path,index=False)
    print("Retained observed source MWh:",ledger.observed_mwh_retained.sum())
    print("Capacity certification: no")

if __name__=="__main__":main()
