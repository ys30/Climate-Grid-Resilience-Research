from pathlib import Path
import pytest
from grid_resilience.usace_grand_coulee_july2024_pump_observation_admit import admit

H=["Day of Month","Midnight Reservoir Elevation","Banks Lake Pump kcfs",
   "Banks Lake Pump MWh","Banks Lake Elev"]

def fixture(tmp_path,days=31,month="July 2024",missing_day=None):
    p=tmp_path/"project.html"
    s=["<html><h1>Grand Coulee Dam</h1>",f"<h2>{month}</h2>","<table><tr>"]
    s.extend(f"<th>{h}</th>" for h in H)
    s.append("</tr>")
    for i in range(1,days+1):
        c=[str(i),"1286.1","10.4",
           "" if i==missing_day else "7000","1568.1"]
        s.append("<tr>"+"".join(f"<td>{x}</td>" for x in c)+"</tr>")
    s.append("</table></html>")
    p.write_text("".join(s));return p

def test_original_explicit_31day_source_with_pumping():
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as tmp:
        x,m=admit(fixture(Path(tmp)))
        assert len(x)==31
        assert m["pumping_energy_nonmissing_days"]==31
        assert m["pumping_mwh_complete_31day_total"]==217000
        assert m["USACE_pumping_MWh_is_project_wide_not_verified_reversible_PG7_PG12_only"]

def test_missing_pump_report_remains_missing_and_total_null(tmp_path):
    x,m=admit(fixture(tmp_path,missing_day=15))
    assert m["pumping_energy_nonmissing_days"]==30
    assert m["pumping_mwh_complete_31day_total"] is None

def test_incomplete_july_calendar_not_admitted(tmp_path):
    with pytest.raises(ValueError,match="31 USACE"):
        admit(fixture(tmp_path,days=30))

def test_current_month_mistaken_for_2024_rejected(tmp_path):
    with pytest.raises(ValueError,match="specifically July 2024"):
        admit(fixture(tmp_path,month="November 2026"))
