"""EIA-923 Page 1 reported-BA monthly fuel/prime-mover net generation.

This is a plant-fuel-prime-mover observation, not a generator or complete BA
inventory. Keep original signed MWh and refuse unexpected workbook layouts.
"""
import argparse,csv,io,json,math,zipfile
from collections import defaultdict
from pathlib import Path
from openpyxl import load_workbook

def extract(archive,output,ba="SRP",month=1):
    if not 1<=month<=12:raise ValueError("Invalid month")
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if "Schedules_2_3_4_5" in n and n.endswith(".xlsx")]
        if len(names)!=1:raise ValueError("Expected one official Page1 workbook")
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        try:
            ws=wb["Page 1 Generation and Fuel Data"]
            header=list(next(ws.iter_rows(min_row=6,max_row=6,values_only=True)))
            def normalized(v):return str(v).strip().replace("\n"," ").replace("  "," ") if v is not None else ""
            required={0:"Plant Id",13:"Reported Prime Mover",14:"Reported Fuel Type Code",
                      16:"Balancing Authority Code",79:"Netgen January",90:"Netgen December",96:"YEAR"}
            for idx,name in required.items():
                if normalized(header[idx])!=name:raise ValueError(f"Unexpected Page1 header {idx}: {header[idx]!r}")
            output_rows=[];unreported=0;observed=0
            for row in ws.iter_rows(min_row=7,values_only=True):
                if not row or row[0] is None or str(row[16]).strip()!=ba:continue
                if int(row[96])!=2024:raise ValueError("Unexpected source year")
                observed+=1
                v=row[78+month]
                if v is None or str(v).strip() in ("",".","NA","NM"):
                    unreported+=1;continue
                value=float(v)
                if not math.isfinite(value):raise ValueError("Nonfinite Page1 net MWh")
                output_rows.append({"plant_id":str(row[0]).strip(),
                  "reported_ba":ba,"prime_mover":str(row[13]).strip().upper(),
                  "reported_fuel":str(row[14]).strip().upper(),
                  "period":f"2024-{month:02d}","net_generation_mwh":value})
        finally:wb.close()
    if observed==0:raise ValueError(f"No official Page1 rows for BA {ba}")
    if not output_rows:raise ValueError(f"No reported Page1 generation values for BA {ba}")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    keys=["plant_id","reported_ba","prime_mover","reported_fuel","period","net_generation_mwh"]
    with (out/"page1_all_fuels_reported_ba.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(output_rows)
    groups=defaultdict(lambda:[0,0.0])
    for row in output_rows:
        k=(row["prime_mover"],row["reported_fuel"])
        groups[k][0]+=1;groups[k][1]+=row["net_generation_mwh"]
    with (out/"page1_prime_mover_fuel_month_summary.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["prime_mover","reported_fuel","source_rows","observed_net_mwh"])
        for (mover,fuel),(count,energy) in sorted(groups.items()):
            w.writerow([mover,fuel,count,energy])
    manifest={"ba":ba,"period":f"2024-{month:02d}","source_rows_for_ba":observed,
       "reported_month_rows":len(output_rows),"missing_netgen_cells":unreported,
       "observed_reported_ba_page1_net_mwh":sum(x["net_generation_mwh"] for x in output_rows),
       "missing_is_zero":False,"source_month_complete":unreported==0,
       "sum_is_partial_if_missing":unreported>0,"historical_calibration_certified":False,
       "warning":"Page1 BA field is reporting attribution; full BA operational supply coverage and Page4 overlap are not established."}
    (out/"page1_all_fuels_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
    print("FUEL SUMS:",[(a,b,v[0],v[1]) for (a,b),v in sorted(groups.items())])
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True);p.add_argument("--output",required=True)
    p.add_argument("--ba",default="SRP");p.add_argument("--month",type=int,default=1)
    a=p.parse_args();extract(a.archive,a.output,a.ba,a.month)
if __name__=="__main__":main()
