import pandas as pd
import pytest
from grid_resilience.srp_2024_factorial_multiwindow_admission import source_audit


def make(hours=168):
    t=pd.date_range("2024-07-01T07:00:00Z",periods=hours,freq="h")
    bs=["AZPS","BPAT","CISO","SRP"]
    observed=pd.DataFrame([(hour,ba) for hour in t for ba in bs],columns=["timestamp","ba"])
    capacity=pd.DataFrame({"ba":bs})
    return observed,observed.copy(),capacity


def test_four_ba_672_rows_is_one_168h_event_not_four():
    result=source_audit(*make())
    assert result["source_four_ba_hourly_rows"]==672
    assert result["source_distinct_utc_hours"]==168
    assert result["complete_disjoint_168h_windows_possible"]==1
    assert not result["four_week_replication_supported_by_this_source"]


def test_4x168_real_distinct_hours_admitted_when_present():
    result=source_audit(*make(672))
    assert result["source_four_ba_hourly_rows"]==2688
    assert result["complete_disjoint_168h_windows_possible"]==4
    assert result["four_week_replication_supported_by_this_source"]


def test_duplicate_ba_hour_rejected():
    d,w,c=make()
    with pytest.raises(ValueError,match="Duplicated"):
        source_audit(pd.concat([d,d.iloc[[0]]],ignore_index=True),w,c)


def test_missing_ba_hour_rejected():
    d,w,c=make()
    with pytest.raises(ValueError,match="Incomplete BA-hour"):
        source_audit(d.iloc[:-1],w,c)


def test_time_gaps_rejected():
    d,w,c=make()
    t=pd.Timestamp("2024-07-15T00:00:00Z")
    d.loc[d.timestamp.eq("2024-07-01T07:00:00+00:00"),"timestamp"]=t
    w.loc[w.timestamp.eq("2024-07-01T07:00:00+00:00"),"timestamp"]=t
    with pytest.raises(ValueError,match="Noncontiguous"):
        source_audit(d,w,c)
