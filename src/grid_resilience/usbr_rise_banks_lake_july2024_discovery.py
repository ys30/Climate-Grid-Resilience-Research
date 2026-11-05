"""USBR RISE July 2024 Banks Lake daily elevation original-source admission.

Source item 129466 (BNK daily-instant elevation, ft) and item 5226
(Grand Coulee pump-generating plant UPPER POND *monthly end-of-month*
elevation, ft). The RISE download API is indexed by itemId. Download
only the actual source response. Do not invent 31 daily elevations
when the API returns a monthly data item or unavailable response.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import io
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SOURCES={
 "banks_lake_daily":{"item_id":129466,"name":"Banks Lake and Dry Falls Dam (BNK) Daily Instant Lake/Reservoir Elevation","frequency":"daily","expected_unit":"ft"},
 "keys_iii_upper_pond_monthly":{"item_id":5226,"name":"Grand Coulee Pump Generating Plant Monthly Upper Pond Elevation","frequency":"monthly_end","expected_unit":"ft"}
}
URL="https://data.usbr.gov/rise/api/result/download"

def request_url(item_id):
    return URL+"?"+urlencode({"after":"2024-06-28","before":"2024-08-04",
        "itemId":int(item_id),"type":"csv","order":"ASC"})

def inspect(data):
    if not data or len(data)<30 or len(data)>8_000_000:
        raise ValueError("Empty or unreasonable official RISE response")
    decoded=data.decode("utf-8-sig",errors="strict")
    if decoded.lstrip().startswith(("{","<","[")):
        raise ValueError("Expected CSV, received JSON/HTML/error content")
    rows=list(csv.reader(io.StringIO(decoded)))
    if len(rows)<2 or len(rows[0])<2:
        raise ValueError("RISE CSV does not contain a header plus records")
    return {"row_count_including_header":len(rows),
            "header":rows[0], "first_two_rows":rows[1:3],
            "last_two_rows":rows[-2:]}

def download(output):
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    result={}
    for key,meta in SOURCES.items():
        url=request_url(meta["item_id"])
        req=Request(url,headers={"Accept":"text/csv","User-Agent":"Research reproducibility EIA860-BPAT-PyPSA/1.0"})
        with urlopen(req,timeout=90) as response:
            raw=response.read()
        output_data=root/(key+"_original_RISE_2024.csv")
        output_data.write_bytes(raw)
        try:
            parsed=inspect(raw)
            status="source_csv_received_schema_not_yet_certified"
            error=None
        except Exception as e:
            parsed={}
            status="source_unreadable_fails_closed"
            error=f"{type(e).__name__}: {e}"
        result[key]={**meta,"source_url":url,"source_sha256":hashlib.sha256(raw).hexdigest(),
                    "original_bytes":len(raw),"status":status,
                    "parsed_source_preview":parsed,"schema_error":error,
                    "source_elevation_is_electric_usable_storage_MWh":False,
                    "water_elevation_used_for_hourly_PyPSA_calibration":False}
    (root/"usbr_rise_july2024_source_discovery_manifest.json").write_text(
         json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    if any(r["status"]!="source_csv_received_schema_not_yet_certified" for r in result.values()):
        raise ValueError("One or more original RISE source responses failed strict CSV check")
    return result

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--output",required=True)
    download(a.parse_args().output)
