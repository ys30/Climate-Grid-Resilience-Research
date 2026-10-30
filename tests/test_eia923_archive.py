import zipfile
import pytest
from grid_resilience.eia923_archive import inspect_archive

URL="https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2024.zip"

def test_manifest_preserves_archive_evidence(tmp_path):
    p=tmp_path/"example.zip"
    with zipfile.ZipFile(p,"w") as z:
        z.writestr("EIA923_Schedules_3A_5A.xlsx",b"synthetic placeholder")
    result=inspect_archive(p,tmp_path/"manifest.json",URL)
    assert result["workbook_count"]==1
    assert len(result["archive_sha256"])==64
    assert result["generation_data_extracted"] is False

def test_refuses_missing_workbook(tmp_path):
    p=tmp_path/"bad.zip"
    with zipfile.ZipFile(p,"w") as z:
        z.writestr("readme.txt","only text")
    with pytest.raises(ValueError,match="No Excel workbooks"):
        inspect_archive(p,tmp_path/"manifest.json",URL)

def test_refuses_unofficial_source(tmp_path):
    p=tmp_path/"x.zip"
    with zipfile.ZipFile(p,"w") as z:
        z.writestr("data.xlsx",b"example")
    with pytest.raises(ValueError,match="Official EIA"):
        inspect_archive(p,tmp_path/"manifest.json","https://example.com/file.zip")
