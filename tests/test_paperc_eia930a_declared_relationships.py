from pathlib import Path
import pytest
from openpyxl import Workbook
from grid_resilience.paperc_eia930a_declared_relationships import get_year, TARGET


def fixture(tmp_path,year):
    wb=Workbook()
    meta=wb.active
    meta.title="Layout Details"
    meta["B2"]=year
    wb.create_sheet("SUMMARY")
    s2=wb.create_sheet("SCH 2")
    header2=["", "Plant Name","EIA Plant ID","EIA Generator ID",
             "Plant ID (EIA-930A)","Generator ID (EIA-930A)",
             "Electric Generator Technology","Nameplate Capacity (MW) (EIA-860)",
             "Nameplate Capacity (MW) (EIA-930A)"]
    s2.append(header2)
    for ba in sorted(TARGET):
        s2.append([ba,"Plant "+ba,2345,"G1",None,None,
                   "Natural Gas Fired Combined Cycle",120.0,None])
    s4=wb.create_sheet("SCH 4")
    s4.append(["BA Code","Plant Name","EIA Plant ID","EIA Generator ID",
               "Plant ID (EIA-930A)","Generator ID (EIA-930A)",
               "Generator Reported on EIA-930A Schedule 2?",
               "BAs having a Pseudo-Tie or Dynamic Relationship",
               "Electric Generator Technology","Nameplate Capacity (MW) (EIA-860)",
               "Nameplate Capacity (MW) (EIA-930A)"])
    s4.append(["AZPS","Example A",123,"1",None,None,"Yes","GRID, CISO",
               "Conventional Hydroelectric",25,None])
    s4.append(["OUTSIDE","Example B",124,"1",None,None,"No","BPAT",
               "Conventional Hydroelectric",30,None])
    path=tmp_path/f"eia930a_{year}.xlsx"
    wb.save(path)
    return path


def test_year_specific_metered_and_declared_relationships(tmp_path):
    s2,s4,group,pairs=get_year(fixture(tmp_path,2024),2024)
    assert len(s2)==4
    assert set(s2.ba)==TARGET
    assert len(s4)==3
    assert len(pairs)==3
    assert set(s4.declared_partner_ba)=={"GRID","CISO","BPAT"}
    assert not s4.proves_caused_july_pair_reciprocity_discrepancy.any()
    assert not group.nameplate_is_available_generation_mw.any()


def test_official_year_mismatch_rejected(tmp_path):
    with pytest.raises(ValueError,match="calendar year"):
        get_year(fixture(tmp_path,2023),2024)


def test_missing_schedule4_partner_fails_closed(tmp_path):
    path=fixture(tmp_path,2024)
    from openpyxl import load_workbook
    w=load_workbook(path)
    sheet=w["SCH 4"]
    sheet["H2"]=""
    sheet["H3"]=""
    w.save(path)
    with pytest.raises(ValueError,match="No relevant"):
        get_year(path,2024)

def test_mechanism_type_label_is_not_misread_as_ba(tmp_path):
    path=fixture(tmp_path,2024)
    from openpyxl import load_workbook
    book=load_workbook(path)
    book["SCH 4"]["H2"]="PSEUDO TIE"
    book["SCH 4"]["H3"]="DYNAMIC IMPORT"
    book["SCH 4"]["A3"]="CISO"
    book.save(path)
    _,relations,_,pairs=get_year(path,2024)
    assert relations.source_declares_mechanism_category.sum()==2
    assert set(relations.loc[relations.source_declares_mechanism_category,
                             "relationship_original_label"])=={"PSEUDO TIE","DYNAMIC IMPORT"}
    assert relations.loc[relations.source_declares_mechanism_category,
                         "declared_partner_ba"].isna().all()
    assert not pairs.specific_pair_discrepancy_cause_verified.any()
