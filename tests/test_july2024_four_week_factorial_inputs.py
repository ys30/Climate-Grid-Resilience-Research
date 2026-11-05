import numpy as np
import pandas as pd
import pytest
from grid_resilience.july2024_four_week_factorial_inputs import admit_july,BAS,START


def sample():
    hrs=pd.date_range(START,periods=744,freq="h")
    all_dates=pd.date_range(START,periods=672,freq="h")
    demand=pd.DataFrame([{
        "Balancing Authority":b,
        "UTC Time at End of Hour":(t+pd.Timedelta(hours=1)).strftime("%m/%d/%Y %I:%M:%S %p"),
        "Demand (MW)":5000+i+100*np.sin(j*.11)}
        for j,t in enumerate(hrs) for i,b in enumerate(BAS)])
    w=pd.DataFrame([{
        "timestamp":t,"ba":b,"temperature_c":30+i+np.sin(j*.1),
        "wind_availability":.3+.1*np.cos(j*.12)}
        for j,t in enumerate(all_dates) for i,b in enumerate(BAS)])
    c=pd.DataFrame([{"ba":b,"gas_mw":4000+i,"wind_mw":100+i,
                     "source_year":2024,"capacity_source":"GENERIC_THERMAL_PROXY_TEST"}
                    for i,b in enumerate(BAS)])
    return demand,w,c


def test_four_actual_disjoint_windows_and_frozen_source_parameters(tmp_path):
    d,w,c=sample()
    rows,meta=admit_july(d,w,c,tmp_path)
    assert len(rows)==4
    assert rows.distinct_hours.eq(168).all()
    assert set(rows.week)=={1,2,3,4}
    assert meta["source_distinct_hourly_timestamps"]==672
    assert not meta["independent_year_or_month_replication"]
    assert not meta["physical_eens_or_historical_outages_estimated"]
    first=pd.read_csv(tmp_path/"week_1/demand.csv")
    last=pd.read_csv(tmp_path/"week_4/demand.csv")
    assert first.timestamp.nunique()==last.timestamp.nunique()==168
    assert not set(first.timestamp)&set(last.timestamp)
    links=pd.read_csv(tmp_path/"frozen_hypothetical_links.csv")
    assert len(links)==3
    assert links.rating_source.str.startswith("HYPOTHETICAL").all()


def test_reject_missing_official_source_hour(tmp_path):
    d,w,c=sample()
    with pytest.raises(ValueError,match="incomplete"):
        admit_july(d.iloc[:-1],w,c,tmp_path)


def test_reject_duplicate_weather_hour(tmp_path):
    d,w,c=sample()
    w.loc[0,"timestamp"]=w.loc[4,"timestamp"]
    with pytest.raises(ValueError,match="duplicated"):
        admit_july(d,w,c,tmp_path)


def test_reject_weather_source_not_full_28_days(tmp_path):
    d,w,c=sample()
    with pytest.raises(ValueError,match="Incomplete true 672"):
        admit_july(d,w.iloc[:-4],c,tmp_path)


def test_reject_bad_capacity_evidence(tmp_path):
    d,w,c=sample()
    c.loc[0,"capacity_source"]="PHYSICAL_SYSTEM_VERIFIED"
    with pytest.raises(ValueError,match="uncalibrated capacity"):
        admit_july(d,w,c,tmp_path)
