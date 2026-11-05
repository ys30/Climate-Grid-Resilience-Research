import pandas as pd
import pytest
from grid_resilience.eia930_monthly_demand import parse_records,from_official_balance_csv

def records():
    hours=pd.date_range("2024-01-01T01:00:00Z",periods=744,freq="h")
    return [{"period":t.strftime("%Y-%m-%dT%H"),"respondent":"SRP",
             "type":"D","value":"50.5"} for t in hours]

def test_valid_complete_january_utc_month():
    result=parse_records(records(),"SRP",2024,1)
    assert len(result)==744
    assert result.demand_mw.sum()==pytest.approx(744*50.5)
    assert str(result.timestamp.iloc[0])=="2024-01-01 00:00:00+00:00"
    assert str(result.timestamp.iloc[-1])=="2024-01-31 23:00:00+00:00"

def test_missing_hour_fails():
    with pytest.raises(ValueError,match="Incomplete UTC"):
        parse_records(records()[:-1],"SRP",2024,1)

def test_duplicate_hour_fails():
    data=records();data.append(data[0].copy())
    with pytest.raises(ValueError,match="duplicate"):
        parse_records(data,"SRP",2024,1)

def test_other_ba_not_substituted():
    with pytest.raises(ValueError,match="No EIA-930 demand"):
        parse_records(records(),"CISO",2024,1)

def test_original_official_hour_ending_csv_month_conversion(tmp_path):
    h=pd.date_range("2024-01-01T01:00:00Z",periods=744,freq="h")
    source=pd.DataFrame({
        "Balancing Authority":"SRP",
        "UTC Time at End of Hour":h.strftime("%m/%d/%Y %I:%M:%S %p"),
        "Demand (MW)":1200.})
    path=tmp_path/"original_eia930.csv";source.to_csv(path,index=False)
    result=from_official_balance_csv(path,"SRP",2024,1)
    assert len(result)==744
    assert str(result.timestamp.iloc[0])=="2024-01-01 00:00:00+00:00"
    assert str(result.timestamp.iloc[-1])=="2024-01-31 23:00:00+00:00"

def test_original_official_csv_rejects_missing_end_hour(tmp_path):
    h=pd.date_range("2024-01-01T01:00:00Z",periods=743,freq="h")
    source=pd.DataFrame({
        "Balancing Authority":"SRP",
        "UTC Time at End of Hour":h.strftime("%m/%d/%Y %I:%M:%S %p"),
        "Demand (MW)":1200.})
    path=tmp_path/"incomplete.csv";source.to_csv(path,index=False)
    with pytest.raises(ValueError,match="complete valid UTC"):
        from_official_balance_csv(path,"SRP",2024,1)

def test_srp_january_2024_seven_utc_boundary_hours_only_admitted_explicitly(tmp_path):
    h=pd.date_range("2024-01-01T08:00:00Z",periods=737,freq="h")
    source=pd.DataFrame({
        "Balancing Authority":"SRP",
        "UTC Time at End of Hour":h.strftime("%m/%d/%Y %I:%M:%S %p"),
        "Demand (MW)":1200.})
    path=tmp_path/"boundary_original.csv";source.to_csv(path,index=False)
    with pytest.raises(ValueError,match="missing_hours=7"):
        from_official_balance_csv(path,"SRP",2024,1)
    admitted=from_official_balance_csv(path,"SRP",2024,1,
        permit_2024_jan_srp_first_seven_absent=True)
    assert len(admitted)==737
    assert admitted.timestamp.iloc[0]==pd.Timestamp("2024-01-01T07:00:00Z")
    assert admitted.timestamp.iloc[-1]==pd.Timestamp("2024-01-31T23:00:00Z")
    assert not admitted.timestamp.isna().any()


def test_boundary_exception_cannot_hide_nonboundary_missing_hour(tmp_path):
    h=pd.date_range("2024-01-01T08:00:00Z",periods=737,freq="h").delete(20)
    source=pd.DataFrame({
        "Balancing Authority":"SRP",
        "UTC Time at End of Hour":h.strftime("%m/%d/%Y %I:%M:%S %p"),
        "Demand (MW)":1200.})
    path=tmp_path/"interior_missing.csv";source.to_csv(path,index=False)
    with pytest.raises(ValueError,match="missing_hours=8"):
        from_official_balance_csv(path,"SRP",2024,1,
            permit_2024_jan_srp_first_seven_absent=True)
