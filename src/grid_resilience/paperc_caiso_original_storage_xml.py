"""Read original CAISO 2023/24 Q2/Q3 storage market_output XLSX via streamed XML.

CAISO source workbooks falsely declare first-cell dimensions; read physical
worksheet XML rows, not library-reported sheet.max_row. Dates in local CAISO
trade time and UTC source cohort are separated. This is market output, not
metered battery discharge, measured physical SOC, or outage/EENS.
"""
import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree.ElementTree import fromstring, iterparse
from zipfile import ZipFile

import pandas as pd

N="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
HEAD=("TRADE_DATE","HOUR","INTERVAL","MARKET","RES_TYPE","TYPE","VALUE")
COHORT={2023:("2023-07-10T00:00:00Z","2023-07-17T00:00:00Z"),
        2024:("2024-07-01T00:00:00Z","2024-07-08T00:00:00Z")}
MARKETS={"IFM","RUC","RTPD","RTD"}
TYPES={"EN","SOC","RU","RD","SR","NR"}
RESOURCES={"LESR","HYBD"}
# Column A numeric date is Excel 1900-epoch serial, *trade date* not UTC.
EXCEL_BASE=datetime(1899,12,30)


def shared_strings(z):
    raw=z.read("xl/sharedStrings.xml")
    root=fromstring(raw)
    return ["".join(x.text or "" for x in node.iter(N+"t"))
            for node in root.findall(N+"si")]


def raw_rows(path):
    """Yield full physical market_output XML rows, ignoring incorrect dimension A1."""
    with ZipFile(path) as z:
        strings=shared_strings(z)
        with z.open("xl/worksheets/sheet1.xml") as infile:
            root=None
            for event,elem in iterparse(infile,events=("start","end")):
                if root is None and event=="start":root=elem
                if event!="end" or elem.tag!=N+"row":continue
                cells={}
                for c in elem.findall(N+"c"):
                    key=re.match(r"[A-Z]+",c.attrib.get("r",""))
                    if key is None:continue
                    v=c.find(N+"v")
                    raw=v.text if v is not None else None
                    if raw is not None and c.attrib.get("t")=="s":
                        raw=strings[int(raw)]
                    cells[key.group()]=raw
                yield cells
                if root is not None:root.clear()


def audit(files):
    evidence=[]
    output=[]
    for year,parts in sorted(files.items()):
        if set(parts)!=({2023:{"Q3"},2024:{"Q2","Q3"}}[year]):
            raise ValueError("Incomplete date-spanning official quarter source list")
        start=pd.Timestamp(COHORT[year][0])
        finish=pd.Timestamp(COHORT[year][1])
        for quarter,path in sorted(parts.items()):
            p=Path(path)
            if not p.exists():raise ValueError("Missing original CAISO file")
            sourcehash=hashlib.sha256(p.read_bytes()).hexdigest()
            count=0
            matches=0
            source_dates=set()
            markets=Counter()
            kinds=Counter()
            headers_ok=False
            for row in raw_rows(p):
                count+=1
                if count==1:
                    if tuple(row.get(x) for x in "ABCDEFG")!=HEAD:
                        raise ValueError("Unexpected actual worksheet XML header")
                    headers_ok=True
                    continue
                if not row.get("A"):continue
                serial=float(row["A"])
                trade_date=(EXCEL_BASE+timedelta(days=int(serial))).date()
                source_dates.add(str(trade_date))
                # Skip data well outside the desired two official UTC weeks.
                if not (pd.Timestamp(start.date())-pd.Timedelta(days=1)).date()<=trade_date<=finish.date():
                    continue
                hour=int(float(row["B"]))
                interval=int(float(row["C"]))
                if not 1<=hour<=25 or interval<1:raise ValueError("Invalid original trading hour/interval")
                local=pd.Timestamp(trade_date)+pd.Timedelta(hours=hour-1)
                local=local.tz_localize("America/Los_Angeles",ambiguous="raise",
                                        nonexistent="raise")
                utc=local.tz_convert("UTC")
                if not start<=utc<finish:continue
                market=row.get("D")
                res=row.get("E")
                typ=row.get("F")
                val=row.get("G")
                if market not in MARKETS or res not in RESOURCES or typ not in TYPES:
                    raise ValueError("Unexpected CAISO market/resource/type")
                if not val:raise ValueError("Blank selected market output not safely imputable")
                number=float(val)
                if not pd.notna(number) or number in (float("inf"),float("-inf")):
                    raise ValueError("Nonfinite original CAISO output")
                output.append({"eia930_study_year":year,"quarter":quarter,
                    "caiso_trade_date_local":str(trade_date),
                    "caiso_hour_ending_local":hour,"interval_index":interval,
                    "utc_hour_start_from_local_trade_date":utc.isoformat(),
                    "market":market,"resource_type":res,"output_type":typ,
                    "original_market_value":number,
                    "original_value_is_not_metered_power_or_soc":True})
                matches+=1
                markets[market]+=1
                kinds[typ]+=1
            if not headers_ok:raise ValueError("No CAISO worksheet header parsed")
            item={"year":year,"source_quarter":quarter,
                  "original_source_sha256":sourcehash,
                  "physical_xml_rows_including_header":count,
                  "earliest_local_trade_date":min(source_dates),
                  "latest_local_trade_date":max(source_dates),
                  "selected_study_window_market_output_rows":matches,
                  "selected_by_market":dict(markets),
                  "selected_by_type":dict(kinds),
                  "quarterly_source_data_not_settlement_quality":True}
            evidence.append(item)
            print("CAISO SOURCE XML RESULT",json.dumps(item))
    d=pd.DataFrame(output)
    if d.empty:raise ValueError("Zero admitted CAISO records")
    if d.duplicated(["eia930_study_year","utc_hour_start_from_local_trade_date",
                     "market","resource_type","output_type","interval_index"]).any():
        raise ValueError("Duplicate source key in source market-output panel")
    overview=d.groupby(["eia930_study_year","market","resource_type","output_type"],
                       as_index=False).agg(
        selected_source_rows=("original_market_value","size"),
        unique_utc_hours=("utc_hour_start_from_local_trade_date","nunique"),
        min_original_value=("original_market_value","min"),
        max_original_value=("original_market_value","max"))
    metadata={"original_source":evidence,
        "desired_study_hours_each":168,
        "target_caiso_ba_only_other_three_bas_not_recovered":True,
        "utc_hour_join_uses_los_angeles_summer_dst":True,
        "market_result_source_not_actual_metered_charge_discharge":True,
        "market_soc_not_proven_measured_physical_energy_state":True,
        "no_eia930_raw_storage_null_imputation":True,
        "historical_outage_or_eens_calibrated":False}
    return d,overview,metadata


def main():
    p=argparse.ArgumentParser()
    for arg in ("q3_2023","q2_2024","q3_2024","output"):
        p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    d,s,m=audit({2023:{"Q3":a.q3_2023},
                 2024:{"Q2":a.q2_2024,"Q3":a.q3_2024}})
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    d.to_csv(out/"paperc_caiso_original_market_output_2023_2024_study_weeks.csv",index=False)
    s.to_csv(out/"paperc_caiso_original_market_output_coverage_by_market_type.csv",index=False)
    (out/"paperc_caiso_original_market_output_scope_and_sha256.json").write_text(
        json.dumps(m,indent=2)+"\n")
    print("CAISO ORIGINAL STUDY MARKET SOURCE COVERAGE")
    print(s.to_string(index=False))


if __name__=="__main__":main()
