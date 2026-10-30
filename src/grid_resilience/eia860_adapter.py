"""Map audited EIA-860 BA/technology nameplate to the *limited* V2 solver schema.

The four-scenario solver currently supports only gas-like dispatch and wind.
Non-wind thermal is NOT silently relabeled as gas; unmatched categories are
disclosed and results are only a partial-fleet screening experiment.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

ALLOWED={"thermal","wind","solar","hydro","nuclear","geothermal","storage","other"}
def adapt(source,output,bas=("CISO","AZPS","BPAT","SRP"),year=2024):
    df=pd.read_csv(source)
    required={"ba","technology","capacity_mw"}
    if not required.issubset(df):raise ValueError(f"Missing {sorted(required-set(df))}")
    if df.empty or df[list(required)].isna().any().any():raise ValueError("Empty/null inventory")
    if df.duplicated(["ba","technology"]).any():raise ValueError("Duplicate BA/technology")
    if set(df.ba)!=set(bas):raise ValueError("BA coverage mismatch")
    if set(df.technology)-ALLOWED:raise ValueError("Unrecognized technologies")
    df["capacity_mw"]=pd.to_numeric(df.capacity_mw,errors="raise")
    if df.capacity_mw.isna().any() or (df.capacity_mw<0).any():raise ValueError("Invalid capacity")
    if "source_year" in df:
        years=pd.to_numeric(df.source_year,errors="raise")
        if not years.eq(year).all():raise ValueError("EIA-860 inventory year mismatch")
    if "capacity_source" in df:
        if df.capacity_source.isna().any() or df.capacity_source.astype(str).str.strip().eq("").any():
            raise ValueError("Missing source label")
    # This deliberately retains broad 'thermal' as an assumed generic
    # dispatchable resource; no claim that 100% is gas or available in summer.
    rows=[]
    for ba in bas:
        sub=df[df.ba==ba].set_index("technology").capacity_mw
        if "thermal" not in sub or "wind" not in sub:
            raise ValueError(f"{ba}: thermal and wind categories must be explicit, including zero")
        rows.append({"ba":ba,"gas_mw":float(sub["thermal"]),"wind_mw":float(sub["wind"]),
                     "source_year":year,"capacity_source":"EIA860_partial_nameplate_GENERIC_THERMAL_PROXY"})
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(out/"capacity.csv",index=False)
    excluded=df[df.technology.isin(ALLOWED-{"thermal","wind"})].copy()
    excluded.to_csv(out/"excluded_technologies.csv",index=False)
    manifest={"source_file":str(source),"year":year,"bas":list(bas),
              "included_technologies":["thermal","wind"],
              "excluded_nameplate_mw":float(excluded.capacity_mw.sum()),
              "warning":"thermal mapped to solver gas_mw is a generic dispatchable proxy, NOT measured gas fleet, historical availability or calibrated power adequacy; solar/hydro/nuclear/etc are omitted."}
    (out/"capacity_mapping_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--output",required=True)
    p.add_argument("--bas",nargs="+",default=["CISO","AZPS","BPAT","SRP"])
    p.add_argument("--year",type=int,default=2024)
    a=p.parse_args()
    print(json.dumps(adapt(a.source,a.output,a.bas,a.year),indent=2))
if __name__=="__main__":main()
