import pandas as pd
import pytest
from grid_resilience.eia930_monthly_demand import parse_records

def records():
    hours=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    return [{"period":t.strftime("%Y-%m-%dT%H"),"respondent":"SRP",
             "type":"D","value":"50.5"} for t in hours]

def test_valid_complete_january_utc_month():
    result=parse_records(records(),"SRP",2024,1)
    assert len(result)==744
    assert result.demand_mw.sum()==pytest.approx(744*50.5)

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
