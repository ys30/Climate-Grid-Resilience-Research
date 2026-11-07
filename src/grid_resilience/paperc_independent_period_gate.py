"""Fail-closed seasonal/year holdout admission for Paper C four-BA sources.

An independent held-out PERIOD requires complete source inputs in a distinct
season or year and no overlapping hours. This does not establish statistically
independent weather events or physically calibrated electric adequacy.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

BAS = {"AZPS", "BPAT", "CISO", "SRP"}
SEASONS = {12: "DJF", 1: "DJF", 2: "DJF", 3: "MAM", 4: "MAM",
           5: "MAM", 6: "JJA", 7: "JJA", 8: "JJA",
           9: "SON", 10: "SON", 11: "SON"}


def inspect_window(window_id, demand, weather, capacity, source_evidence):
    if not window_id or not isinstance(source_evidence, dict):
        raise ValueError("Window ID and explicit source evidence are required")
    if not all(source_evidence.get(k) is True for k in
               ("official_hour_start_demand", "documented_weather_source",
                "frozen_capacity_convention", "source_provenance_available")):
        raise ValueError("Source provenance or hour convention not admitted")
    expected = {"timestamp", "ba"}
    for label, frame in (("demand", demand), ("weather", weather)):
        if not expected.issubset(frame.columns):
            raise ValueError(f"Missing {label} time and BA keys")
    if "ba" not in capacity or len(capacity) != 4 or capacity.ba.duplicated().any() or set(capacity.ba) != BAS:
        raise ValueError("Incomplete frozen four-BA capacity source")
    d, w = demand.copy(), weather.copy()
    for f in (d,w):
        f["timestamp"] = pd.to_datetime(f.timestamp, utc=True, errors="raise")
        if f.duplicated(["timestamp", "ba"]).any():
            raise ValueError("Duplicate BA-hour source")
    dates = pd.DatetimeIndex(sorted(d.timestamp.unique()))
    if len(dates) != 168 or len(d) != 672 or len(w) != 672:
        raise ValueError("Independent candidate must contain 168 hours x four BA")
    expected_time = pd.date_range(dates[0], periods=168, freq="h")
    if not dates.equals(expected_time):
        raise ValueError("Candidate has missing or noncontiguous hours")
    grid = pd.MultiIndex.from_product([expected_time, sorted(BAS)], names=["timestamp", "ba"])
    for f in (d, w):
        rows = pd.MultiIndex.from_frame(f[["timestamp", "ba"]])
        if len(rows) != len(grid) or not rows.isin(grid).all() or len(rows.unique()) != len(grid):
            raise ValueError("Incomplete or mismatched four-BA source grid")
    if set(d.columns) >= {"demand_mw"}:
        numeric = pd.to_numeric(d.demand_mw, errors="coerce")
        if numeric.isna().any() or numeric.lt(0).any():
            raise ValueError("Invalid demand observation")
    # Require each 168h window within a single meteorological season/year.
    # December belongs to the following DJF season-year.
    season_ids = {(int(t.year) + (1 if t.month == 12 else 0), SEASONS[t.month]) for t in dates}
    if len(season_ids) != 1:
        raise ValueError("Candidate crosses a meteorological season boundary")
    season_year, season = next(iter(season_ids))
    return {"window_id": window_id, "start_utc": dates[0].isoformat(),
            "end_utc": dates[-1].isoformat(), "unique_utc_hours": 168,
            "ba_hour_rows": 672, "calendar_year": int(dates[0].year),
            "meteorological_season": season,
            "meteorological_season_year": season_year,
            "source_admitted_for_period_comparison": True,
            "source_hour_start_verified_by_manifest": True,
            "real_available_generator_mw_verified": False,
            "statistically_independent_climate_event_verified": False,
            "historical_eens_validated": False}


def audit_periods(records):
    if not records:
        raise ValueError("No periods")
    if len({r["window_id"] for r in records}) != len(records):
        raise ValueError("Duplicate period ID")
    ordered = sorted(records, key=lambda r: r["start_utc"])
    for left, right in zip(ordered, ordered[1:]):
        if pd.Timestamp(right["start_utc"]) <= pd.Timestamp(left["end_utc"]):
            raise ValueError("Temporal source windows overlap")
    groups = {(r["meteorological_season_year"], r["meteorological_season"]) for r in records}
    years = {r["calendar_year"] for r in records}
    seasons = {r["meteorological_season"] for r in records}
    return {"candidate_windows": len(records),
            "distinct_meteorological_season_years": len(groups),
            "distinct_calendar_years": len(years),
            "different_season_candidate_available": len(seasons) >= 2,
            "different_calendar_year_candidate_available": len(years) >= 2,
            "cross_period_holdout_source_admitted": len(groups) >= 2,
            "independent_statistical_events_established": False,
            "source_supported_physical_grid_adequacy": False,
            "conclusion": ("cross-season/year source periods present, separate event/physics validation still required"
                           if len(groups) >= 2 else
                           "only within-season source windows; no independent-season/year holdout"),
            "windows": ordered}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True,help="JSON list of 168-hour source-window paths and evidence flags")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    entries=json.loads(Path(args.manifest).read_text())
    windows=[]
    for item in entries:
        windows.append(inspect_window(
            item["window_id"], pd.read_csv(item["demand"]),
            pd.read_csv(item["weather"]), pd.read_csv(item["capacity"]),
            item["source_evidence"]))
    report=audit_periods(windows)
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
