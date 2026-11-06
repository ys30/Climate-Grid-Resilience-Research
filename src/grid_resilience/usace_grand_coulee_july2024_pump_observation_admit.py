"""USACE Grand Coulee historic July 2024 daily pump-energy and flow observations.

USACE project-level Banks Lake Pump MWh and kcfs include plant-level
pumping activity. Do not assign this to the six reversible PS units
rather than six dedicated pumps. Missing daily fields remain NaN; no
cumulative July total reported unless 31 genuine rows are present.
"""
import argparse,hashlib,json,re
from pathlib import Path
from html.parser import HTMLParser
import pandas as pd

class Rows(HTMLParser):
    def __init__(self):
        super().__init__();self.rows=[];self.row=None;self.cell=None;self.in_table=0
    def handle_starttag(self,tag,attrs):
        if tag=="table":self.in_table+=1
        elif self.in_table and tag=="tr":self.row=[]
        elif self.in_table and tag in ("th","td") and self.row is not None:self.cell=[]
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ("th","td") and self.cell is not None and self.row is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell=None
        elif tag=="tr" and self.row is not None:
            self.rows.append(self.row);self.row=None
        elif tag=="table":self.in_table=max(0,self.in_table-1)

def admit(raw):
    content=Path(raw).read_bytes()
    txt=content.decode("utf-8",errors="strict")
    if not re.search(r"(?is)<h2[^>]*>\s*July\s+2024\s*</h2>",txt):
        raise ValueError("USACE historic report not specifically July 2024")
    parser=Rows();parser.feed(txt)
    head_candidates=[(i,row) for i,row in enumerate(parser.rows)
        if "Day of Month" in row and "Banks Lake Pump MWh" in row and
        "Banks Lake Pump kcfs" in row and "Banks Lake Elev" in row]
    if len(head_candidates)!=1:
        raise ValueError("USACE original pump reporting header missing or ambiguous")
    ix,headers=head_candidates[0]
    if len(headers)!=len(set(headers)):
        raise ValueError("Ambiguous USACE report labels")
    data=[]
    for row in parser.rows[ix+1:]:
        if row and row[0]=="1" and data:
            break
        if row and re.fullmatch(r"\d{1,2}",row[0]):
            day=int(row[0])
            if 1<=day<=31:
                if len(row)!=len(headers):
                    raise ValueError(f"USACE July source row {day} mismatched header columns")
                d=dict(zip(headers,row))
                d["day"]=day;data.append(d)
        if row and row[0] in ("TOT","AVG","MAX","MIN"):
            break
    if len(data)!=31 or sorted(x["day"] for x in data)!=list(range(1,32)):
        raise ValueError(f"Source cannot certify all 31 USACE July calendar rows: {len(data)}")
    original=pd.DataFrame(data).sort_values("day")
    original["date"]=pd.to_datetime("2024-07-"+original.day.astype(str).str.zfill(2))
    for key,name in (
        ("Banks Lake Pump MWh","usace_banks_lake_pumping_electricity_mwh"),
        ("Banks Lake Pump kcfs","usace_banks_lake_pump_flow_kcfs"),
        ("Banks Lake Elev","usace_banks_lake_reported_elev_ft"),
        ("Midnight Reservoir Elevation","usace_roosevelt_midnight_elev_ft")):
        if key not in original:raise ValueError(f"USACE field {key} absent")
        original[name]=pd.to_numeric(original[key].replace("",pd.NA),errors="coerce")
        if original[key].ne("").sum()>0 and original[name].notna().sum()==0:
            raise ValueError(f"All reported {key} values invalid numeric")
    cols=["date","usace_banks_lake_pumping_electricity_mwh",
         "usace_banks_lake_pump_flow_kcfs","usace_banks_lake_reported_elev_ft",
         "usace_roosevelt_midnight_elev_ft"]
    x=original[cols].copy()
    for c in cols[1:]:
        x[c+"_source_observed"]=x[c].notna()
    manifest={"USACE_site":"GCL Grand Coulee Project Daily",
      "USACE_original_historical_page_July_2024":True,
      "source_sha256":hashlib.sha256(content).hexdigest(),
      "original_july_day_rows":len(x),
      "pumping_energy_nonmissing_days":int(x.usace_banks_lake_pumping_electricity_mwh.notna().sum()),
      "pump_flow_nonmissing_days":int(x.usace_banks_lake_pump_flow_kcfs.notna().sum()),
      "upper_elevation_nonmissing_days":int(x.usace_banks_lake_reported_elev_ft.notna().sum()),
      "lower_elevation_nonmissing_days":int(x.usace_roosevelt_midnight_elev_ft.notna().sum()),
      "pumping_mwh_complete_31day_total":(
        float(x.usace_banks_lake_pumping_electricity_mwh.sum()) if
        x.usace_banks_lake_pumping_electricity_mwh.notna().all() else None),
      "USACE_pumping_MWh_is_project_wide_not_verified_reversible_PG7_PG12_only":True,
      "USACE_daily_pump_kcfs_is_not_automatically_daily_total_volume":True,
      "USACE_2024_actual_mwh_not_bpa_PS_dispatch_calibration":True,
      "historical_real_outage_EENS_inferred":False}
    return x,manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    x,m=admit(a.source)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    x.to_csv(out/"usace_grand_coulee_banks_pumping_2024_july_31day_actual_reported.csv",index=False)
    (out/"usace_grand_coulee_july2024_original_pumping_audit_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print("SOURCE-VERIFIED ORIGINAL USACE GRAND COULEE JULY 2024 PUMPING AND WATER LEVEL COVERAGE")
    print(json.dumps(m,indent=2))
    print(x.to_string(index=False))
if __name__=="__main__":main()
