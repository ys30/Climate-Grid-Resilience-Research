import io
import zipfile
import json
import pandas as pd
import pytest
from openpyxl import Workbook
from grid_resilience.eia923_page1_ps_netgen import extract, MONTHS

def archive(tmp_path, *, bad_header=False, duplicate=False):
    wb=Workbook()
    ws=wb.active
    ws.title="Page 1 Energy Storage"
    headers=[""]*70
    headers[0]="Plant Id"
    headers[12]="Reported\nPrime Mover"
    headers[15]="Balancing\nAuthority Code"
    for i,m in enumerate(MONTHS):
        headers[54+i]=f"Netgen\n{m}"
    if bad_header:
        headers[54]="Grossgen\nJanuary"
    for i,v in enumerate(headers,start=1):
        ws.cell(row=6,column=i,value=v)
    for rowno in ([7,8] if duplicate else [7]):
        ws.cell(row=rowno,column=1,value=104)
        ws.cell(row=rowno,column=13,value="PS")
        ws.cell(row=rowno,column=16,value="CISO")
        ws.cell(row=rowno,column=55,value=-5)
        ws.cell(row=rowno,column=56,value=0)
    data=io.BytesIO()
    wb.save(data)
    path=tmp_path/"source.zip"
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("EIA923_Schedules_2_3_4_5_2024.xlsx",data.getvalue())
    return path

def test_extract_negative_zero_and_missing_separately(tmp_path):
    source=archive(tmp_path)
    report=extract(source,tmp_path/"output")
    obs=pd.read_csv(tmp_path/"output"/"eia923_page1_ps_plant_month_net_mwh.csv")
    assert len(obs)==2
    assert obs.net_generation_mwh.tolist()==[-5.0,0.0]
    assert report["missing_netgen_cells_by_ba"]=={"CISO":10}
    assert report["historical_calibration_certified"] is False

def test_rejects_wrong_netgen_columns(tmp_path):
    with pytest.raises(ValueError,match="Unexpected Netgen"):
        extract(archive(tmp_path,bad_header=True),tmp_path/"output")

def test_duplicate_plant_month_rejected(tmp_path):
    with pytest.raises(ValueError,match="Duplicate"):
        extract(archive(tmp_path,duplicate=True),tmp_path/"output")
