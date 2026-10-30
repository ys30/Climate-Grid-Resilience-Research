"""Fail-closed comparison of independently prepared observed and simulated generation.

Inputs are BA/technology/period aggregate MWh, not raw EIA-923 spreadsheets.
A crosswalk, technology definitions and complete period coverage must be
audited upstream. This module does not assert that EIA-923 validates a BA map.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

KEYS = ["ba", "technology", "period"]
VALUE = "generation_mwh"

def _load(path, label):
    frame = pd.read_csv(path, dtype={"ba": str, "technology": str, "period": str})
    needed = set(KEYS + [VALUE])
    if not needed.issubset(frame.columns):
        raise ValueError(f"{label}: missing {sorted(needed - set(frame.columns))}")
    if frame.empty or frame[KEYS].isna().any().any():
        raise ValueError(f"{label}: empty or null group labels")
    for col in KEYS:
        frame[col] = frame[col].str.strip()
        if frame[col].eq("").any():
            raise ValueError(f"{label}: blank {col}")
    if frame.duplicated(KEYS).any():
        raise ValueError(f"{label}: duplicate BA/technology/period")
    frame[VALUE] = pd.to_numeric(frame[VALUE], errors="raise")
    if frame[VALUE].isna().any() or not frame[VALUE].map(
        lambda x: -float("inf") < float(x) < float("inf")
    ).all():
        raise ValueError(f"{label}: nonfinite generation")
    # Negative net generation is physically possible for some metering
    # conventions, so it is retained rather than silently clamped.
    return frame[KEYS + [VALUE]]

def compare(observed_csv, modeled_csv, output_dir, *, allow_negative=True):
    obs = _load(observed_csv, "observed")
    sim = _load(modeled_csv, "modeled")
    if not allow_negative and ((obs[VALUE] < 0).any() or (sim[VALUE] < 0).any()):
        raise ValueError("Negative generation excluded by configuration")
    joined = obs.merge(sim, on=KEYS, how="outer", suffixes=("_observed", "_modeled"),
                       indicator=True, validate="one_to_one")
    if not joined._merge.eq("both").all():
        missing = joined.loc[joined._merge != "both", KEYS + ["_merge"]]
        raise ValueError("Incomplete matched generation coverage: " +
                         missing.head(8).to_json(orient="records"))
    joined = joined.drop(columns="_merge")
    joined["error_mwh"] = joined.generation_mwh_modeled - joined.generation_mwh_observed
    joined["absolute_error_mwh"] = joined.error_mwh.abs()
    # Weighted absolute percentage error (WAPE) is withheld if the
    # observed absolute-generation denominator is zero.
    def summarize(group):
        denominator = float(group.generation_mwh_observed.abs().sum())
        abs_error = float(group.absolute_error_mwh.sum())
        return pd.Series({
            "n_periods": len(group),
            "observed_mwh": float(group.generation_mwh_observed.sum()),
            "modeled_mwh": float(group.generation_mwh_modeled.sum()),
            "bias_mwh": float(group.error_mwh.sum()),
            "mae_mwh_per_period": float(group.absolute_error_mwh.mean()),
            "wape": abs_error / denominator if denominator > 0 else float("nan"),
        })
    summary = joined.groupby(["ba", "technology"], sort=True)[
        ["generation_mwh_observed", "generation_mwh_modeled", "error_mwh", "absolute_error_mwh"]
    ].apply(summarize).reset_index()
    overall = summarize(joined)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    joined.sort_values(KEYS).to_csv(out / "generation_matched.csv", index=False)
    summary.to_csv(out / "generation_calibration_summary.csv", index=False)
    metadata = {
        "status": "diagnostic_comparison_only",
        "comparison_rows": len(joined),
        "ba_count": int(joined.ba.nunique()),
        "technologies": sorted(joined.technology.unique().tolist()),
        "periods": sorted(joined.period.unique().tolist()),
        "aggregate_bias_mwh": float(overall["bias_mwh"]),
        "aggregate_mae_mwh_per_cell": float(overall["mae_mwh_per_period"]),
        "aggregate_wape": None if pd.isna(overall["wape"]) else float(overall["wape"]),
        "historical_calibration_certified": False,
        "caveats": [
            "BA/technology classification, time aggregation, EIA-923 plant crosswalk and net/gross conventions must be audited upstream.",
            "Matching periods does not independently establish grid topology, transmission ratings, hourly availability, or predictive validity.",
            "Do not compare a thermal/wind-only model with a full-fleet observed inventory as though complete."
        ],
    }
    (out / "generation_calibration_manifest.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    return metadata

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--observed", required=True)
    parser.add_argument("--modeled", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--reject-negative", action="store_true")
    args = parser.parse_args()
    print(json.dumps(compare(args.observed, args.modeled, args.output,
                             allow_negative=not args.reject_negative), indent=2))

if __name__ == "__main__":
    main()
