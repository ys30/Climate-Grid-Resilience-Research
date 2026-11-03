"""Plant-based BA assignment must reveal units absent from Page4 monthly scope."""
import pandas as pd
import pytest
from grid_resilience.eia860_plant_ba_census import census,read_plant_ba

def samples():
    plants=pd.DataFrame({"plant_id":["001","2","3"],"plant_reported_ba":["SRP","SRP","OTHER"]})
    operable=pd.DataFrame({"plant_id":["1","2","3"],"generator_id":["A","B","C"],
        "nameplate_capacity_mw":[100.,30.,50.]})
    page4=pd.DataFrame({"plant_id":["1"],"generator_id":["A"],
        "reported_ba":["SRP"],"period":["2024-01"]})
    return plants,operable,page4

def test_missing_monthly_page4_units_visible_without_zero_imputation():
    d,m=census(*samples())
    assert len(d)==2
    assert m["eia860_plant_assigned_operable_generators"]==2
    assert m["eia860_plant_assigned_nameplate_mw"]==130
    assert m["of_those_appearing_in_eia923_page4_ba_month"]==1
    assert m["plant_assigned_operable_not_in_page4_month"]==1
    assert m["plant_assigned_nameplate_not_in_page4_month_mw"]==30
    assert m["page4_reported_ba_generator_count"]==1
    assert m["page4_reported_ba_not_in_plant_assigned_roster_count"]==0
    assert m["ba_attribution_is_bidirectionally_identical"] is False
    assert m["historical_calibration_certified"] is False

def test_duplicate_plants_fail():
    a,b,c=samples()
    with pytest.raises(ValueError,match="Duplicate EIA-860 plant"):
        census(pd.concat([a,a.iloc[:1]]),b,c)

def test_unrelated_missing_plant_is_reported_but_does_not_block_target_ba():
    a,b,c=samples()
    rows,manifest=census(a.iloc[:2],b,c)
    assert len(rows)==2
    assert manifest["nationwide_operable_records_without_plant_join"]==1

def test_invalid_unrelated_capacity_is_not_used_for_target_ba():
    a,b,c=samples()
    b.loc[2,"nameplate_capacity_mw"]="not-reported"
    rows,manifest=census(a,b,c)
    assert manifest["eia860_plant_assigned_nameplate_mw"]==130.

def test_invalid_target_ba_capacity_fails_closed():
    a,b,c=samples()
    b.loc[1,"nameplate_capacity_mw"]="not-reported"
    with pytest.raises(ValueError,match="target BA generator nameplate"):
        census(a,b,c)

def test_no_target_ba_plant_is_rejected():
    a,b,c=samples()
    a["plant_reported_ba"]="OTHER"
    with pytest.raises(ValueError,match="No EIA-860 operable"):
        census(a,b,c)

def test_duplicate_page4_id_fails():
    a,b,c=samples()
    with pytest.raises(ValueError,match="Duplicate EIA-923"):
        census(a,b,pd.concat([c,c]))

def test_real_zip_shape_plant_header_extraction(tmp_path):
    import io
    import zipfile
    from openpyxl import Workbook
    wb=Workbook()
    ws=wb.active
    ws.title="Plant"
    # Match archived official 2024 workbook positional schema: row 2,
    # Plant Code at zero-based column 3; BA Code at zero-based column 13.
    ws.append(["EIA-860 2024 Schedule 2"]+[None]*14)
    headers=[""]*15
    headers[3]="Plant Code"
    headers[13]="Balancing Authority Code"
    headers[14]="Balancing Authority Name"
    ws.append(headers)
    row=[""]*15
    row[3]=1234
    row[13]="SRP"
    ws.append(row)
    row=[""]*15
    row[3]=5678
    row[13]="PACE"
    ws.append(row)
    buf=io.BytesIO()
    wb.save(buf)
    archive=tmp_path/"sample_eia860.zip"
    with zipfile.ZipFile(archive,"w") as z:
        z.writestr("2___Plant_Y2024.xlsx",buf.getvalue())
    out=read_plant_ba(archive)
    assert out.plant_id.tolist()==["1234","5678"]
    assert out.plant_reported_ba.tolist()==["SRP","PACE"]

def test_malformed_plant_workbook_rejected(tmp_path):
    import io
    import zipfile
    from openpyxl import Workbook
    wb=Workbook();wb.active.title="Plant"
    wb.active.append(["Plant Code","Not a BA header"])
    buf=io.BytesIO();wb.save(buf)
    archive=tmp_path/"invalid_eia860.zip"
    with zipfile.ZipFile(archive,"w") as z:
        z.writestr("2___Plant_Y2024.xlsx",buf.getvalue())
    with pytest.raises(ValueError,match="header not found"):
        read_plant_ba(archive)

def test_page4_ba_attribution_disagrees_with_plant_ba():
    a,b,c=samples()
    # EIA-923 monthly reported SRP, annual EIA-860 Plant assignment OTHER
    c=pd.concat([c,pd.DataFrame({"plant_id":["3"],"generator_id":["C"],
        "reported_ba":["SRP"],"period":["2024-01"]})],ignore_index=True)
    rows,report=census(a,b,c)
    assert len(rows)==2
    assert report["page4_reported_ba_generator_count"]==2
    assert report["page4_reported_ba_not_in_plant_assigned_roster_count"]==1
    assert report["page4_reported_ba_missing_plant_roster_identities"]==[
        {"plant_id":"3","generator_id":"C"}]

def test_page4_generator_absent_from_operable_inventory_is_flagged():
    a,b,c=samples()
    c=pd.concat([c,pd.DataFrame({"plant_id":["999"],"generator_id":["X"],
        "reported_ba":["SRP"],"period":["2024-01"]})],ignore_index=True)
    _,report=census(a,b,c)
    assert report["page4_reported_ba_not_in_plant_assigned_roster_count"]==1
