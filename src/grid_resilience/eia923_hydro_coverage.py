"""Report observed HY/PS monthly coverage without treating absent records as zero.

This is a source-coverage diagnostic, NOT proof that a fleet exists in each BA.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

BAS = ("AZPS", "BPAT", "CISO", "SRP")
CODES = ("HY", "PS")
MONTHS = tuple(f"2024-{m:02d}" for m in range(1, 13))
REQUIRED = {"reported_ba", "prime_mover", "period", "net_generation_mwh",
            "generator_month_records"}

def audit(input_csv, output_dir):
    df = pd.read_csv(input_csv, dtype={"reported_ba": str, "prime_mover": str,
                                        "period": str}, keep_default_na=False)
    if not REQUIRED.issubset(df.columns):
        raise ValueError("Missing prime mover monthly audit fields")
    df = df.copy()
    for col in ("reported_ba", "prime_mover", "period"):
        df[col] = df[col].str.strip()
    df = df[df.reported_ba.isin(BAS) & df.prime_mover.isin(CODES)].copy()
    if df.duplicated(["reported_ba", "prime_mover", "period"]).any():
        raise ValueError("Ambiguous duplicate BA/prime-mover/month rows")
    if not df.empty:
        if not df.period.isin(MONTHS).all():
            raise ValueError("Unexpected year/month in 2024 coverage audit")
        df["net_generation_mwh"] = pd.to_numeric(df.net_generation_mwh, errors="raise")
        df["generator_month_records"] = pd.to_numeric(df.generator_month_records, errors="raise")
        if not df.net_generation_mwh.map(lambda v: -float("inf") < v < float("inf")).all():
            raise ValueError("Nonfinite net generation")
        if not df.generator_month_records.map(lambda v: float(v).is_integer() and v > 0).all():
            raise ValueError("Invalid observed record count")
    index = pd.MultiIndex.from_product([BAS, CODES, MONTHS],
                                       names=["reported_ba", "prime_mover", "period"])
    observed = df.set_index(["reported_ba", "prime_mover", "period"])[
        ["net_generation_mwh", "generator_month_records"]]
    result = observed.reindex(index).reset_index()
    result["coverage_status"] = result.generator_month_records.notna().map(
        {True: "observed_record", False: "missing_record"})
    result["net_generation_mwh"] = result["net_generation_mwh"].astype("Float64")
    result["generator_month_records"] = result["generator_month_records"].astype("Int64")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    result.to_csv(out / "hydro_ps_coverage_2024.csv", index=False)
    counts = result.groupby(["reported_ba", "prime_mover", "coverage_status"]).size()
    summary = {"expected_ba_code_month_slots": len(index),
               "observed_slots": int((result.coverage_status == "observed_record").sum()),
               "missing_slots": int((result.coverage_status == "missing_record").sum()),
               "observed_zero_generation_slots": int(
                   ((result.coverage_status == "observed_record") &
                    (result.net_generation_mwh == 0)).sum()),
               "by_ba_code": [
                   {"ba": ba, "prime_mover": code,
                    "observed_months": int(counts.get((ba, code, "observed_record"), 0)),
                    "missing_months": int(counts.get((ba, code, "missing_record"), 0))}
                   for ba in BAS for code in CODES],
               "historical_calibration_certified": False,
               "caution": "Missing record is not zero output or evidence that the fleet exists. Source/plant inventory is required to determine expected coverage."}
    (out / "hydro_ps_coverage_manifest.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    print(json.dumps(audit(a.input, a.output), indent=2))

if __name__ == "__main__":
    main()
