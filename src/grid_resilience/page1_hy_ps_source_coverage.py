"""Source-grain-separated Page1 HY/PS coverage; never infer it from Page4."""
import argparse,json
from pathlib import Path
import pandas as pd

MONTHS=[f"2024-{m:02d}" for m in range(1,13)]
def audit(page1,ba="SRP"):
    needed={"plant_id","ba","prime_mover","period","net_generation_mwh"}
    if not needed.issubset(page1):raise ValueError("Missing Page1 source columns")
    d=page1.loc[page1.ba.eq(ba)&page1.prime_mover.isin(["HY","PS"])].copy()
    if d.empty:raise ValueError("No Page1 HY/PS source records")
    if not d.period.isin(MONTHS).all():raise ValueError("Unexpected month")
    d["net_generation_mwh"]=pd.to_numeric(d.net_generation_mwh,errors="raise")
    if d.net_generation_mwh.isna().any():raise ValueError("Missing reported Page1 net MWh")
    observed=d.groupby(["prime_mover","period"],as_index=False).agg(
      source_rows=("plant_id","size"),observed_net_mwh=("net_generation_mwh","sum"))
    grid=pd.MultiIndex.from_product([["HY","PS"],MONTHS],names=["prime_mover","period"]).to_frame(index=False)
    coverage=grid.merge(observed,on=["prime_mover","period"],how="left",validate="one_to_one")
    coverage["coverage_status"]=coverage.source_rows.notna().map({True:"observed_page1_rows",False:"no_reported_page1_rows"})
    coverage["source_grain"]="Page1 plant-fuel-prime-mover month"
    coverage["calibration_certified"]=False
    manifest={"ba":ba,"observed_month_slots":int(coverage.source_rows.notna().sum()),
      "expected_month_slots":24,"missing_page1_month_slots":int(coverage.source_rows.isna().sum()),
      "page4_coverage_not_interchangeable":True,"historical_calibration_certified":False}
    return coverage,manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--page1",required=True);p.add_argument("--output",required=True)
    p.add_argument("--ba",default="SRP")
    a=p.parse_args()
    table,m=audit(pd.read_csv(a.page1),a.ba)
    dest=Path(a.output);dest.mkdir(parents=True,exist_ok=True)
    table.to_csv(dest/"page1_hy_ps_source_coverage.csv",index=False)
    (dest/"page1_hy_ps_source_coverage_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print(json.dumps(m,indent=2))
if __name__=="__main__":main()
