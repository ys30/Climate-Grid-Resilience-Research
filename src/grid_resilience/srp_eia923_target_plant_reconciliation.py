"""Auditable EIA923 Page1 fuel/mover rows vs Page4 generator rows for selected SRP plants.

This is a reporting-grain discrepancy diagnostic, not physical generation
loss or thermal derating. Keep other-fuel Page1 rows separate rather than
silently attributing them to the target technology.
"""
import argparse
import io
import json
import zipfile
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook

TARGETS=("141","55129","147")
MONTHS={1:"January",7:"July"}
MOVER={"GT","CT","CA","CS","ST"}


def inspect(archive, *, plants=TARGETS):
    selected={str(p).lstrip("0") or "0" for p in plants}
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if "Schedules_2_3_4_5" in n and n.endswith(".xlsx")]
        if len(names)!=1:raise ValueError("Expected one schedules workbook")
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        p1=[];p4=[]
        try:
            a=wb["Page 1 Generation and Fuel Data"]
            ah=next(a.iter_rows(min_row=6,max_row=6,values_only=True))
            expected={0:"Plant Id",13:"Reported Prime Mover",14:"Reported Fuel Type Code",
                      16:"Balancing Authority Code",79:"Netgen January",85:"Netgen July",96:"YEAR"}
            for i,label in expected.items():
                if str(ah[i]).strip()!=label:raise ValueError("Page1 schema changed")
            for rno,row in enumerate(a.iter_rows(min_row=7,values_only=True),7):
                if row[0] is None:continue
                pid=str(row[0]).strip().lstrip("0") or "0"
                if pid not in selected or str(row[16]).strip()!="SRP":continue
                if int(row[96])!=2024:raise ValueError("Unexpected source year")
                for month,name in MONTHS.items():
                    v=row[78+month]
                    available=v is not None and str(v).strip() not in ("","NM","NA",".")
                    value=float(v) if available else None
                    p1.append({"period":f"2024-{month:02d}","plant_id":pid,"source_row":rno,
                        "prime_mover":str(row[13]).strip(),
                        "fuel":str(row[14]).strip(),"reported_signed_net_mwh":value,
                        "source_value_reported":available})
            b=wb["Page 4 Generator Data"]
            bh=next(b.iter_rows(min_row=6,max_row=6,values_only=True))
            if str(bh[0]).strip()!="Plant Id":raise ValueError("Page4 schema changed")
            for rno,row in enumerate(b.iter_rows(min_row=7,values_only=True),7):
                if row[0] is None:continue
                pid=str(row[0]).strip().lstrip("0") or "0"
                if pid not in selected or str(row[27]).strip()!="SRP":continue
                if int(row[28])!=2024:raise ValueError("Unexpected source year")
                for month,name in MONTHS.items():
                    v=row[13+month]
                    available=v is not None and str(v).strip() not in ("","NM","NA",".")
                    value=float(v) if available else None
                    p4.append({"period":f"2024-{month:02d}","plant_id":pid,"source_row":rno,
                        "generator_id":str(row[11]).strip(),"prime_mover":str(row[12]).strip(),
                        "reported_signed_net_mwh":value,"source_value_reported":available})
        finally:
            wb.close()
    aa=pd.DataFrame(p1);bb=pd.DataFrame(p4)
    if aa.empty or bb.empty:raise ValueError("Target plants missing from source sheets")
    if bb.loc[bb.source_value_reported].duplicated(["period","plant_id","generator_id"]).any():
        raise ValueError("Duplicate Page4 reported generator-month")
    aa["target_ng_fuel_mover"]=aa.fuel.eq("NG")&aa.prime_mover.isin(MOVER)
    details=[]
    for pid in sorted(selected):
        for month in MONTHS:
            period=f"2024-{month:02d}"
            one=aa[(aa.plant_id==pid)&(aa.period==period)]
            four=bb[(bb.plant_id==pid)&(bb.period==period)]
            a=one[one.target_ng_fuel_mover&one.source_value_reported]
            b=four[four.source_value_reported]
            if a.empty or b.empty:raise ValueError(f"Target source missing {pid} {period}")
            amwh=float(a.reported_signed_net_mwh.sum())
            bmwh=float(b.reported_signed_net_mwh.sum())
            details.append({
                "plant_id":pid,"period":period,
                "page1_all_rows":len(one),
                "page1_ng_rows_reported":len(a),
                "page1_other_fuel_mover_rows":int((~one.target_ng_fuel_mover).sum()),
                "page1_ng_prime_movers":",".join(sorted(a.prime_mover.unique())),
                "page1_other_fuel_movers":",".join(sorted(
                    set((str(r.fuel)+"/"+str(r.prime_mover))
                        for r in one.loc[~one.target_ng_fuel_mover].itertuples()))),
                "page4_reported_generator_count":len(b),
                "page4_generators":",".join(sorted(b.generator_id.astype(str).unique())),
                "page4_prime_movers":",".join(sorted(b.prime_mover.astype(str).unique())),
                "page1_ng_signed_net_mwh":amwh,
                "page4_all_generator_signed_net_mwh":bmwh,
                "p1_minus_p4_mwh":amwh-bmwh
            })
    result=pd.DataFrame(details)
    manifest={"source":"Official EIA923 2024 Schedules_2_3_4_5",
      "source_reported_ba":"SRP","page1_grain":"plant-fuel-prime_mover-row-month",
      "page4_grain":"plant-generator-row-month",
      "page1_only_ng_compatible_fuel_mover":True,
      "page4_all_movers_in_plant":True,
      "source_reconciliation_not_generator_allocation":True,
      "monthly_difference_is_weather_derating":False,
      "historical_reliability_calibrated":False}
    return aa,bb,result,manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    one,four,result,m=inspect(a.archive)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    one.to_csv(out/"target_page1_source_rows.csv",index=False)
    four.to_csv(out/"target_page4_source_rows.csv",index=False)
    result.to_csv(out/"target_plant_reconciliation.csv",index=False)
    (out/"target_plant_reconciliation_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print(result.to_string(index=False))


if __name__=="__main__":
    main()
