"""Join EIA-923 generator-month observations to reviewed EIA-860 generator fuel codes.

EIA-860 inventory must first be extracted from the official 2024 workbook.
Only exact plant_id + generator_id matches are allowed. Unmatched, ambiguous,
or multi-fuel generators are NOT assigned a PyPSA technology.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

FUEL_TO_TECH = {
    "NG": "gas", "BIT": "coal", "SUB": "coal", "LIG": "coal", "RC": "coal",
    "NUC": "nuclear", "WAT": "hydro", "SUN": "solar", "WND": "wind",
    "GEO": "geothermal", "DFO": "oil", "RFO": "oil", "JF": "oil",
}
KEYS=["plant_id","generator_id"]

def join(eia923_csv, eia860_csv, output):
    a=pd.read_csv(eia923_csv,dtype={k:str for k in KEYS},keep_default_na=False)
    b=pd.read_csv(eia860_csv,dtype={k:str for k in KEYS},keep_default_na=False)
    if not {"plant_id","generator_id","reported_ba","period","generation_mwh"}.issubset(a):
        raise ValueError("EIA-923 generator-month schema incomplete")
    if not {"plant_id","generator_id","energy_source_1","prime_mover"}.issubset(b):
        raise ValueError("EIA-860 reviewed generator inventory schema incomplete")
    for frame in (a,b):
        for key in KEYS:
            frame[key]=frame[key].str.strip()
            if frame[key].eq("").any():
                raise ValueError("Empty generator join key")
    for col in ("reported_ba", "period"):
        a[col] = a[col].fillna("").astype(str).str.strip()
        if a[col].eq("").any():
            raise ValueError(f"Blank EIA-923 {col}; refusing unassigned generation")
    if not a.period.str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])").all():
        raise ValueError("Invalid EIA-923 YYYY-MM period")
    for col in ("energy_source_1", "prime_mover"):
        b[col] = b[col].fillna("").astype(str).str.strip().str.upper()
        if b[col].eq("").any():
            raise ValueError(f"Blank EIA-860 {col}")
    if "prime_mover" in a:
        a["prime_mover"] = a["prime_mover"].fillna("").astype(str).str.strip().str.upper()
        if a.prime_mover.eq("").any():
            raise ValueError("Blank EIA-923 prime_mover")
    if b.duplicated(KEYS).any():
        raise ValueError("Ambiguous EIA-860 generator ID inventory")
    if a.duplicated(KEYS+["period"]).any():
        raise ValueError("Duplicate EIA-923 generator-month")
    # Refuse silent fuel guesses: use the externally reviewed EIA-860
    # predominant energy source, and flag all other/unknown combinations.
    joined=a.merge(b[KEYS+["energy_source_1","prime_mover"]],on=KEYS,how="left",
                   validate="many_to_one",indicator=True,suffixes=("_923","_860"))
    joined["technology"]=joined.energy_source_1.map(FUEL_TO_TECH)
    # Pumped-storage units must not be treated as conventional hydro.
    # A net injection can be negative for either technology, so sign is not a classifier.
    ps = joined["prime_mover_860"].eq("PS") if "prime_mover_860" in joined else pd.Series(False, index=joined.index)
    joined.loc[ps, "technology"] = pd.NA
    joined["mapping_status"]="matched"
    joined.loc[joined._merge.ne("both"),"mapping_status"]="unmatched_generator"
    joined.loc[joined.technology.isna() & joined._merge.eq("both"),"mapping_status"]="unclassified_fuel_or_pumped_storage"
    if "prime_mover_923" in joined and "prime_mover_860" in joined:
        mismatch=joined.prime_mover_923.fillna("").astype(str).str.strip().ne(
            joined.prime_mover_860.fillna("").astype(str).str.strip())
        joined.loc[mismatch & joined._merge.eq("both"),"mapping_status"]="prime_mover_conflict"
    if joined.mapping_status.ne("matched").any():
        counts=joined.mapping_status.value_counts().to_dict()
        raise ValueError(f"Unresolved generator classification; refusing partial aggregation: {counts}")
    joined["generation_mwh"]=pd.to_numeric(joined.generation_mwh,errors="raise")
    if not joined.generation_mwh.map(lambda v: -float("inf")<float(v)<float("inf")).all():
        raise ValueError("Nonfinite generator generation")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    joined.groupby(["reported_ba","technology","period"],as_index=False).generation_mwh.sum().rename(
        columns={"reported_ba":"ba"}).to_csv(out/"observed_ba_technology_month.csv",index=False)
    manifest={"status":"mechanically_joined_not_independently_calibrated",
              "generator_month_rows":len(joined),"historical_calibration_certified":False,
              "limitations":"Single predominant energy source may misclassify multi-fuel/dual-fuel generation; storage codes excluded; generator IDs and EIA-860 inventory require external audit."}
    (out/"generator_technology_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--eia923",required=True);p.add_argument("--eia860",required=True)
    p.add_argument("--output",required=True)
    x=p.parse_args();print(json.dumps(join(x.eia923,x.eia860,x.output),indent=2))
if __name__=="__main__":
    main()
