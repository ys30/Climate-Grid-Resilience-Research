"""Inspect Page 1 hydro/pumped-storage rows for target BAs without inferring generation."""
import argparse, io, json, zipfile
from pathlib import Path
from collections import Counter
from openpyxl import load_workbook

BAS = {"AZPS", "BPAT", "CISO", "SRP"}
CODES = {"HY", "PS"}

def inspect(archive, output):
    with zipfile.ZipFile(archive) as z:
        files=[n for n in z.namelist() if "Schedules_2_3_4_5" in n and n.endswith(".xlsx")]
        if len(files)!=1: raise ValueError("Exactly one schedules workbook required")
        wb=load_workbook(io.BytesIO(z.read(files[0])),read_only=True,data_only=True)
        try:
            ws=wb["Page 1 Generation and Fuel Data"]
            headers=list(ws.iter_rows(min_row=6,max_row=6,values_only=True))[0]
            # Column positions are verified against the original 2024 Page 1 probe.
            # Refuse unexpected layout instead of producing misleading coverage.
            if "Plant" not in str(headers[0]) or "Prime Mover" not in " ".join(str(headers[13]).split()) or "Balancing" not in " ".join(str(headers[16]).split()):
                raise ValueError("Page 1 source layout differs; inspect headers before classifying BA/hydro")
            counts=Counter(); examples=[]
            for i,row in enumerate(ws.iter_rows(min_row=7,values_only=True),start=7):
                if len(row)<17: continue
                code=str(row[13]).strip() if row[13] is not None else ""
                ba=str(row[16]).strip() if row[16] is not None else ""
                if code in CODES and ba in BAS:
                    counts[(ba,code)]+=1
                    if len(examples)<12:
                        examples.append({"row":i,"plant_id":str(row[0]),"ba":ba,"prime_mover":code})
        finally:
            wb.close()
    report={"source":"EIA-923 2024 Page 1 (plant/fuel/prime mover), not generator-level Page 4",
            "source_rows_by_ba_code":[{"ba":ba,"prime_mover":code,"source_rows":counts[(ba,code)]}
                                      for ba in sorted(BAS) for code in sorted(CODES)],
            "examples":examples,
            "monthly_net_generation_extracted":False,
            "historical_calibration_certified":False,
            "warning":"Row counts are not coverage of months or unique generating units. Page 1 reporting basis must be independently reconciled before energy aggregation."}
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(inspect(a.archive,a.output),indent=2))

if __name__=="__main__": main()
