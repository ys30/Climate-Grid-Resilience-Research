import csv
from pathlib import Path

import pandas as pd
import pytest

from grid_resilience.paperc_eia930_2024_fuel_schema_bridge import audit_2024


def make_half(path, dates, modern=False, missing_gas=False):
    stem="Net Generation (MW) from "
    cols=["Balancing Authority","UTC Time at End of Hour","Net Generation (MW)",
          stem+"Natural Gas",
          stem+("Wind without Integrated Battery Storage" if modern else "Wind")]
    if modern:cols.append(stem+"Wind with Integrated Battery Storage")
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for t in dates:
            for ba in ("AZPS","BPAT","CISO","SRP"):
                row={"Balancing Authority":ba,
                     "UTC Time at End of Hour":(t+pd.Timedelta(hours=1)).strftime("%m/%d/%Y %I:%M:%S %p"),
                     "Net Generation (MW)":"100",
                     stem+"Natural Gas":"" if missing_gas and ba=="AZPS" else "40",
                     stem+("Wind without Integrated Battery Storage" if modern else "Wind"):"12"}
                if modern:row[stem+"Wind with Integrated Battery Storage"]="3"
                w.writerow(row)


def fixtures(tmp_path):
    times=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    old,new=tmp_path/"Jan.csv",tmp_path/"Jul.csv"
    make_half(old,times[:7])
    make_half(new,times[7:],modern=True)
    return old,new,times


def test_28_hour_partition_recovers_net_and_gas_not_wind(tmp_path):
    old,new,_=fixtures(tmp_path)
    hourly,summary,flags=audit_2024(old,new)
    assert len(hourly)==672
    assert flags["jan_jun_utc_hours"]==28
    assert flags["jul_dec_utc_hours"]==644
    assert flags["source_schema_changed"]
    assert flags["all_natural_gas_168h_complete"]
    assert summary.raw_net_generation_mwh.eq(16800).all()
    assert summary.raw_natural_gas_mwh.eq(6720).all()
    assert summary.legacy_unsplit_wind_hours.eq(7).all()
    assert summary.modern_wind_without_battery_hours.eq(161).all()
    assert summary.modern_wind_with_battery_hours.eq(161).all()
    assert not summary.cross_schema_wind_168h_comparable_certified.any()


def test_gas_missing_in_one_partition_never_imputed(tmp_path):
    old,new,times=fixtures(tmp_path)
    make_half(old,times[:7],missing_gas=True)
    _,summary,flags=audit_2024(old,new)
    assert pd.isna(summary.loc[summary.ba.eq("AZPS"),"raw_natural_gas_mwh"].iloc[0])
    assert not flags["all_natural_gas_168h_complete"]


def test_missing_entire_source_hour_fails(tmp_path):
    old,new,times=fixtures(tmp_path)
    make_half(new,times[8:],modern=True)
    with pytest.raises(ValueError,match="Missing"):
        audit_2024(old,new)


def test_duplicate_source_hour_fails(tmp_path):
    old,new,times=fixtures(tmp_path)
    make_half(new,times[6:],modern=True)
    with pytest.raises(ValueError,match="Overlapping"):
        audit_2024(old,new)
