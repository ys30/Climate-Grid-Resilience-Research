"""Synthetic official-style workbook probe, including Energy Source 3."""
import io
import zipfile

import pandas as pd
import pytest
from openpyxl import Workbook

from grid_resilience.srp_eia860_full_fuel_field_probe import probe


def fixture(path, third_fuel="DFO"):
    wb=Workbook()
    ws=wb.active
    ws.title="Operable"
    ws.append(["Official workbook preamble"])
    ws.append(["Plant Code","Generator ID","Prime Mover",
               "Energy Source 1","Energy Source 2","Energy Source 3"])
    ws.append([6177,"CO1","ST","SUB","",third_fuel])
    ws.append([6177,"CO2","ST","SUB","",None])
    buffer=io.BytesIO()
    wb.save(buffer)
    with zipfile.ZipFile(path,"w") as archive:
        archive.writestr("3_1_Generator_Y2024.xlsx",buffer.getvalue())


def page1():
    return pd.DataFrame({
        "plant_id":["6177"],"reported_ba":["SRP"],"period":["2024-01"],
        "prime_mover":["ST"],"reported_fuel":["DFO"],"net_generation_mwh":[160.391]
    })


def test_finds_third_energy_source_without_assigning_generation(tmp_path):
    p=tmp_path/"eia860.zip"
    fixture(p)
    generators,source,m=probe(p,page1())
    assert len(generators)==2
    assert m["matching_generator_ids"]==["CO1"]
    assert "Energy Source 3" in m["source_fuel_fields"]
    assert m["eia923_signed_net_mwh"]==160.391
    assert not m["generator_fuel_identity_certified"]
    assert len(source)==1


def test_absent_from_all_fields_is_a_scope_flag_not_missing_generation(tmp_path):
    p=tmp_path/"eia860.zip"
    fixture(p,third_fuel="")
    _,_,m=probe(p,page1())
    assert m["generators_with_fuel_in_any_source_field"]==0
    assert m["eia923_signed_net_mwh"]==160.391


def test_no_matching_source_page1_fails(tmp_path):
    p=tmp_path/"eia860.zip"
    fixture(p)
    with pytest.raises(ValueError,match="No selected EIA-923"):
        probe(p,page1(),reported_fuel="RFO")
