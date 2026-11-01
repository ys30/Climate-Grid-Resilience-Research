import io
import zipfile
from openpyxl import Workbook
from grid_resilience.eia923_page1_hy_inventory import inventory

def test_hydro_inventory_keeps_source_rows_not_generation(tmp_path):
    wb=Workbook()
    ws=wb.active
    ws.title="Page 1 Generation and Fuel Data"
    headers=[""]*45
    headers[0]="Plant Id"
    headers[13]="Reported\nPrime Mover"
    headers[14]="Reported\nFuel Type Code"
    headers[16]="Balancing\nAuthority Code"
    for i,h in enumerate(headers,1):ws.cell(6,i,h)
    for row,plant,ba,code,fuel in [(7,100,"BPAT","HY","WAT"),(8,100,"BPAT","HY","WAT"),
                                    (9,104,"CISO","HY","WAT"),(10,200,"BPAT","PS","WAT")]:
        for col,v in [(1,plant),(14,code),(15,fuel),(17,ba)]:ws.cell(row,col,v)
    data=io.BytesIO();wb.save(data)
    z=tmp_path/"archive.zip"
    with zipfile.ZipFile(z,"w") as f:f.writestr("EIA923_Schedules_2_3_4_5_2024.xlsx",data.getvalue())
    report=inventory(z,tmp_path/"out")
    assert report["hydro_source_rows"]==3
    assert report["distinct_plant_ba_pairs"]==2
    assert report["multiple_source_rows_same_plant_ba"]==1
    assert report["monthly_net_generation_extracted"] is False
