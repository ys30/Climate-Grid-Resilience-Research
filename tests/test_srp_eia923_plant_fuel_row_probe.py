import io
import zipfile
from openpyxl import Workbook
import pytest
from grid_resilience.srp_eia923_plant_fuel_row_probe import inspect


def make_zip(path):
    w=Workbook();s=w.active;s.title="Page 1 Generation and Fuel Data"
    for _ in range(5):s.append([None]*97)
    h=[None]*97
    for i,name in {0:"Plant Id",13:"Reported Prime Mover",14:"Reported Fuel Type Code",
                   16:"Balancing Authority Code",32:"Total Fuel Consumption January",
                   79:"Netgen January",96:"YEAR"}.items():h[i]=name
    s.append(h)
    for fuel,net,cons in (("SUB",270.,140.),("DFO",160.391,8.)):
        row=[None]*97
        row[0]=6177;row[13]="ST";row[14]=fuel;row[16]="SRP"
        row[32]=cons;row[79]=net;row[96]=2024
        s.append(row)
    buf=io.BytesIO();w.save(buf)
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("EIA923_Schedules_2_3_4_5_2024.xlsx",buf.getvalue())


def test_preserves_separate_fuel_rows_and_original_consumption(tmp_path):
    f=tmp_path/"eia.zip";make_zip(f)
    result=inspect(f)
    assert result["source_row_count"]==2
    assert {r["reported_fuel"] for r in result["plant_source_rows"]}=={"SUB","DFO"}
    dfo=next(r for r in result["plant_source_rows"] if r["reported_fuel"]=="DFO")
    assert next(c["original_value"] for c in dfo["columns"] if c["column_index_1based"]==33)==8.
    assert not result["generator_allocation_certified"]


def test_unavailable_plant_is_rejected(tmp_path):
    f=tmp_path/"eia.zip";make_zip(f)
    with pytest.raises(ValueError,match="No matching"):
        inspect(f,plant="9999")
