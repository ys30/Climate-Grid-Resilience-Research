from pathlib import Path
import csv
import pytest
from grid_resilience.usbr_rise_banks_lake_july2024_admit import admit

def fixtures(tmp_path,truncate=False):
    daily=tmp_path/"daily.csv";monthly=tmp_path/"monthly.csv"
    with daily.open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["#DOWNLOAD URL# x"]+[""]*6)
        n=30 if truncate else 31
        for i in range(1,n+1):
            w.writerow(["Banks Lake and Dry Falls Dam (BNK)","Lake/Reservoir Elevation",
                        str(1570+i*.1),"ft","daily","instant",f"2024-07-{i:02d} 19:00:00"])
    with monthly.open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["Grand Coulee Pump Generating Plant","Upper Pond Elevation",
                    "1563.2","ft","monthly","instant","2024-07-01 07:00:00"])
    return daily,monthly

def test_full_31_days_and_one_month_end_not_daily_interpolation(tmp_path):
    d,m,r=admit(*fixtures(tmp_path))
    assert len(d)==31 and len(m)==1
    assert r["banks_2024_july_31_elevation_ft"]>r["banks_2024_july_1_elevation_ft"]
    assert r["grand_coulee_PG_2024_july_month_end_upper_pond_elevation_ft"]==1563.2
    assert not r["pumped_storage_usable_electric_MWh_verified"]

def test_missing_july_day_fails_closed(tmp_path):
    with pytest.raises(ValueError,match="incomplete July"):
        admit(*fixtures(tmp_path,truncate=True))

def test_never_accept_wrong_units(tmp_path):
    a,b=fixtures(tmp_path)
    a.write_text(a.read_text().replace(",ft,daily,",",m,daily,"))
    with pytest.raises(ValueError,match="unexpected unit"):
        admit(a,b)

def test_no_monthly_pond_data_not_assumed_equal_banks_daily(tmp_path):
    a,b=fixtures(tmp_path)
    b.write_text("")
    with pytest.raises(ValueError,match="No original RISE"):
        admit(a,b)
