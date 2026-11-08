import csv
from datetime import timedelta
import pandas as pd
import pytest

from grid_resilience.paperc_eia930_halfyear_utc_boundary import audit,BAS


def source(path,starts,wind):
    cols=["Balancing Authority","UTC Time at End of Hour",
          "Net Generation (MW)","Net Generation (MW) from Natural Gas",
          "Net Generation (MW) from "+wind]
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for t in starts:
            for ba in BAS:
                w.writerow({"Balancing Authority":ba,
                    "UTC Time at End of Hour":(t+pd.Timedelta(hours=1)).strftime("%m/%d/%Y %I:%M:%S %p"),
                    "Net Generation (MW)":"100","Net Generation (MW) from Natural Gas":"40",
                    "Net Generation (MW) from "+wind:"20"})


def test_ba_local_archive_splits_do_not_create_missing_utc_hours(tmp_path):
    dates=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    a,b=tmp_path/"jan.csv",tmp_path/"jul.csv"
    source(a,dates[:7],"Wind")
    source(b,dates[7:],"Wind without Integrated Battery Storage")
    result,info=audit(a,b)
    assert len(result)==672
    assert info["source_jan_jun_hours"]==28
    assert info["source_jul_dec_hours"]==644
    assert info["all_utc_ba_hours_source_recovered"]
    assert not info["cross_partitions_fuel_schema_identical"]
    assert all(r["complete_observed_net_168h_mwh"]==16800 for r in info["by_ba"])
    assert all(r["complete_observed_natural_gas_168h_mwh"]==6720 for r in info["by_ba"])


def test_missing_true_source_hours_stay_missing(tmp_path):
    dates=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    a,b=tmp_path/"jan.csv",tmp_path/"jul.csv"
    source(a,dates[:6],"Wind")
    source(b,dates[7:],"Wind")
    result,info=audit(a,b)
    assert info["unrecovered_missing_ba_hours"]==4
    assert not info["all_utc_ba_hours_source_recovered"]
    assert all(r["complete_observed_net_168h_mwh"] is None for r in info["by_ba"])


def test_overlap_not_double_counted(tmp_path):
    dates=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    a,b=tmp_path/"jan.csv",tmp_path/"jul.csv"
    source(a,dates[:8],"Wind")
    source(b,dates[7:],"Wind")
    with pytest.raises(ValueError,match="Duplicate"):
        audit(a,b)
