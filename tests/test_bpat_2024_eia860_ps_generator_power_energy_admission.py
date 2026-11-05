import io
import zipfile
import pandas as pd
import pytest
from openpyxl import Workbook
from grid_resilience.bpat_2024_eia860_ps_generator_power_energy_admission import audit

def archive(tmp_path):
    wb=Workbook()
    ws=wb.active;ws.title="Plant"
    ws.append(["EIA information"])
    ws.append(["Plant Code","Balancing Authority Code"])
    ws.append([10,"BPAT"])
    ws.append([20,"AZPS"])
    mem=io.BytesIO();wb.save(mem)
    z=tmp_path/"eia8602024.zip"
    with zipfile.ZipFile(z,"w") as f:
        f.writestr("2___Plant_Y2024.xlsx",mem.getvalue())
    return z

def records():
    g=pd.DataFrame([
        {"plant_id":"10","generator_id":"PS1","prime_mover":"PS",
         "reported_technology":"Pumped Storage","nameplate_capacity_mw":"120",
         "status":"OP","energy_source_1":"WAT"},
        {"plant_id":"10","generator_id":"BAT1","prime_mover":"BA",
         "reported_technology":"Battery Storage","nameplate_capacity_mw":"100",
         "status":"OP","energy_source_1":"MWH"},
        {"plant_id":"20","generator_id":"PS2","prime_mover":"PS",
         "reported_technology":"Pumped Storage","nameplate_capacity_mw":"70",
         "status":"OP","energy_source_1":"WAT"}])
    s=pd.DataFrame([
        {"plant_id":"10","generator_id":"BAT1","energy_mwh":"400","charge_mw":"100",
         "discharge_mw":"100","storage_technology":"Battery",
         "operating_year":"2021","operating_month":"1"},
        {"plant_id":"10","generator_id":"PS1","energy_mwh":"500","charge_mw":"90",
         "discharge_mw":"100","storage_technology":"Pumped hydro",
         "operating_year":"2020","operating_month":"1"}])
    return g,s

def test_exact_ps_source_verified_not_battery(tmp_path):
    g,s=records()
    ps,storage,m=audit(archive(tmp_path),g,s)
    assert m["bpat_ps_prime_mover_records"]==1
    assert m["bpat_ps_source_complete_mw_mwh_records"]==1
    assert m["bpat_ps_source_complete_reported_energy_mwh"]==500
    assert m["bpat_eia860_storage_sheet_all_technologies_rows"]==2
    assert m["physical_ps_672h_dispatch_parameters_admitted"]
    assert not m["initial_soc_verified"]

def test_ps_missing_energy_fields_is_not_converted_from_battery(tmp_path):
    g,s=records()
    s=s.loc[s.generator_id.eq("BAT1")]
    _,storage,m=audit(archive(tmp_path),g,s)
    assert m["bpat_ps_prime_mover_records"]==1
    assert m["bpat_ps_exact_generator_storage_sheet_matches"]==0
    assert not m["physical_ps_672h_dispatch_parameters_admitted"]
    assert m["bpat_storage_sheet_complete_power_energy_rows"]==1

def test_future_operation_date_rejected(tmp_path):
    g,s=records()
    s.loc[s.generator_id.eq("PS1"),"operating_year"]="2025"
    _,_,m=audit(archive(tmp_path),g,s)
    assert not m["physical_ps_672h_dispatch_parameters_admitted"]

def test_duplicate_generator_keys_rejected(tmp_path):
    g,s=records()
    with pytest.raises(ValueError,match="Duplicate"):
        audit(archive(tmp_path),pd.concat([g,g.iloc[[0]]]),s)
