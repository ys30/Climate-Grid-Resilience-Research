"""Guard against interpreting EIA-930 observed exchange as thermal capacity."""
import csv
from datetime import datetime,timedelta,timezone
import pandas as pd
import pytest
from grid_resilience.eia930_bilateral_aggregation import run

BAS=("CISO","AZPS","BPAT","SRP")

def fixture(tmp_path,duplicate=False,nonfinite=False):
    path=tmp_path/"exchange.csv"
    with path.open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["Balancing Authority","Directly Interconnected Balancing Authority","Interchange (MW)","UTC Time at End of Hour"])
        for ba in BAS:
            for i in range(696):
                t=datetime(2024,2,1,tzinfo=timezone.utc)+timedelta(hours=i+1)
                row=[ba,"OTHER","NaN" if nonfinite and i==0 else "15",t.strftime("%m/%d/%Y %I:%M:%S %p")]
                w.writerow(row)
                if duplicate and ba=="BPAT" and i==0:w.writerow(row)
    return path

def test_bilateral_exchange_is_not_line_rating(tmp_path):
    result=run(fixture(tmp_path),tmp_path/"output")
    assert result["historical_calibration_certified"] is False
    assert all(result["hours_by_ba"][ba]==696 for ba in BAS)
    out=pd.read_csv(tmp_path/"output"/"bilateral_hourly_totals.csv")
    assert len(out)==2784
    assert set(out.sum_bilateral_interchange_mw)=={15.0}
    assert "not independently validated transmission capacity" in result["interpretation"]

def test_repeated_counterpart_is_rejected(tmp_path):
    with pytest.raises(ValueError,match="Repeated counterpart"):
        run(fixture(tmp_path,duplicate=True),tmp_path/"output")

def test_nonfinite_exchange_is_rejected(tmp_path):
    with pytest.raises(ValueError,match="Nonfinite interchange"):
        run(fixture(tmp_path,nonfinite=True),tmp_path/"output")
