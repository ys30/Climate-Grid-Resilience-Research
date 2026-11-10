"""Strict source-reported EIA-930 six+Other+Petroleum reconciliation.

The analysis is a bookkeeping diagnostic, NOT a generation shortfall, physical
dispatch, measured outage, EENS, or a replacement for blank original categories.
Scope: 161 UTC hours in the 2024 Jul-Dec modern fuel taxonomy.
"""
from pathlib import Path
import argparse
import json
import pandas as pd

from grid_resilience.paperc_2024_full_fuel_schema_audit import BAS, N, START

OTHER = "Other Fuel Sources"
PETROLEUM = "All Petroleum Products"


def reconcile(fuel: pd.DataFrame, six: pd.DataFrame):
    required = {"year", "ba", "utc_hour_start", "original_partition",
                "original_fuel_category", "fuel_value_reported",
                "reported_fuel_mwh"}
    if not required.issubset(fuel.columns):
        raise ValueError("Missing original EIA-930 fuel fields")
    x = fuel.loc[fuel.year.eq(2024) &
                 fuel.original_partition.eq("Jul_Dec")].copy()
    x["utc_hour_start"] = pd.to_datetime(x.utc_hour_start, utc=True)
    keys = {(ba, START + pd.Timedelta(hours=i)) for ba in BAS for i in range(N)}
    if set(zip(x.ba, x.utc_hour_start)) != keys:
        raise ValueError("161h source BA-hour coverage incomplete")
    if x.duplicated(["ba", "utc_hour_start", "original_fuel_category"]).any():
        raise ValueError("Duplicate original fuel record")
    flags = x.fuel_value_reported.astype(str).str.lower()
    if not flags.isin(["true", "false"]).all():
        raise ValueError("Invalid original numeric flag")
    x["reported"] = flags.eq("true")
    if (x.loc[~x.reported, "reported_fuel_mwh"].notna().any() or
            x.loc[x.reported, "reported_fuel_mwh"].isna().any()):
        raise ValueError("Numeric/blank reporting flags inconsistent")
    labels = set(x.original_fuel_category.unique())
    if not {OTHER, PETROLEUM}.issubset(labels):
        raise ValueError("Required original fuel labels not found")
    subset = x.loc[x.original_fuel_category.isin([OTHER, PETROLEUM])].copy()
    counts = subset.groupby(["ba", "utc_hour_start"]).size()
    if len(counts) != 4 * N or not counts.eq(2).all():
        raise ValueError("Other/Petroleum source categories not rectangular")
    subset["value"] = subset.reported_fuel_mwh.where(subset.reported)
    values = subset.pivot(index=["ba", "utc_hour_start"],
                          columns="original_fuel_category",
                          values="value").reset_index()
    original = six.copy()
    original["utc_hour_start"] = pd.to_datetime(original.utc_hour_start, utc=True)
    needed = ["ba", "utc_hour_start", "net_generation_mw",
              "all_six_original_components_numeric",
              "sum_six_original_reported_components_mwh"]
    if not set(needed).issubset(original.columns):
        raise ValueError("Missing six-category source baseline")
    if original.duplicated(["ba", "utc_hour_start"]).any():
        raise ValueError("Duplicate six-category key")
    out = original[needed].merge(values, on=["ba", "utc_hour_start"],
                                 how="outer", validate="one_to_one", indicator=True)
    if len(out) != 4 * N or not out["_merge"].eq("both").all():
        raise ValueError("Non-identical source six-fuel and extra-category cohorts")
    out.drop(columns="_merge", inplace=True)
    complete = out.all_six_original_components_numeric.astype(str).str.lower()
    if not complete.isin(["true", "false"]).all():
        raise ValueError("Invalid six-category completeness flag")
    out["six_numeric"] = complete.eq("true")
    out["seven_numeric"] = (out.six_numeric & out[OTHER].notna() &
                            out.net_generation_mw.notna() &
                            out.sum_six_original_reported_components_mwh.notna())
    out["eight_numeric"] = out.seven_numeric & out[PETROLEUM].notna()
    out["net_minus_six_mwh"] = (out.net_generation_mw -
                                out.sum_six_original_reported_components_mwh).where(out.six_numeric)
    out["net_minus_six_plus_other_mwh"] = (
        out.net_minus_six_mwh - out[OTHER]).where(out.seven_numeric)
    out["net_minus_six_plus_other_petroleum_mwh"] = (
        out.net_minus_six_plus_other_mwh - out[PETROLEUM]).where(out.eight_numeric)
    # Avoid interpreting signed weekly cancellation as hourly reconciliation.
    # Missing source hours stay null and are excluded from all discrepancy counts.
    for level in ("seven", "eight"):
        col = "net_minus_six_plus_other_mwh" if level == "seven" else "net_minus_six_plus_other_petroleum_mwh"
        out[f"{level}_hour_abs_difference_mwh"] = out[col].abs()
        out[f"{level}_hour_nonzero_difference"] = out[col].abs().gt(1e-9).where(out[col].notna())
    out["all_16_categories_certified_complete"] = False
    out["difference_is_not_unserved_energy_or_EENS"] = True
    summary = out.groupby("ba", as_index=False).agg(
        hours=("utc_hour_start", "size"),
        six_numeric_hours=("six_numeric", "sum"),
        seven_numeric_hours=("seven_numeric", "sum"),
        eight_numeric_hours=("eight_numeric", "sum"),
        signed_seven_difference_mwh=("net_minus_six_plus_other_mwh",
                                     lambda v: v.sum(min_count=1)),
        abs_seven_difference_mwh=("net_minus_six_plus_other_mwh",
                                  lambda v: v.abs().sum(min_count=1)),
        signed_eight_difference_mwh=("net_minus_six_plus_other_petroleum_mwh",
                                     lambda v: v.sum(min_count=1)),
        abs_eight_difference_mwh=("net_minus_six_plus_other_petroleum_mwh",
                                  lambda v: v.abs().sum(min_count=1)),
        nonzero_seven_hours=("seven_hour_nonzero_difference",
                             lambda v: int(v.sum()) if v.notna().any() else None),
        nonzero_eight_hours=("eight_hour_nonzero_difference",
                             lambda v: int(v.sum()) if v.notna().any() else None),
        max_abs_seven_hour_mwh=("seven_hour_abs_difference_mwh", "max"),
        max_abs_eight_hour_mwh=("eight_hour_abs_difference_mwh", "max")))
    return out, summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fuel", required=True)
    p.add_argument("--six", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    hourly, summary = reconcile(pd.read_csv(args.fuel), pd.read_csv(args.six))
    dest = Path(args.output)
    dest.mkdir(parents=True, exist_ok=True)
    hourly.to_csv(dest / "paper_c_2024_161h_source_seven_eight_hourly.csv", index=False)
    summary.to_csv(dest / "paper_c_2024_161h_source_seven_eight_summary.csv", index=False)
    (dest / "paper_c_2024_161h_source_seven_eight_scope.json").write_text(
        json.dumps({"source": "original EIA-930 2024 Jul-Dec modern fuel taxonomy",
                    "hours_per_BA": N, "original_blanks_never_zero": True,
                    "full_16_fuel_closure_certified": False,
                    "not_outages_or_EENS": True}, indent=2) + "\n")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
