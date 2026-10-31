import csv
from datetime import datetime,timedelta,timezone
import pytest
from grid_resilience.eia930_six_month_demand import extract,BAS,FORMAT

def fixture(tmp_path,missing=False):
    p=tmp_path/"source.csv"
    with p.open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["Balancing Authority","UTC Time at End of Hour","Demand (MW)"])
        t=datetime(2024,2,1,tzinfo=timezone.utc)
        for h in range(3):
            for ba in BAS:
                w.writerow([ba,(t+timedelta(hours=h+1)).strftime(FORMAT),"" if missing and h==1 and ba=="SRP" else 100])
    return p

def test_hour_end_converted_to_hour_start(tmp_path):
    result=extract(fixture(tmp_path),tmp_path/"out",hours=3)
    assert result["rows"]==12
    with (tmp_path/"out"/"hourly_ba_demand.csv").open() as f:
        rows=list(csv.DictReader(f))
    assert rows[0]["timestamp"]=="2024-02-01T00:00:00+00:00"

def test_missing_raw_is_not_imputed(tmp_path):
    with pytest.raises(ValueError,match="Incomplete raw demand"):
        extract(fixture(tmp_path,True),tmp_path/"out",hours=3)
