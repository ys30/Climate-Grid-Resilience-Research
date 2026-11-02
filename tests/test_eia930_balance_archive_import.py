import io,zipfile
import pandas as pd
import pytest
from grid_resilience.eia930_balance_archive_import import extract

def fixture(tmp_path, missing=False):
    hours=pd.date_range("2024-01-01T01:00:00Z",periods=744,freq="h")
    d=pd.DataFrame({"Balancing Authority":"SRP","UTC Time at End of Hour":hours.strftime("%m/%d/%Y %H:%M"),
                    "Demand (MW)":100})
    if missing:d=d.iloc[:-1]
    dest=tmp_path/"data.zip"
    with zipfile.ZipFile(dest,"w") as f:f.writestr("EIA930_BALANCE_2024_Jan_Jun.csv",d.to_csv(index=False))
    return dest

def test_exact_744_and_end_hour(tmp_path):
    p=extract(fixture(tmp_path),"SRP",2024,1)
    assert len(p)==744
    assert p.timestamp.iloc[0]==pd.Timestamp("2024-01-01T00:00:00Z")
    assert p.timestamp.iloc[-1]==pd.Timestamp("2024-01-31T23:00:00Z")
    assert p.demand_mw.sum()==74400

def test_missing_hour_fail(tmp_path):
    with pytest.raises(ValueError,match="Incomplete UTC hours"):
        extract(fixture(tmp_path,True),"SRP",2024,1)

def test_missing_ba_fail(tmp_path):
    with pytest.raises(ValueError,match="No records"):
        extract(fixture(tmp_path),"CISO",2024,1)
