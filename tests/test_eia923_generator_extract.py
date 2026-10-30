import io
import zipfile
from openpyxl import Workbook
from grid_resilience.eia923_generator_extract import extract

def fixture(path):
    wb=Workbook()
    ws=wb.active
    ws.title="Page 4 Generator Data"
    ws.cell(5,15,"Net Generation (MWh)")
    ws.cell(6,1,"Plant Id")
    row=[None]*29
    row[0]=104;row[11]="G01";row[12]="ST";row[27]="CISO";row[28]=2024
    row[14:26]=[0,-12,4,None,1,2,3,4,5,6,7,8]
    ws.append(row)
    stream=io.BytesIO()
    wb.save(stream)
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("EIA923_Schedules_2_3_4_5_M_12_2024_Final.xlsx",stream.getvalue())

def test_real_layout_zero_negative_and_missing(tmp_path):
    path=tmp_path/"archive.zip"
    fixture(path)
    result=extract(path,tmp_path/"out")
    assert result["total_records"]==11
    assert result["excluded_missing_month_cells"]==1
    import pandas as pd
    df=pd.read_csv(tmp_path/"out"/"eia923_generator_month_net_mwh.csv")
    assert df.loc[df.period=="2024-01","generation_mwh"].iloc[0]==0
    assert df.loc[df.period=="2024-02","generation_mwh"].iloc[0]==-12
    assert "2024-04" not in df.period.values
