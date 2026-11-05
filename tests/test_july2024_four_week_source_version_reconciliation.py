import pandas as pd
import pytest
from grid_resilience.july2024_four_week_source_version_reconciliation import audit

def source():
    h=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    b=("AZPS","BPAT","CISO","SRP")
    x=pd.DataFrame([(t,ba) for t in h for ba in b],columns=["timestamp","ba"])
    x["demand_mw"]=5000.
    y=x[["timestamp","ba"]].copy()
    y["temperature_c"]=35.
    y["wind_availability"]=.2
    return x,y


def test_repeated_same_sources_are_exactly_identical():
    d,w=source()
    r,m=audit(d,d.copy(),w,w.copy())
    assert len(r)==12 and r.source_values_identical.all()
    assert m["model_interaction_difference_can_be_labeled_exact_reproduction"]


def test_changed_era5_hour_detected_even_with_same_source_time_keys():
    d,w=source()
    newer=w.copy()
    newer.loc[10,"temperature_c"]+=2.
    r,m=audit(d,d,w,newer)
    row=r.loc[(r.ba=="CISO")&(r.field=="temperature_c")].iloc[0]
    assert row.values_differing_above_1e8_tolerance==1
    assert not m["all_numeric_source_values_identical"]
    assert not m["model_interaction_difference_can_be_labeled_exact_reproduction"]


def test_missing_original_hour_rejected():
    d,w=source()
    with pytest.raises(ValueError,match="size"):
        audit(d.iloc[:-1],d,w,w)


def test_swapped_timestamp_rejected():
    d,w=source()
    shifted=d.copy()
    shifted["timestamp"]=shifted.timestamp+pd.Timedelta(days=1)
    with pytest.raises(ValueError,match="Different first-week"):
        audit(d,shifted,w,w)
