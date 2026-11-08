from pathlib import Path
from zipfile import ZipFile
import pytest
from grid_resilience.paperc_caiso_original_storage_xml import audit,raw_rows

STRING=("TRADE_DATE","HOUR","INTERVAL","MARKET","RES_TYPE","TYPE","VALUE",
        "RTD","LESR","SOC")

def make(tmp_path,name,entries,duplicate=False):
    path=tmp_path/name
    rows=['<row r="1">'+''.join(
        f'<c r="{col}1" t="s"><v>{i}</v></c>' for i,col in enumerate("ABCDEFG"))+'</row>']
    for i,(serial,h,interval,value) in enumerate(entries,2):
        vals={"A":str(serial),"B":str(h),"C":str(interval),
              "D":"7","E":"8","F":"9","G":str(value)}
        row='<row r="%s">'%i+''.join(
            f'<c r="{key}{i}"'+(' t="s"' if key in "DEF" else '')+
            f'><v>{v}</v></c>' for key,v in vals.items())+'</row>'
        rows.append(row)
    if duplicate:
        rows.append(rows[-1].replace(f'r="{len(rows)}"',f'r="{len(rows)+1}"'))
    ss='<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'+''.join(
        f'<si><t>{x}</t></si>' for x in STRING)+'</sst>'
    # Intentionally wrong worksheet declared dimension A1.
    xml='<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'+(
        '<dimension ref="A1"/><sheetData>'+''.join(rows)+'</sheetData></worksheet>')
    with ZipFile(path,"w") as z:
        z.writestr("xl/sharedStrings.xml",ss)
        z.writestr("xl/worksheets/sheet1.xml",xml)
    return path

def cohort(tmp_path,duplicate=False):
    # Excel dates: 2023-07-09 = 45116; 2024-06-30 = 45473.
    # All are local PDT hour-18 => 00:00 UTC following calendar date.
    return {
      2023:{"Q3":make(tmp_path,"23q3.xlsx",[(45116,18,1,33.0)],duplicate)},
      2024:{"Q2":make(tmp_path,"24q2.xlsx",[(45473,18,1,44.0)]),
            "Q3":make(tmp_path,"24q3.xlsx",[(45474,1,1,55.0)])}
    }

def test_broken_dimensional_metadata_still_yields_rows(tmp_path):
    f=make(tmp_path,"a.xlsx",[(45116,18,1,2.0)])
    assert len(list(raw_rows(f)))==2

def test_timezone_bridge_includes_june30_for_july1_utc(tmp_path):
    d,s,m=audit(cohort(tmp_path))
    assert len(d)==3
    assert set(d.eia930_study_year)=={2023,2024}
    assert d.loc[d.quarter.eq("Q2"),
        "utc_hour_start_from_local_trade_date"].iloc[0].startswith("2024-07-01T00")
    assert m["market_result_source_not_actual_metered_charge_discharge"]
    assert m["no_eia930_raw_storage_null_imputation"]

def test_broken_header_rejected(tmp_path):
    files=cohort(tmp_path)
    p=files[2024]["Q2"]
    with ZipFile(p) as z:
        raw=z.read("xl/sharedStrings.xml").replace(b"TRADE_DATE",b"BAD_HEADER")
        sheet=z.read("xl/worksheets/sheet1.xml")
    with ZipFile(p,"w") as z:
        z.writestr("xl/sharedStrings.xml",raw)
        z.writestr("xl/worksheets/sheet1.xml",sheet)
    with pytest.raises(ValueError,match="header"):
        audit(files)

def test_missing_quarter_is_not_assumed_zero(tmp_path):
    files=cohort(tmp_path)
    del files[2024]["Q2"]
    with pytest.raises(ValueError,match="quarter"):
        audit(files)
