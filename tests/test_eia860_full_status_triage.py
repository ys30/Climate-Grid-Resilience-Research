import io
import zipfile
import pandas as pd
from openpyxl import Workbook
from grid_resilience.eia860_full_status_triage import compare_status_sheets

def test_status_workbook_identity_without_renaming(tmp_path):
    wb=Workbook()
    op=wb.active;op.title="Operable"
    for ws in (op,wb.create_sheet("Retired")):
        ws.append(["metadata"])
        ws.append(["Plant Code","Generator ID","Status"])
    op.append([58109,"TG2","OP"])
    wb["Retired"].append([58109,"TG1","RE"])
    wb["Retired"].append([10661,"GEN5","RE"])
    buf=io.BytesIO();wb.save(buf)
    archive=tmp_path/"official.zip"
    with zipfile.ZipFile(archive,"w") as z:
        z.writestr("3_1_Generator_Y2024.xlsx",buf.getvalue())
    unmatched=pd.DataFrame([
      {"plant_id":"00058109","generator_id":"TG1","reported_ba":"BPAT","period":"2024-01"},
      {"plant_id":"10661","generator_id":"GEN4","reported_ba":"CISO","period":"2024-02"},
      {"plant_id":"99999","generator_id":"X","reported_ba":"CISO","period":"2024-02"}])
    r=compare_status_sheets(archive,unmatched)
    a=r[r.generator_id=="TG1"].iloc[0]
    assert a.exact_sheet_matches=="Retired"
    assert a.exact_reported_statuses=="RE"
    assert a.status_resolution=="exact_key_found_in_source"
    assert r[r.generator_id=="GEN4"].iloc[0].status_resolution=="plant_only_found"
    assert r[r.generator_id=="X"].iloc[0].status_resolution=="plant_not_in_generator_workbook"
    assert not r.retirement_or_rename_certified.any()
