import pandas as pd
import pytest
from grid_resilience.paperc_independent_period_gate import inspect_window, audit_periods

BAS=("AZPS","BPAT","CISO","SRP")
EVIDENCE={"official_hour_start_demand":True,"documented_weather_source":True,
          "frozen_capacity_convention":True,"source_provenance_available":True}


def window(start, id_="w1"):
    dates=pd.date_range(start,periods=168,freq="h")
    d=pd.DataFrame([(t,ba,100.) for t in dates for ba in BAS],
                   columns=["timestamp","ba","demand_mw"])
    w=d[["timestamp","ba"]].copy()
    c=pd.DataFrame({"ba":BAS})
    return inspect_window(id_,d,w,c,EVIDENCE)


def test_four_adjacent_july_windows_not_cross_season_holdout():
    rows=[window(f"2024-07-{day:02d}T00:00:00Z",f"week{i}")
          for i,day in enumerate((1,8,15,22),1)]
    x=audit_periods(rows)
    assert x["candidate_windows"]==4
    assert x["distinct_meteorological_season_years"]==1
    assert not x["cross_period_holdout_source_admitted"]


def test_genuine_other_year_source_candidate_is_separate_period():
    x=audit_periods([window("2024-07-01T00:00:00Z"),
                     window("2025-07-01T00:00:00Z","w2")])
    assert x["different_calendar_year_candidate_available"]
    assert x["cross_period_holdout_source_admitted"]
    assert not x["independent_statistical_events_established"]


def test_same_year_distinct_season_is_period_holdout():
    x=audit_periods([window("2024-01-08T00:00:00Z"),
                     window("2024-07-01T00:00:00Z","w2")])
    assert not x["different_calendar_year_candidate_available"]
    assert x["different_season_candidate_available"]


def test_overlap_and_duplicate_id_rejected():
    a=window("2024-07-01T00:00:00Z")
    b=window("2024-07-02T00:00:00Z","w2")
    with pytest.raises(ValueError,match="overlap"):
        audit_periods([a,b])
    with pytest.raises(ValueError,match="Duplicate"):
        audit_periods([a,a])


def test_missing_ba_hour_rejected():
    dates=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    d=pd.DataFrame([(t,ba) for t in dates for ba in BAS],columns=["timestamp","ba"])
    w=d.iloc[:-1]
    with pytest.raises(ValueError,match="168 hours x four BA"):
        inspect_window("broken",d,w,pd.DataFrame({"ba":BAS}),EVIDENCE)


def test_crossing_season_boundary_rejected():
    dates=pd.date_range("2024-08-29T00:00:00Z",periods=168,freq="h")
    d=pd.DataFrame([(t,ba) for t in dates for ba in BAS],columns=["timestamp","ba"])
    with pytest.raises(ValueError,match="season boundary"):
        inspect_window("boundary",d,d.copy(),pd.DataFrame({"ba":BAS}),EVIDENCE)


def test_provenance_not_assumed():
    dates=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    d=pd.DataFrame([(t,ba) for t in dates for ba in BAS],columns=["timestamp","ba"])
    evidence=dict(EVIDENCE,official_hour_start_demand=False)
    with pytest.raises(ValueError,match="provenance"):
        inspect_window("nohour",d,d.copy(),pd.DataFrame({"ba":BAS}),evidence)
