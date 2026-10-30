"""Technology-resolved capacity inventory gate for future PyPSA expansion.

Accepts audited BA/technology nameplate totals. This does not infer fuel type
from a broad thermal bucket or create hourly availability profiles.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

TECHNOLOGIES = ("gas", "coal", "nuclear", "hydro", "solar", "wind", "geothermal", "oil", "biomass", "storage", "other")
REQUIRED = {"ba", "technology", "capacity_mw", "source_year", "capacity_source"}

def validate(source, output, expected_bas=None, expected_year=None):
    df = pd.read_csv(source, dtype={"ba": str, "technology": str, "capacity_source": str})
    if not REQUIRED.issubset(df):
        raise ValueError(f"Missing required columns: {sorted(REQUIRED - set(df))}")
    if df.empty or df[list(REQUIRED)].isna().any().any():
        raise ValueError("Empty inventory or missing values")
    for field in ("ba", "technology", "capacity_source"):
        df[field] = df[field].str.strip()
        if df[field].eq("").any():
            raise ValueError(f"Blank {field}")
    if not set(df.technology).issubset(TECHNOLOGIES):
        raise ValueError(f"Unknown technology categories: {sorted(set(df.technology)-set(TECHNOLOGIES))}")
    if df.duplicated(["ba", "technology"]).any():
        raise ValueError("Duplicate BA/technology rows")
    df["capacity_mw"] = pd.to_numeric(df.capacity_mw, errors="raise")
    df["source_year"] = pd.to_numeric(df.source_year, errors="raise")
    if not df.capacity_mw.map(lambda x: 0 <= float(x) < float("inf")).all():
        raise ValueError("Capacity must be finite and nonnegative")
    if not df.source_year.map(lambda x: float(x).is_integer() and 1900 <= float(x) <= 2100).all():
        raise ValueError("Invalid source year")
    if expected_year is not None and not df.source_year.eq(expected_year).all():
        raise ValueError("Source year mismatch")
    if expected_bas is not None and set(df.ba) != set(expected_bas):
        raise ValueError("BA coverage mismatch")
    bas = sorted(df.ba.unique().tolist())
    matrix = pd.MultiIndex.from_product([bas, TECHNOLOGIES], names=["ba", "technology"])
    # Keep absent entries absent: missing inventory cannot be silently treated as zero.
    missing = matrix.difference(pd.MultiIndex.from_frame(df[["ba", "technology"]]))
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    df.sort_values(["ba", "technology"]).to_csv(out / "technology_capacity_audited_input.csv", index=False)
    manifest = {
        "classification": "technology_resolved_nameplate_only_not_dispatch_ready",
        "bas": bas, "technologies": list(TECHNOLOGIES),
        "source_years": sorted(df.source_year.astype(int).unique().tolist()),
        "inventory_rows": len(df),
        "total_nameplate_mw": float(df.capacity_mw.sum()),
        "missing_ba_technology_combinations": [list(x) for x in missing],
        "hourly_availability_validated": False,
        "calibration_complete": False,
        "warning": "Absence is not zero. Nameplate alone cannot establish hourly dependable supply; storage requires energy capacity, efficiency and SOC.",
    }
    (out / "technology_capacity_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--expected-year", type=int)
    p.add_argument("--expected-bas", nargs="+")
    args = p.parse_args()
    print(json.dumps(validate(args.source, args.output, args.expected_bas, args.expected_year), indent=2))

if __name__ == "__main__":
    main()
