"""Source-native reciprocal directed EIA-930 interchange audit, July 2024 UTC.

Compare A->B and B->A only where both directional source values exist.
An absent direction, blank cell, or counterparty's unverified reporting scope
is NOT equivalent to physical non-delivery or zero energy flow.
"""
import argparse
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import math
import pandas as pd
from .eia930_fuel_decomposition import FMT

BAS=("AZPS","BPAT","CISO","SRP")
NEEDED={"Balancing Authority","Directly Interconnected Balancing Authority",
        "UTC Time at End of Hour","Interchange (MW)"}


def read(path, start, end):
    rows={}
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if not NEEDED.issubset(reader.fieldnames or []):
            raise ValueError("Missing original EIA930 bilateral columns")
        for r in reader:
            a=r["Balancing Authority"].strip()
            b=r["Directly Interconnected Balancing Authority"].strip()
            if not a or not b or a==b:
                continue
            if a not in BAS and b not in BAS:
                continue
            t=datetime.strptime(r["UTC Time at End of Hour"].strip(),FMT).replace(
                tzinfo=timezone.utc)-timedelta(hours=1)
            if not start<=t<end:continue
            key=(t,a,b)
            if key in rows:raise ValueError("Duplicate directional BA/hour/counterparty")
            raw=r["Interchange (MW)"].strip()
            v=float(raw) if raw else None
            if v is not None and not math.isfinite(v):
                raise ValueError("Nonfinite bilateral interchange")
            rows[key]=v
    return rows


def audit(first,second,start="2024-07-01T00:00:00Z"):
    t=pd.Timestamp(start)
    if t.year!=2024 or t.tzinfo is None or t.utcoffset()!=pd.Timedelta(0):
        raise ValueError("UTC 2024 cohort required")
    lo=t.to_pydatetime()
    hi=lo+timedelta(hours=168)
    old=read(first,lo,hi)
    new=read(second,lo,hi)
    if set(old)&set(new):raise ValueError("Repeated directional pair across archive halves")
    data={**old,**new}
    keys={(t,*sorted((a,b))) for t,a,b in data}
    items=[]
    for hour,a,b in sorted(keys):
        forward=data.get((hour,a,b))
        backward=data.get((hour,b,a))
        found_forward=(hour,a,b) in data
        found_backward=(hour,b,a) in data
        complete=found_forward and found_backward and forward is not None and backward is not None
        raw_sum=forward+backward if complete else None
        items.append({"utc_hour_start":hour.isoformat(),"ba_a":a,"ba_b":b,
                      "both_ba_in_selected_four":a in BAS and b in BAS,
                      "a_reports_b":found_forward,"b_reports_a":found_backward,
                      "a_to_b_reported_mw":forward,"b_to_a_reported_mw":backward,
                      "both_direction_values_present":bool(complete),
                      "signed_reciprocity_sum_mw":raw_sum,
                      "absolute_reciprocity_sum_mw":abs(raw_sum) if complete else None,
                      "reciprocity_within_1mw":bool(complete and abs(raw_sum)<=1),
                      "transmission_rating_or_power_flow_verified":False})
    detail=pd.DataFrame(items)
    if detail.empty:raise ValueError("No original directed interchange for target BAs")
    summary=[]
    for (a,b),g in detail.groupby(["ba_a","ba_b"],sort=True):
        v=g.absolute_reciprocity_sum_mw.dropna()
        summary.append({"ba_a":a,"ba_b":b,
            "observed_pair_hour_keys":len(g),
            "both_directions_reported_hours":int(g.both_direction_values_present.sum()),
            "only_one_direction_or_blank_hours":int((~g.both_direction_values_present).sum()),
            "reciprocity_within_1mw_hours":int(g.reciprocity_within_1mw.sum()),
            "absolute_reciprocity_deviation_valid_hours_mwh":float(v.sum()),
            "maximum_absolute_reciprocity_deviation_mw":float(v.max()) if len(v) else None,
            "is_internal_selected_four_pair":bool(a in BAS and b in BAS),
            "physical_intertie_capacity_verified":False})
    manifest={"window":"2024-07-01/07 UTC","source_halfyear_files":2,
              "directed_source_rows_old":len(old),"directed_source_rows_new":len(new),
              "unordered_pair_hour_keys":len(detail),"pair_groups":len(summary),
              "counterparties_outside_four_ba_included":True,
              "missing_direction_never_converted_to_zero":True,
              "bilateral_reciprocity_is_not_thermal_limit_or_adequacy":True,
              "historical_eens_validated":False}
    return detail,pd.DataFrame(summary),manifest


def main():
    p=argparse.ArgumentParser()
    for k in ("jan-jun","jul-dec","output"):
        p.add_argument("--"+k,required=True)
    a=p.parse_args()
    d,s,m=audit(a.jan_jun,a.jul_dec)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    d.to_csv(out/"july2024_reciprocal_directed_pair_hourly.csv",index=False)
    s.to_csv(out/"july2024_reciprocal_directed_pair_summary.csv",index=False)
    (out/"july2024_reciprocity_source_scope.json").write_text(json.dumps(m,indent=2)+"\n")
    print(s.to_string(index=False))
    print(json.dumps(m,indent=2))

if __name__=="__main__":main()
