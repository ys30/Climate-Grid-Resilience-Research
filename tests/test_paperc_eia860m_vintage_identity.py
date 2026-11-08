import pandas as pd
import pytest
from openpyxl import Workbook
from grid_resilience.paperc_eia860m_vintage_identity import inventory,reconcile

def xlsx(tmp_path,month):
    wb=Workbook();ws=wb.active;ws.title="Operating"
    ws.append([f"Inventory of Operating Generators as of {month.capitalize()} 2025"])
    ws.append([])
    ws.append(["Plant ID","Generator ID","Balancing Authority Code",
               "Nameplate Capacity (MW)","Technology","Energy Source Code",
               "Prime Mover Code","Status"])
    ws.append([101,"A","AZPS",100,"Natural Gas","NG","CT","(OP) Operating"])
    ws.append([102,"B","BPAT",50,"Wind","WND","WT","(OP) Operating"])
    path=tmp_path/f"{month}.xlsx";wb.save(path)
    return path

def source():
    roster=pd.DataFrame([
        {"year":2024,"ba":"AZPS","plant_id_source":"101","generator_id_source":"A",
         "technology":"Natural Gas","reported_nameplate_mw":100,
         "eia860_generator_id_recognized":True},
        {"year":2024,"ba":"BPAT","plant_id_source":"102","generator_id_source":"B",
         "technology":"Wind","reported_nameplate_mw":50,
         "eia860_generator_id_recognized":True},
        {"year":2024,"ba":"CISO","plant_id_source":"103","generator_id_source":"C",
         "technology":"Solar","reported_nameplate_mw":30,
         "eia860_generator_id_recognized":True},
        {"year":2024,"ba":"SRP","plant_id_source":"104","generator_id_source":"D",
         "technology":"Hydro","reported_nameplate_mw":10,
         "eia860_generator_id_recognized":False}])
    annual=pd.DataFrame({"year":[2024]*4,"ba":["AZPS","BPAT","CISO","SRP"],
           "eia930a_row":[0,1,2,3],"match_class":["matched_identity_same_plant_ba",
           "unmatched_in_sameyear_eia860_operable","matched_identity_same_plant_ba",
           "no_eia930a_source_identity"]})
    return roster,annual

def test_monthly_source_exact_id_and_changed_vintage(tmp_path):
    monthly=inventory(xlsx(tmp_path,"august"),"august")
    roster,annual=source()
    detail,transition,summ,scope=reconcile(roster,monthly,annual,2024,"august")
    assert len(detail)==4
    assert detail.match_category_changed_between_vintages.sum()==2
    assert summ.monthly_same_ba_matches.sum()==2
    assert summ.monthly_unmatched.sum()==1
    assert summ.monthly_no_verified_identity.sum()==1
    assert not scope["actual_hourly_dispatch_or_EENS_calibrated"]

def test_wrong_month_header_rejected(tmp_path):
    with pytest.raises(ValueError,match="title"):
        inventory(xlsx(tmp_path,"february"),"august")

def test_monthly_duplicate_identity_not_allowed(tmp_path):
    path=xlsx(tmp_path,"august")
    from openpyxl import load_workbook
    wb=load_workbook(path);wb["Operating"].append([101,"A","AZPS",100,"Natural Gas","NG","CT","(OP) Operating"]);wb.save(path)
    with pytest.raises(ValueError,match="repeated"):
        inventory(path,"august")

def test_annual_row_alignment_required(tmp_path):
    monthly=inventory(xlsx(tmp_path,"august"),"august")
    roster,annual=source()
    with pytest.raises(ValueError,match="fully aligned"):
        reconcile(roster,monthly,annual.iloc[:-1],2024,"august")
