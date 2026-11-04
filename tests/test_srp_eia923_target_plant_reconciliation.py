import io
import zipfile
import pytest
from openpyxl import Workbook

from grid_resilience.srp_eia923_target_plant_reconciliation import inspect


def sample_archive(tmp_path, *, page4_missing=False):
    wb=Workbook()
    a=wb.active
    a.title="Page 1 Generation and Fuel Data"
    b=wb.create_sheet("Page 4 Generator Data")
    fields={0:"Plant Id",13:"Reported Prime Mover",14:"Reported Fuel Type Code",
            16:"Balancing Authority Code",79:"Netgen January",
            85:"Netgen July",96:"YEAR"}
    for col,name in fields.items():a.cell(6,col+1,name)
    b.cell(6,1,"Plant Id")
    for index,plant in enumerate((141,55129,147),start=7):
        a.cell(index,1,plant)
        a.cell(index,14,"GT");a.cell(index,15,"NG")
        a.cell(index,17,"SRP");a.cell(index,97,2024)
        a.cell(index,80,500.);a.cell(index,86,800.)
        if not (page4_missing and plant==141):
            b.cell(index,1,plant)
            b.cell(index,12,"A");b.cell(index,13,"GT")
            b.cell(index,28,"SRP");b.cell(index,29,2024)
            b.cell(index,15,400.);b.cell(index,21,600.)
    out=io.BytesIO();wb.save(out)
    p=tmp_path/"f923_2024.zip"
    with zipfile.ZipFile(p,"w") as z:z.writestr("2_Schedules_2_3_4_5_Y2024.xlsx",out.getvalue())
    return p


def test_extracts_original_fuel_mover_and_generator_rows(tmp_path):
    one,four,detail,m=inspect(sample_archive(tmp_path))
    assert len(detail)==6
    assert set(detail.plant_id)=={"141","55129","147"}
    assert detail.loc[detail.period.eq("2024-07"),"p1_minus_p4_mwh"].eq(200).all()
    assert detail.page4_generators.eq("A").all()
    assert len(one)==6 and len(four)==6
    assert not m["monthly_difference_is_weather_derating"]


def test_missing_page4_target_fails_closed(tmp_path):
    with pytest.raises(ValueError,match="Target source missing"):
        inspect(sample_archive(tmp_path,page4_missing=True))


def test_unexpected_page1_schema_rejected(tmp_path):
    p=sample_archive(tmp_path)
    with zipfile.ZipFile(p) as z:
        name=z.namelist()[0]
        from openpyxl import load_workbook
        wb=load_workbook(io.BytesIO(z.read(name)))
    wb["Page 1 Generation and Fuel Data"].cell(6,80,"Wrong January header")
    data=io.BytesIO();wb.save(data)
    with zipfile.ZipFile(p,"w") as z:z.writestr(name,data.getvalue())
    with pytest.raises(ValueError,match="Page1 schema"):
        inspect(p)
