"""Compare official directed EIA-930 bilateral entries and reported BA net interchange.

July 1–7 UTC straddles semiannual file partitions. Missing bilateral data
never becomes zero flow. Sum of reporting counterparties is only an EIA
reporting-accounting diagnostic, not a transmission or plant-flow model.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from .eia930_fuel_decomposition import FMT

BAS = ("AZPS", "BPAT", "CISO", "SRP")
BALANCE_FIELD = "Total Interchange (MW)"
INTERCHANGE_FIELD = "Interchange (MW)"
BA_COL = "Balancing Authority"
PARTNER_COL = "Directly Interconnected Balancing Authority"
TIME_COL = "UTC Time at End of Hour"


def _hour(raw):
    return datetime.strptime(raw.strip(), FMT).replace(
        tzinfo=timezone.utc) - timedelta(hours=1)


def _read_balance(path, label, start, stop):
    found = {}
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {BA_COL, TIME_COL, BALANCE_FIELD}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Missing official BA total interchange columns")
        for row in reader:
            ba = row[BA_COL].strip()
            if ba not in BAS:
                continue
            t = _hour(row[TIME_COL])
            if not start <= t < stop:
                continue
            key = t, ba
            if key in found:
                raise ValueError("Duplicate balance BA/hour within " + label)
            s = row[BALANCE_FIELD].strip()
            v = float(s) if s else None
            if v is not None and not math.isfinite(v):
                raise ValueError("Nonfinite reported total interchange")
            found[key] = v
    return found


def _read_bilateral(path, label, start, stop):
    flow = defaultdict(float)
    counterparts = defaultdict(set)
    blank = set()
    records = 0
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {BA_COL, TIME_COL, PARTNER_COL, INTERCHANGE_FIELD}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Missing official bilateral interchange columns")
        for row in reader:
            ba = row[BA_COL].strip()
            if ba not in BAS:
                continue
            t = _hour(row[TIME_COL])
            if not start <= t < stop:
                continue
            partner = row[PARTNER_COL].strip()
            if not partner:
                raise ValueError("Empty bilateral counterparty")
            key = t, ba
            if partner in counterparts[key]:
                raise ValueError("Duplicate BA/hour/counterparty within " + label)
            counterparts[key].add(partner)
            s = row[INTERCHANGE_FIELD].strip()
            if s:
                v = float(s)
                if not math.isfinite(v):
                    raise ValueError("Nonfinite bilateral flow")
                flow[key] += v
            else:
                blank.add(key)
            records += 1
    return flow, counterparts, blank, records


def audit(balance_halves, bilateral_halves, start="2024-07-01T00:00:00Z"):
    if set(balance_halves) != {"Jan_Jun", "Jul_Dec"} or set(bilateral_halves) != {"Jan_Jun", "Jul_Dec"}:
        raise ValueError("Require both official source partitions for both report families")
    beginning = pd.Timestamp(start)
    if beginning.tzinfo is None or beginning.utcoffset() != pd.Timedelta(0) or beginning.year != 2024:
        raise ValueError("Explicit 2024 UTC window required")
    lo = beginning.to_pydatetime()
    hi = lo + timedelta(hours=168)
    balance = {}
    flow = {}
    partners = {}
    blank = set()
    files = []
    for part in ("Jan_Jun", "Jul_Dec"):
        part_balance = _read_balance(balance_halves[part], part, lo, hi)
        overlap = set(balance) & set(part_balance)
        if overlap:
            raise ValueError("BA totals overlap across source partitions")
        balance.update(part_balance)
        part_flow, part_partners, part_blank, n = _read_bilateral(bilateral_halves[part], part, lo, hi)
        overlap = set(partners) & set(part_partners)
        if overlap:
            raise ValueError("Bilateral BA/hour overlaps across source partitions")
        flow.update(part_flow)
        partners.update(part_partners)
        blank.update(part_blank)
        files.append({"partition": part, "balance_ba_hours": len(part_balance),
                      "bilateral_counterparty_rows": n,
                      "bilateral_ba_hours": len(part_partners)})
    expected = {(lo + timedelta(hours=h), ba) for h in range(168) for ba in BAS}
    if set(balance) != expected:
        raise ValueError(f"Incomplete original BALANCE BA-hour grid: {len(balance)}/672")
    if set(partners) - expected:
        raise ValueError("Unexpected BILATERAL BA-hour records")
    rows = []
    for t, ba in sorted(expected):
        key = t, ba
        bil_present = key in partners
        bil_complete = bil_present and key not in blank
        total = balance[key]
        summed = flow.get(key) if bil_complete else None
        matched = total is not None and bil_complete
        diff = summed - total if matched else None
        rows.append({
            "utc_hour_start": t.isoformat(), "ba": ba,
            "reported_total_interchange_mw": total,
            "balance_total_interchange_reported": total is not None,
            "bilateral_ba_hour_present": bil_present,
            "bilateral_counterparty_rows": len(partners.get(key, ())),
            "bilateral_all_present_counterparty_values_reported": bil_complete,
            "sum_reported_bilateral_mw": summed,
            "bilateral_minus_reported_total_mw": diff,
            "total_missing_but_bilateral_present": total is None and bil_complete,
            "pair_fully_reported": matched,
            "hourly_reporting_agreement_within_1mw":
                abs(diff) <= 1 if matched else False,
            "physical_transfer_capacity_validated": False
        })
    detail = pd.DataFrame(rows)
    summary = []
    for ba, group in detail.groupby("ba", sort=True):
        diffs = group.bilateral_minus_reported_total_mw.dropna()
        summary.append({
            "ba": ba, "expected_ba_hours": len(group),
            "reported_total_interchange_hours": int(group.balance_total_interchange_reported.sum()),
            "missing_total_interchange_hours": int((~group.balance_total_interchange_reported).sum()),
            "bilateral_any_counterparty_hours": int(group.bilateral_ba_hour_present.sum()),
            "bilateral_all_present_counterparty_values_hours": int(
                group.bilateral_all_present_counterparty_values_reported.sum()),
            "missing_total_but_bilateral_observed_hours": int(
                group.total_missing_but_bilateral_present.sum()),
            "matched_reported_hours": len(diffs),
            "matched_hours_within_1mw": int(group.hourly_reporting_agreement_within_1mw.sum()),
            "matched_signed_difference_mwh": float(diffs.sum()),
            "matched_absolute_difference_mwh": float(diffs.abs().sum()),
            "matched_max_absolute_difference_mw": float(diffs.abs().max()) if len(diffs) else None,
            "source_total_interchange_imputed": False,
            "bilateral_is_physical_transfer_capacity": False
        })
    manifest = {
        "period": "2024-07-01 to 2024-07-08 UTC exclusive",
        "full_original_balance_ba_hour_grid": True,
        "bilateral_absence_never_zero": True,
        "missing_raw_total_interchange_never_replaced_with_bilateral": True,
        "bilateral_complete_counterparty_universe_verified": False,
        "bilateral_sign_convention_or_reciprocity_physically_verified": False,
        "hourly_interchange_suffices_for_transfer_rating": False,
        "historical_grid_adequacy_or_eens_validated": False,
        "files": files
    }
    return detail, pd.DataFrame(summary), manifest


def main():
    p = argparse.ArgumentParser()
    for name in ("balance-jan-jun", "balance-jul-dec",
                 "interchange-jan-jun", "interchange-jul-dec", "output"):
        p.add_argument("--" + name, required=True)
    a = p.parse_args()
    b = {"Jan_Jun": a.balance_jan_jun, "Jul_Dec": a.balance_jul_dec}
    i = {"Jan_Jun": a.interchange_jan_jun, "Jul_Dec": a.interchange_jul_dec}
    detail, summary, manifest = audit(b, i)
    dest = Path(a.output)
    dest.mkdir(parents=True, exist_ok=True)
    detail.to_csv(dest / "july2024_168h_bilateral_vs_reported_total_hourly.csv", index=False)
    summary.to_csv(dest / "july2024_168h_bilateral_vs_reported_total_by_ba.csv", index=False)
    (dest / "july2024_168h_bilateral_scope.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
