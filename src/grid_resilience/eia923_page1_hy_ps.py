"""Verified EIA-923 2024 Page 1 monthly net generation HY/PS BA ledger."""
import argparse,csv,io,json,math,zipfile
from pathlib import Path
from openpyxl import load_workbook

def extract(archive,output,ba="SRP"):
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if "Schedules_2_3_4_5" in n and n.endswith(".xlsx")]
        if len(names)!=1:raise ValueError("Expected one EIA-923 schedules workbook")
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        try:
            ws=wb["Page 1 Generation and Fuel Data"]
            h=[str(x).strip() if x is not None else "" for x in next(ws.iter_rows(min_row=6,max_row=6,values_only=True))]
            fixed={0:"Plant Id",13:"Reported\nPrime Mover",14:"Reported\nFuel Type Code",16:"Balancing\nAuthority Code",79:"Netgen\nJanuary",90:"Netgen\nDecember",96:"YEAR"}
            for col,label in fixed.items():
                if h[col]!=label:raise ValueError(f"Unexpected header {col}: {h[col]!r}")
            rows=[];missing=0
            for r in ws.iter_rows(min_row=7,values_only=True):
                if r[0] is None or str(r[16]).strip()!=ba:continue
                mover=str(r[13]).strip().upper()
                fuel=str(r[14]).strip().upper()
                if mover not in ("HY","PS"):continue
                if int(r[96])!=2024:raise ValueError("Unexpected year")
                for month in range(1,13):
                    value=r[78+month]
                    if value is None or str(value).strip() in ("",".","NA","NM"):
                        missing+=1;continue
                    value=float(value)
                    if not math.isfinite(value):raise ValueError("Nonfinite MWh")
                    rows.append({"plant_id":str(r[0]).strip(),"ba":ba,"prime_mover":mover,
                                 "fuel":fuel,"period":f"2024-{month:02d}","net_generation_mwh":value})
        finally:wb.close()
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    with (out/"page1_hy_ps_monthly_observations.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["plant_id","ba","prime_mover","fuel","period","net_generation_mwh"])
        w.writeheader();w.writerows(rows)
    totals={}
    for code in ("HY","PS"):
        vals=[x["net_generation_mwh"] for x in rows if x["prime_mover"]==code and x["period"]=="2024-01"]
        totals[code]={"source_rows":len(vals),"net_generation_mwh":sum(vals) if vals else None}
    summary={"ba":ba,"year":2024,"jan":totals,"missing_month_cells":missing,
             "historical_calibration_certified":False,
             "notes":"Page1 plant/prime-mover/fuel rows, not generator-level Page4; PS may be negative. No missing-as-zero."}
    (out/"page1_hy_ps_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    return summary
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True);p.add_argument("--output",required=True);p.add_argument("--ba",default="SRP")
    a=p.parse_args();extract(a.archive,a.output,a.ba)
if __name__=="__main__":main()
