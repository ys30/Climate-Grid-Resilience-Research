"""Synthetic workbook regression tests; not a substitute for official EIA-923 validation."""
import io,zipfile
from openpyxl import Workbook
import pytest
from grid_resilience.eia923_page1_all_fuels import extract

def fixture_archive(path,ba="SRP",jan=20.0):
    wb=Workbook();ws=wb.active;ws.title="Page 1 Generation and Fuel Data"
    h=[None]*97
    for i,v in {0:"Plant Id",13:"Reported\nPrime Mover",14:"Reported\nFuel Type Code",
                16:"Balancing\nAuthority Code",79:"Netgen\nJanuary",
                90:"Netgen\nDecember",96:"YEAR"}.items():h[i]=v
    ws.append([None]*97)
    for _ in range(4):ws.append([None]*97)
    ws.append(h)
    row=[None]*97;row[0]=141;row[13]="HY";row[14]="WAT";row[16]=ba;row[79]=jan;row[96]=2024
    ws.append(row)
    stream=io.BytesIO();wb.save(stream)
    with zipfile.ZipFile(path,"w") as z:z.writestr("EIA923_Schedules_2_3_4_5_2024.xlsx",stream.getvalue())

def test_observed_signed_mwh_and_source_completeness(tmp_path):
    src=tmp_path/"official_fixture.zip";fixture_archive(src,jan=-12)
    m=extract(src,tmp_path/"out",ba="SRP")
    assert m["observed_reported_ba_page1_net_mwh"]==-12
    assert m["source_month_complete"] is True
    assert m["missing_netgen_cells"]==0

def test_missing_values_not_silently_zero(tmp_path):
    src=tmp_path/"official_fixture.zip";fixture_archive(src,jan=None)
    with pytest.raises(ValueError,match="No reported"):
        extract(src,tmp_path/"out",ba="SRP")

def test_wrong_ba_fails_closed(tmp_path):
    src=tmp_path/"official_fixture.zip";fixture_archive(src,ba="AZPS")
    with pytest.raises(ValueError,match="No official Page1"):
        extract(src,tmp_path/"out",ba="SRP")
