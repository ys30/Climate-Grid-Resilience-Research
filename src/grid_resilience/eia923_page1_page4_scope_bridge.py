"""Audit EIA-923 Page 1 versus Page 4 monthly plant coverage.

Page 1 uses plant/fuel/prime-mover rows; Page 4 uses generator rows.
Do not sum the two generation sources into a purported BA-wide total.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _prepare(frame, required, label):
    missing = set(required) - set(frame.columns)
    if missing:
        raise ValueError(f"{label}: missing columns {sorted(missing)}")
    d = frame.copy()
    for col in required:
        if col == "net_generation_mwh" or col == "generation_mwh":
            continue
        d[col] = d[col].astype("string").str.strip()
        if d[col].isna().any() or d[col].eq("").any():
            raise ValueError(f"{label}: missing identity {col}")
    d["plant_id"] = d.plant_id.str.replace(r"^0+(?=[0-9])", "", regex=True)
    value_column = "net_generation_mwh" if label == "page1" else "generation_mwh"
    d[value_column] = pd.to_numeric(d[value_column], errors="coerce")
    if not np.isfinite(d[value_column].to_numpy(dtype=float)).all():
        raise ValueError(f"{label}: missing or nonfinite observed generation")
    if not d.period.str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])").all():
        raise ValueError(f"{label}: invalid YYYY-MM period")
    return d


def bridge(page1, page4, *, ba="SRP", period="2024-01"):
    """Return per-source summaries and plant overlap, never combined MWh."""
    if not isinstance(ba, str) or not ba.strip():
        raise ValueError("Nonempty BA required")
    if not isinstance(period, str) or not pd.Series([period]).str.fullmatch(
        r"\d{4}-(0[1-9]|1[0-2])"
    ).all():
        raise ValueError("Invalid requested period")
    a = _prepare(
        page1,
        ("plant_id", "reported_ba", "period", "prime_mover",
         "reported_fuel", "net_generation_mwh"),
        "page1",
    )
    b = _prepare(
        page4,
        ("plant_id", "generator_id", "reported_ba", "period",
         "generation_mwh"),
        "page4",
    )
    # Page 1 legitimately permits multiple underlying records per plant/fuel/prime mover/month.
    # A 2024 SRP nuclear plant has three rows for the same visible combination.
    # Preserve source rows and report repeated coarse keys; never deduplicate or combine with Page 4.
    repeated_page1_keys = int(a.duplicated(
        ["plant_id", "reported_ba", "period", "prime_mover", "reported_fuel"],
        keep=False).sum())
    if b.duplicated(["plant_id", "generator_id", "reported_ba", "period"]).any():
        raise ValueError("Duplicate Page 4 generator/BA/month")
    a = a.loc[a.reported_ba.eq(ba) & a.period.eq(period)].copy()
    b = b.loc[b.reported_ba.eq(ba) & b.period.eq(period)].copy()
    if a.empty or b.empty:
        raise ValueError("One or both source scopes have no selected BA/month records")
    a_plants = set(a.plant_id.astype(str))
    b_plants = set(b.plant_id.astype(str))
    overlapped = sorted(a_plants & b_plants)
    rows = []
    for source, frame, metric, other_plants in (
        ("page1", a, "net_generation_mwh", b_plants),
        ("page4", b, "generation_mwh", a_plants),
    ):
        for scope, mask in (
            ("plant_present_in_other_sheet", frame.plant_id.isin(other_plants)),
            ("plant_absent_from_other_sheet", ~frame.plant_id.isin(other_plants)),
        ):
            selected = frame.loc[mask]
            rows.append({
                "source": source, "plant_overlap_scope": scope,
                "record_count": len(selected),
                "distinct_plants": int(selected.plant_id.nunique()),
                "source_only_reported_net_mwh": float(selected[metric].sum()),
            })
    summary = {
        "ba": ba, "period": period,
        "page1_source_rows": len(a),
        "page1_rows_with_repeated_coarse_keys": int(a.duplicated(
            ["plant_id", "reported_ba", "period", "prime_mover", "reported_fuel"],
            keep=False).sum()),
        "page1_coarse_key_is_unique": bool(repeated_page1_keys == 0),
        "page4_source_rows": len(b),
        "page1_unique_plants": len(a_plants),
        "page4_unique_plants": len(b_plants),
        "plants_present_in_both_sheets": len(overlapped),
        "page1_only_plants": len(a_plants - b_plants),
        "page4_only_plants": len(b_plants - a_plants),
        "page1_reported_mwh_source_only": float(a.net_generation_mwh.sum()),
        "page4_reported_mwh_source_only": float(b.generation_mwh.sum()),
        "page1_page4_sum_permitted": False,
        "duplicate_physical_generation_ruled_out": False,
        "eia930_ba_wide_calibration_certified": False,
        "historical_calibration_certified": False,
        "note": "A common plant ID does not establish duplicate physical generation; "
                "non-overlapping plant IDs do not establish comparable BA dispatch scope.",
    }
    return pd.DataFrame(rows), pd.DataFrame({"plant_id": overlapped}), summary


def main():
    parser = argparse.ArgumentParser()
    for key in ("page1", "page4", "output"):
        parser.add_argument("--" + key, required=True)
    parser.add_argument("--ba", default="SRP")
    parser.add_argument("--period", default="2024-01")
    args = parser.parse_args()
    a = pd.read_csv(args.page1, dtype={"plant_id": "string"}, keep_default_na=False)
    b = pd.read_csv(args.page4, dtype={
        "plant_id": "string", "generator_id": "string"
    }, keep_default_na=False)
    rows, overlap, summary = bridge(a, b, ba=args.ba, period=args.period)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    rows.to_csv(output / "page1_page4_source_scope_breakdown.csv", index=False)
    overlap.to_csv(output / "page1_page4_shared_plant_ids.csv", index=False)
    (output / "page1_page4_scope_manifest.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
