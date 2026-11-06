from pathlib import Path
import pytest
from grid_resilience.grand_coulee_roosevelt_july2024_admit import admit

def inputs(tmp_path,days=31):
    a=tmp_path/"usgs.rdb";b=tmp_path/"usbr.csv"
    data=["# USGS original test","agency_cd\tsite_no\tdatetime\t123_62614_00003\t123_62614_00003_cd",
          "5s\t15s\t20d\t14n\t10s"]
    for n in range(1,days+1):
        data.append(f"USGS\t12436000\t2024-07-{n:02d}\t1286.50\tA")
    a.write_text("\n".join(data)+"\n")
    b.write_text('''"#SERIES DATA#","","","","","","",""
"Grand Coulee Power Plant","End of Month Forebay Elevation","1286.24","ft","monthly","instant","2024-07-01 06:00:00","Although values are dated as the first of each month they represent the end of month value for that month."
''')
    return a,b

def test_usgs_daily_31_and_one_usbr_month():
    a,b=inputs(Path(__import__("tempfile").mkdtemp()))
    x,m=admit(a,b)
    assert len(x)==31 and m["USGS_12436000_2024_07_daily_mean_observations"]==31
    assert m["USBR_5253_2024_07_monthly_Grand_Coulee_forebay_ft"]==1286.24
    assert not m["direct_bank_lake_minus_roosevelt_daily_head_m_permitted"]

def test_missing_usgs_one_day_rejected(tmp_path):
    with pytest.raises(ValueError,match="missing July"):
        admit(*inputs(tmp_path,30))

def test_wrong_usgs_station_rejected(tmp_path):
    a,b=inputs(tmp_path)
    a.write_text(a.read_text().replace("12436000","12436001"))
    with pytest.raises(ValueError,match="station identity"):
        admit(a,b)

def test_wrong_monthly_frequency_rejected(tmp_path):
    a,b=inputs(tmp_path)
    b.write_text(b.read_text().replace('"monthly"','"daily"'))
    with pytest.raises(ValueError,match="unit/frequency"):
        admit(a,b)
