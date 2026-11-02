"""Source-scoped EIA-923 monthly technology coverage, no invented generation."""
import argparse,json
from pathlib import Path
import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
MONTHS=tuple(f"2024-{i:02d}" for i in range(1,13))

def coverage(ledger,operable):
    required={"plant_id","generator_id","reported_ba","period","generation_mwh"}
    if not required.issubset(ledger.columns):raise ValueError("Missing monthly ledger columns")
    if not {"plant_id","generator_id","energy_source_1","energy_source_2","multiple_fuels","prime_mover"}.issubset(operable.columns):
        raise ValueError("Missing EIA-860 technology fields")
    a,b=ledger.copy(),operable.copy()
    for f in (a,b):
        for k in ("plant_id","generator_id"):
            f[k]=f[k].astype("string").str.strip()
            if f[k].isna().any() or f[k].eq("").any():raise ValueError("Blank IDs")
        f["plant_id"]=f.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
    if b.duplicated(["plant_id","generator_id"]).any():raise ValueError("Duplicate inventory keys")
    if a.duplicated(["plant_id","generator_id","reported_ba","period"]).any():raise ValueError("Duplicate ledger keys")
    if not a.reported_ba.isin(BAS).all() or not a.period.isin(MONTHS).all():
        raise ValueError("Unexpected BA/month")
    a["generation_mwh"]=pd.to_numeric(a.generation_mwh,errors="raise")
    if not a.generation_mwh.map(lambda x:float("-inf")<float(x)<float("inf")).all():
        raise ValueError("Missing or invalid generation")
    joined=a.merge(b[["plant_id","generator_id","energy_source_1","energy_source_2","multiple_fuels","prime_mover"]],
                   on=["plant_id","generator_id"],how="left",validate="many_to_one",indicator=True)
    secondary=joined.energy_source_2.fillna("").astype(str).str.strip().str.upper()
    multifuel=joined.multiple_fuels.fillna("").astype(str).str.strip().str.upper()
    primary=joined.energy_source_1.fillna("").astype(str).str.strip().str.upper()
    ambiguous=(secondary.ne("")&~secondary.isin(["NA","NONE","."])) | multifuel.isin(["Y","YES","1","TRUE"]) | primary.isin(["","NA","NONE","."])
    joined["classification"]= "single_source_candidate"
    joined.loc[ambiguous,"classification"]="multifuel_ambiguous"
    joined.loc[joined["_merge"].ne("both"),"classification"]="not_in_operable_inventory"
    joined["technology_key"]=joined.energy_source_1.where(joined.classification.eq("single_source_candidate"),"UNRESOLVED")
    included=joined[joined.classification.eq("single_source_candidate")]
    sums=included.groupby(["reported_ba","technology_key","period"],as_index=False).agg(
        source_mwh=("generation_mwh","sum"),source_rows=("generator_id","size"))
    grid=pd.MultiIndex.from_product([BAS,sorted(included.technology_key.dropna().unique()),MONTHS],
          names=["reported_ba","technology_key","period"])
    summary=sums.set_index(["reported_ba","technology_key","period"]).reindex(grid).reset_index()
    summary["coverage_status"]=summary.source_rows.notna().map({True:"has_selected_source_rows",False:"missing_selected_source_rows"})
    summary["calibration_certified"]=False
    counts=joined.groupby(["reported_ba","classification"],as_index=False).agg(
        rows=("generator_id","size"),source_mwh=("generation_mwh","sum"))
    return joined.drop(columns=["_merge"]),summary,counts

def main():
    p=argparse.ArgumentParser()
    for k in ("ledger","operable","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    j,s,c=coverage(pd.read_csv(a.ledger,dtype={"plant_id":"string","generator_id":"string"}),
                   pd.read_csv(a.operable,dtype={"plant_id":"string","generator_id":"string"}))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    j.to_csv(out/"eia923_technology_classification_audit.csv",index=False)
    s.to_csv(out/"eia923_month_technology_coverage.csv",index=False)
    c.to_csv(out/"eia923_multifuel_exclusions.csv",index=False)
    print(json.dumps({"rows":len(j),"classification_counts":j.classification.value_counts().to_dict(),
      "observed_month_slots":int(s.source_rows.notna().sum()),"expected_slots":len(s),
      "calibration_certified":False},indent=2))
if __name__=="__main__":main()
