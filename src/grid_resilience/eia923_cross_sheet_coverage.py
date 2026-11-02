"""Cross-sheet EIA-923 coverage audit; no implicit plant-generator reconciliation."""
import argparse
import json
from pathlib import Path
import pandas as pd

def audit(page4,hy,ps):
    frames=[]
    for name,frame,required in (
        ("page4",page4,{"plant_id","generator_id","prime_mover","reported_ba","period"}),
        ("hy",hy,{"plant_id","prime_mover","reported_ba","period"}),
        ("ps",ps,{"plant_id","prime_mover","reported_ba","period"})):
        if not required.issubset(frame.columns):raise ValueError(f"{name}: missing {sorted(required-set(frame.columns))}")
        f=frame.copy()
        if f.empty:raise ValueError(f"{name}: empty source")
        for field in ("plant_id","reported_ba","period"):
            f[field]=f[field].astype("string").str.strip()
            if f[field].isna().any() or f[field].eq("").any():raise ValueError(f"{name}: invalid {field}")
        f["plant_id"]=f.plant_id.str.replace(r"^0+(?=[0-9])", "",regex=True)
        frames.append(f)
    g,h,p=frames
    if not h.prime_mover.eq("HY").all() or not p.prime_mover.eq("PS").all():
        raise ValueError("Page 1 HY/PS technology mismatch")
    if g.duplicated(["plant_id","generator_id","period"]).any():
        raise ValueError("Duplicate Page 4 generator-month identifiers")
    if h.duplicated(["plant_id","reported_ba","prime_mover","period"]).any() or p.duplicated(["plant_id","reported_ba","prime_mover","period"]).any():
        raise ValueError("Duplicate Page 1 plant-technology-month identifiers")
    page1=pd.concat([h,p],ignore_index=True)
    p4=set(g.plant_id); p1=set(page1.plant_id)
    return {
      "page4_unique_plants":len(p4),
      "page1_hy_ps_unique_plants":len(p1),
      "page1_plants_also_in_page4":len(p1 & p4),
      "page4_hy_ps_rows":int(g.prime_mover.isin(["HY","PS"]).sum()),
      "page4_plants_multiple_reported_bas":int((g.groupby("plant_id").reported_ba.nunique()>1).sum()),
      "page1_plants_multiple_reported_bas":int((page1.groupby("plant_id").reported_ba.nunique()>1).sum()),
      "page1_hy_ps_shared_plants":len(set(h.plant_id)&set(p.plant_id)),
      "full_fleet_crosswalk_certified":False,
      "historical_calibration_certified":False,
      "caution":"Page 1 plant-month and Page 4 generator-month are not interchangeable."
    }

def main():
    ap=argparse.ArgumentParser()
    for arg in ("page4","hy","ps","output"):ap.add_argument("--"+arg,required=True)
    args=ap.parse_args()
    result=audit(*(pd.read_csv(getattr(args,k),dtype={"plant_id":"string","generator_id":"string"},keep_default_na=False) for k in ("page4","hy","ps")))
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
