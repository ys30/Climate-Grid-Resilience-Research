"""Probe the original USACE Grand Coulee historic daily pumping report.

The current USACE 30-day report has Banks Lake Pump kcfs/MWh, but it
might not allow 2024 via month-back parameter. Refuse pretending a
current table represents July 2024. Archive returned response and hash.
"""
import argparse,hashlib,json,re
from pathlib import Path
from urllib.request import urlopen,Request

BASE="https://public.crohms.org/dd/nwdp/project_daily/webexec/rep"
URLS=[
  BASE+"?ago=28&r=gcl",
  BASE+"?r=gcl&ago=28"
]
def probe(out):
    root=Path(out);root.mkdir(parents=True,exist_ok=True)
    results=[]
    for i,url in enumerate(URLS):
        try:
            with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0 research source verification"}),timeout=60) as r:
                blob=r.read()
            text=blob.decode("utf-8",errors="replace")
            (root/f"usace_grand_coulee_2024_july_probe_{i}_original.html").write_bytes(blob)
            # Avoid 2024 incidental timestamps in metadata; demand title.
            title=re.search(r"(?is)(?:Grand Coulee Dam|Grand Coulee Daily).{0,1200}?July\s+2024",text)
            result={"url":url,"original_bytes":len(blob),
               "original_sha256":hashlib.sha256(blob).hexdigest(),
               "historic_july_2024_page_heading_verified":bool(title),
               "has_Banks_Lake_Pump_MWh_header":"Banks Lake Pump MWh" in text,
               "has_Banks_Lake_Pump_kcfs_header":"Banks Lake Pump kcfs" in text,
               "july_2024_rows_admitted":False,
               "source_response_not_used_as_real_2024_pumping_MWh":True,
               "visible_heading_context":re.findall(r"(?is)<h[1-4][^>]*>.*?</h[1-4]>",text)[:6]}
        except Exception as ex:
            result={"url":url,"failed_closed":True,"error":str(ex)}
        results.append(result)
    manifest={"candidates":results,
        "any_original_2024_july_usace_pumping_observed":False,
        "no_pumping_data_2024_calibrated":True,
        "request_restricted_to_official_USACE":True}
    (root/"usace_grand_coulee_2024_july_historical_access_gate.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
    if not any(r.get("historic_july_2024_page_heading_verified") and r.get("has_Banks_Lake_Pump_MWh_header") for r in results):
        raise ValueError("Original USACE daily report not certified for historical July 2024: source gate closed")

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    probe(p.parse_args().output)
