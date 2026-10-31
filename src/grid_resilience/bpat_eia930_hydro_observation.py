"""Compare EIA-930 observed BPAT hydro+pumped output against EIA-860
non-storage hydro nameplate, without treating the two as equivalent fleets.
"""
import argparse,csv,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
import pandas as pd
from .eia930_fuel_decomposition import FMT

def compare(balance,capacity,out):
    caps=pd.read_csv(capacity)
    hydro=caps.loc[(caps.ba=="BPAT")&(caps.technology=="hydro")]
    if len(hydro)!=1:raise ValueError("Expected one BPAT hydro capacity group")
    mw=float(hydro.iloc[0].nameplate_capacity_mw)
    if not 0<mw<float("inf"):raise ValueError("Invalid hydro nameplate")
    records=[];seen=set()
    with Path(balance).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        field="Net Generation (MW) from Hydropower and Pumped Storage"
        if field not in (reader.fieldnames or []):raise ValueError("Missing EIA-930 hydro+pumped category")
        for row in reader:
            if row["Balancing Authority"].strip()!="BPAT":continue
            ts=datetime.strptime(row["UTC Time at End of Hour"],FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not datetime(2024,2,1,tzinfo=timezone.utc)<=ts<datetime(2024,3,1,tzinfo=timezone.utc):continue
            if ts in seen:raise ValueError("Duplicate BPAT hour")
            seen.add(ts)
            raw=row[field].strip()
            if not raw:raise ValueError("Blank observed hydro group hour")
            val=float(raw)
            if not -float("inf")<val<float("inf"):raise ValueError("Invalid hourly reported generation")
            records.append({"timestamp":ts.isoformat(),"reported_hydro_and_pumped_net_mw":val,
                            "ratio_to_nonstorage_hydro_nameplate":val/mw,
                            "below_5pct_nameplate":val<0.05*mw,
                            "below_10pct_nameplate":val<0.10*mw})
    if len(records)!=696:raise ValueError(f"Expected 696 BPAT hours; found {len(records)}")
    df=pd.DataFrame(records)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/"bpat_eia930_reported_hydro_hourly.csv",index=False)
    result={"hours":len(df),"eia860_bpat_single_fuel_nonstorage_hydro_nameplate_mw":mw,
      "eia930_mixed_hydro_and_pumped_reported_mean_mw":float(df.reported_hydro_and_pumped_net_mw.mean()),
      "eia930_mixed_hydro_and_pumped_reported_min_mw":float(df.reported_hydro_and_pumped_net_mw.min()),
      "eia930_mixed_hydro_and_pumped_reported_monthly_net_mwh":float(df.reported_hydro_and_pumped_net_mw.sum()),
      "reported_hours_below_5pct_nonstorage_nameplate":int(df.below_5pct_nameplate.sum()),
      "reported_hours_below_10pct_nonstorage_nameplate":int(df.below_10pct_nameplate.sum()),
      "source_categories_not_equivalent":True,
      "not_a_physical_hydro_availability_estimate":True,
      "historical_calibration_certified":False,
      "warning":"EIA-930 hydro AND pumped storage net output; EIA-860 denominator excludes pumped storage. Ratios are descriptive, not physical CF/availability."}
    (out/"bpat_eia930_hydro_observation_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
def main():
    p=argparse.ArgumentParser()
    for field in ("balance","capacity","output"):p.add_argument("--"+field,required=True)
    a=p.parse_args();print(json.dumps(compare(a.balance,a.capacity,a.output),indent=2))
if __name__=="__main__":main()
