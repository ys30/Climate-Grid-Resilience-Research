"""Independent identity-level eligibility audit for partial EIA-860/Page-4 supply.

Fuel-code overlap is not evidence that an observed generator was included.
Do not infer missing generator net MWh as zero, or call this a complete BA fleet.
"""
import argparse,json
from pathlib import Path
import pandas as pd

KEYS=["plant_id","generator_id"]
def validate(page4,review,ba="SRP",month="2024-01"):
    p=page4.copy();r=review.copy()
    if not set(KEYS+["reported_ba","period","generation_mwh"]).issubset(p):
        raise ValueError("Missing observed generator-month columns")
    if not set(KEYS+["screening_candidate"]).issubset(r):
        raise ValueError("Missing screened generator identity fields")
    for f in (p,r):
        for k in KEYS:
            f[k]=f[k].astype("string").str.strip()
            if f[k].isna().any() or f[k].eq("").any():raise ValueError("Blank generator ID")
        f["plant_id"]=f.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
    if r.duplicated(KEYS).any():raise ValueError("Duplicate candidate generator IDs")
    if r.empty:raise ValueError("Empty capacity review")
    p=p[p.reported_ba.eq(ba)&p.period.eq(month)].copy()
    if p.empty or p.duplicated(KEYS).any():raise ValueError("Empty or duplicate observed generator-month IDs")
    if p[KEYS].isna().any().any() or p[KEYS].eq("").any().any():raise ValueError("Blank selected generator IDs")
    p["generation_mwh"]=pd.to_numeric(p.generation_mwh,errors="raise")
    if p.generation_mwh.isna().any() or not p.generation_mwh.map(lambda x:float("-inf")<float(x)<float("inf")).all():
        raise ValueError("Invalid observed net generation")
    r["screening_candidate"]=r.screening_candidate.astype(str).str.lower().map({"true":True,"false":False})
    if r.screening_candidate.isna().any():raise ValueError("Ambiguous candidate flag")
    joined=p.merge(r[KEYS+["screening_candidate"]],on=KEYS,how="left",indicator=True,validate="one_to_one")
    joined["identity_scope"]="not_in_capacity_review"
    joined.loc[joined["_merge"].eq("both")&joined.screening_candidate.eq(False),"identity_scope"]="reviewed_but_excluded"
    joined.loc[joined["_merge"].eq("both")&joined.screening_candidate.eq(True),"identity_scope"]="exact_screened_generator"
    summary=joined.groupby("identity_scope").agg(rows=("generator_id","size"),observed_net_mwh=("generation_mwh","sum")).reset_index()
    matched=joined.identity_scope.eq("exact_screened_generator")
    observed_total=float(p.generation_mwh.sum())
    observed_abs_total=float(p.generation_mwh.abs().sum())
    matched_total=float(joined.loc[matched,"generation_mwh"].sum())
    matched_abs=float(joined.loc[matched,"generation_mwh"].abs().sum())
    manifest={"ba":ba,"month":month,"observed_page4_rows":len(p),
        "observed_page4_net_mwh":observed_total,
        "exact_screened_observed_net_mwh":matched_total,
        "excluded_or_unmatched_observed_net_mwh":observed_total-matched_total,
        "observed_page4_absolute_mwh":observed_abs_total,
        "screened_identity_share_of_absolute_mwh":matched_abs/observed_abs_total if observed_abs_total else None,
        "exact_generator_screened_rows":int(joined.identity_scope.eq("exact_screened_generator").sum()),
        "excluded_or_unmatched_rows":int(joined.identity_scope.ne("exact_screened_generator").sum()),
        "all_page4_observed_generators_screened":bool(joined.identity_scope.eq("exact_screened_generator").all()),
        "complete_ba_fleet_certified":False,"historical_calibration_certified":False,
        "warning":"Exact identity inclusion is only within partial Page4 source; EIA-930 total and Page1 have separate scope."}
    if abs(float(summary.observed_net_mwh.sum())-observed_total)>max(1e-8,abs(observed_total)*1e-10):
        raise ValueError("Observed energy ledger failed reconciliation")
    return joined.drop(columns=["_merge"]),summary,manifest

def main():
    parser=argparse.ArgumentParser()
    for k in ("page4","review","output"):parser.add_argument("--"+k,required=True)
    parser.add_argument("--ba",default="SRP");parser.add_argument("--month",default="2024-01")
    a=parser.parse_args()
    d,s,m=validate(pd.read_csv(a.page4,dtype={"plant_id":"string","generator_id":"string"}),
                   pd.read_csv(a.review,dtype={"plant_id":"string","generator_id":"string"}),a.ba,a.month)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    d.to_csv(out/"exact_generator_scope_rows.csv",index=False)
    s.to_csv(out/"exact_generator_scope_summary.csv",index=False)
    (out/"exact_generator_scope_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print(json.dumps({"summary":s.to_dict("records"),"manifest":m},indent=2))
if __name__=="__main__":main()
