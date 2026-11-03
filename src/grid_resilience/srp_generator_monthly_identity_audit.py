"""Audit observed generator rows, zero-output identities and screen eligibility.

A source-scope diagnostic, NOT a full balancing-authority fleet census.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

def audit(review, rows):
    keys=["plant_id","generator_id"]
    required_review=set(keys+["screening_candidate","nameplate_capacity_mw"])
    required_rows=set(keys+["generation_mwh","identity_scope"])
    if not required_review.issubset(review.columns) or not required_rows.issubset(rows.columns):
        raise ValueError("Required generator audit columns missing")
    c=review.copy();g=rows.copy()
    for d in [c,g]:
        for k in keys:
            d[k]=d[k].astype("string").str.strip()
            if d[k].isna().any() or d[k].eq("").any():
                raise ValueError("Blank generator identity")
        if d.duplicated(keys).any():
            raise ValueError("Duplicate generator identity")
    flags=c.screening_candidate.astype(str).str.lower().map({"true":True,"false":False})
    if flags.isna().any():raise ValueError("Invalid generator eligibility")
    c["eligible"]=flags
    c["nameplate_capacity_mw"]=pd.to_numeric(c.nameplate_capacity_mw,errors="raise")
    g["generation_mwh"]=pd.to_numeric(g.generation_mwh,errors="raise")
    if not np.isfinite(c.nameplate_capacity_mw.to_numpy()).all() or (c.nameplate_capacity_mw<0).any():
        raise ValueError("Invalid capacities")
    if not np.isfinite(g.generation_mwh.to_numpy()).all():
        raise ValueError("Invalid generation")
    joined=g.merge(c[keys+["eligible","nameplate_capacity_mw"]],on=keys,how="left",validate="one_to_one",indicator=True)
    if not joined._merge.eq("both").all() or len(joined)!=len(c):
        raise ValueError("Source identity reconciliation incomplete")
    expected=joined.eligible.map({True:"exact_screened_generator",False:"reviewed_but_excluded"})
    if not expected.eq(joined.identity_scope).all():
        raise ValueError("Source identity eligibility mismatch")
    negative=int((joined.generation_mwh<0).sum())
    screened=joined.loc[joined.eligible]
    excluded=joined.loc[~joined.eligible]
    return {
      "matched_generator_identities":len(joined),
      "screened_identities":len(screened),
      "excluded_identities":len(excluded),
      "screened_zero_observed_monthly_net_generation":int(screened.generation_mwh.eq(0).sum()),
      "excluded_zero_observed_monthly_net_generation":int(excluded.generation_mwh.eq(0).sum()),
      "excluded_with_nonzero_observed_monthly_net_generation":int(excluded.generation_mwh.ne(0).sum()),
      "negative_reported_net_generation_identities":negative,
      "screened_observed_page4_monthly_net_mwh":float(screened.generation_mwh.sum()),
      "excluded_observed_page4_monthly_net_mwh":float(excluded.generation_mwh.sum()),
      "screened_nameplate_mw":float(screened.nameplate_capacity_mw.sum()),
      "excluded_nameplate_mw":float(excluded.nameplate_capacity_mw.sum()),
      "scope":"Matched EIA-860 identities to source-reported EIA-923 Page4 monthly generator rows; NOT full BA fleet nor dispatch calibration",
      "no_recorded_generation_does_not_prove_inactive_or_unavailable":True,
      "historical_calibration_certified":False
    }

def main():
    p=argparse.ArgumentParser()
    for k in ("review","rows","output"):p.add_argument("--"+k,required=True)
    args=p.parse_args()
    result=audit(pd.read_csv(args.review),pd.read_csv(args.rows))
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
