import io,zipfile
from openpyxl import Workbook
import pandas as pd
import pytest
from grid_resilience.eia923_page1_hy_netgen import extract, MONTHS

def make_archive(tmp_path, duplicate=False, wrong_header=False):
    wb=Workbook();ws=wb.active;ws.title="Page 1 Generation and Fuel Data"
    h=[""]*97
    h[0]="Plant Id";h[13]="Reported\nPrime Mover"
    h[14]="Reported\nFuel Type Code";h[16]="Balancing\nAuthority Code"
    for i,m in enumerate(MONTHS):h[79+i]=f"Netgen\n{m}"
    if wrong_header:h[79]="Quantity January"
    for i,v in enumerate(h,1):ws.cell(6,i,v)
    for row in ([7,8] if duplicate else [7]):
        for col,value in [(1,42),(14,"HY"),(15,"WAT"),(17,"BPAT"),(80,-2),(81,0)]:
            ws.cell(row,col,value)
    buffer=io.BytesIO();wb.save(buffer)
    z=tmp_path/"archive.zip"
    with zipfile.ZipFile(z,"w") as f:f.writestr("EIA923_Schedules_2_3_4_5_2024.xlsx",buffer.getvalue())
    return z

def test_signed_zero_and_missing(tmp_path):
    m=extract(make_archive(tmp_path),tmp_path/"out")
    x=pd.read_csv(tmp_path/"out"/"page1_hy_plant_month_net_mwh.csv")
    assert x.net_generation_mwh.tolist()==[-2.0,0.0]
    assert m["observed_plant_month_rows"]==2
    assert m["missing_month_cells_by_ba"]=={"BPAT":10}
    assert m["historical_calibration_certified"] is False

def test_rejects_wrong_netgen_header(tmp_path):
    with pytest.raises(ValueError,match="Unexpected Netgen"):
        extract(make_archive(tmp_path,wrong_header=True),tmp_path/"out")

def test_rejects_duplicate_plant_month(tmp_path):
    with pytest.raises(ValueError,match="Duplicate"):
        extract(make_archive(tmp_path,duplicate=True),tmp_path/"out")
