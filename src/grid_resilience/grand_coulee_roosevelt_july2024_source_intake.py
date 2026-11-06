"""Source-first Grand Coulee lower-reservoir elevation audit: USGS 12436000.

Fetch July 2024 daily lake elevation 62614 as official USGS RDB and USBR
RISE item 5253 monthly forebay. Preserve raw with checksum. Daily data
may be unavailable even if site supports historic data: explicitly fail.
Do not interpret dam forebay-tailwater head as Banks Lake pump head.
"""
import argparse, hashlib, json
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode

SOURCES={
 "usgs_lake_roosevelt_daily":(
  "https://waterservices.usgs.gov/nwis/dv/?" +
  urlencode({"format":"rdb","sites":"12436000","startDT":"2024-07-01",
    "endDT":"2024-07-31","parameterCd":"62614","siteStatus":"all"})),
 "usbr_grand_coulee_monthly_forebay":(
  "https://data.usbr.gov/rise/api/result/download?"+
  urlencode({"after":"2024-06-28","before":"2024-08-04",
             "itemId":5253,"type":"csv","order":"ASC"}))
}
def fetch(dest):
    dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
    report={}
    for label,url in SOURCES.items():
        try:
            with urlopen(Request(url,headers={"User-Agent":"Academic source-data verification/1.0","Accept":"text/plain, text/csv"}),timeout=80) as r:
                raw=r.read()
            filename=label+"_2024_07_raw.txt"
            (dest/filename).write_bytes(raw)
            if not raw or len(raw)>10_000_000 or raw.lstrip()[:10].lower().startswith(b"<html"):
                raise ValueError("Original response empty, too large or HTML error")
            report[label]={"url":url,"filename":filename,
                "sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),
                "retrieval_status":"raw_download_complete_pending_observation_admission",
                "raw_preview_lines":raw.decode("utf-8-sig",errors="replace").splitlines()[:16]}
        except Exception as ex:
            report[label]={"url":url,"retrieval_status":"unavailable",
                           "error":str(ex),"not_imputed":True}
    (dest/"roosevelt_lower_reservoir_source_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if any(v.get("retrieval_status")!="raw_download_complete_pending_observation_admission" for v in report.values()):
        raise ValueError("Original lower-reservoir data missing; refuse observed head estimation")

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    fetch(p.parse_args().output)
