"""Inspect official EIA-923 Page 1 layout before building hydro ingestion."""
import argparse,io,json,zipfile
from pathlib import Path
from openpyxl import load_workbook

def probe(archive,output):
    with zipfile.ZipFile(archive) as z:
        members=[n for n in z.namelist() if "Schedules_2_3_4_5" in n and n.endswith(".xlsx")]
        if len(members)!=1:raise ValueError("Expected one EIA923 schedules workbook")
        wb=load_workbook(io.BytesIO(z.read(members[0])),read_only=True,data_only=True)
        try:
            ws=wb["Page 1 Generation and Fuel Data"]
            first_rows=[]
            for row in ws.iter_rows(min_row=1,max_row=10,values_only=True):
                first_rows.append([str(x)[:100] if x is not None else None for x in row[:45]])
            data_examples=[]
            for ix,row in enumerate(ws.iter_rows(min_row=11,values_only=True)):
                if any("HY"==str(x).strip() or "PS"==str(x).strip() for x in row[:20]):
                    data_examples.append({"worksheet_row":ix+11,"first_20_fields":[str(x)[:60] if x is not None else None for x in row[:20]]})
                    if len(data_examples)>=5:break
            report={"worksheet":"Page 1 Generation and Fuel Data","first_ten_rows":first_rows,
                    "first_five_HY_PS_code_examples":data_examples,
                    "verified_hydro_extraction_complete":False,
                    "note":"Layout and sample probe only: do not mix plant-level Page 1 with generator-level Page 4."}
        finally:wb.close()
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2)+"\n")
    return report
def main():
    p=argparse.ArgumentParser();p.add_argument("--archive",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();m=probe(a.archive,a.output)
    print(json.dumps(m,indent=2))
if __name__=="__main__":main()
