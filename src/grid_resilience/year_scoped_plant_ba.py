"""Period-aware EIA-923 plant/technology to BA mapping.

Every observed plant/technology/month must match a year-specific crosswalk.
Does not infer historical affiliations or validate claimed source documents.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def aggregate(generation_csv, crosswalk_csv, output_dir):
    g = pd.read_csv(generation_csv, dtype={"plant_id": str, "period": str, "technology": str})
    x = pd.read_csv(crosswalk_csv, dtype={"plant_id": str, "technology": str,
                                         "ba": str, "mapping_source": str, "source_year": str})
    gcols = {"plant_id", "period", "technology", "generation_mwh"}
    xcols = {"plant_id", "technology", "ba", "mapping_source", "source_year"}
    if not gcols.issubset(g) or not xcols.issubset(x):
        raise ValueError("Missing period-aware crosswalk or generation fields")
    if g.empty or x.empty or g[list(gcols)].isna().any().any() or x[list(xcols)].isna().any().any():
        raise ValueError("Empty or null input")
    for df, cols in [(g, ["plant_id", "period", "technology"]),
                     (x, ["plant_id", "technology", "ba", "mapping_source", "source_year"])]:
        for col in cols:
            df[col] = df[col].astype(str).str.strip()
            if df[col].eq("").any():
                raise ValueError(f"Blank {col}")
    if not g.period.str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])").all():
        raise ValueError("Invalid YYYY-MM period")
    if not x.source_year.str.fullmatch(r"\d{4}").all():
        raise ValueError("Invalid crosswalk source year")
    g["source_year"] = g.period.str[:4]
    if g.duplicated(["plant_id", "period", "technology"]).any():
        raise ValueError("Duplicate observed plant-month-technology")
    if x.duplicated(["plant_id", "source_year", "technology"]).any():
        raise ValueError("Ambiguous BA crosswalk for plant-year-technology")
    g["generation_mwh"] = pd.to_numeric(g.generation_mwh, errors="raise")
    if not g.generation_mwh.map(lambda v: -float("inf") < float(v) < float("inf")).all():
        raise ValueError("Nonfinite generation")
    joined = g.merge(x, on=["plant_id", "source_year", "technology"], how="left",
                     validate="many_to_one", indicator=True)
    if not joined._merge.eq("both").all():
        raise ValueError("Missing year-specific plant-to-BA mapping")
    totals = joined.groupby(["ba", "technology", "period"], as_index=False).generation_mwh.sum()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    totals.sort_values(["ba", "technology", "period"]).to_csv(
        out / "observed_ba_technology_month.csv", index=False
    )
    manifest = {
        "classification": "year_scoped_crosswalk_not_independently_verified",
        "mapped_rows": len(joined),
        "years": sorted(joined.source_year.unique().tolist()),
        "source_labels": sorted(joined.mapping_source.unique().tolist()),
        "historical_calibration_certified": False,
        "warning": "BA changes within a calendar year and EIA-923/860 source authenticity are not verified."
    }
    (out / "year_scoped_mapping_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--generation", required=True)
    p.add_argument("--crosswalk", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    print(json.dumps(aggregate(args.generation, args.crosswalk, args.output), indent=2))

if __name__ == "__main__":
    main()
