import pandas as pd
import pytest
from grid_resilience.grand_coulee_july2024_dual_reservoir_stage_panel import pair

def inputs():
    days=pd.date_range("2024-07-01",periods=31,freq="D")
    banks=pd.DataFrame({"date":days.strftime("%Y-%m-%d"),
      "source_record_timestamp":(days+pd.Timedelta(hours=19)).astype(str),
      "elevation_ft":[1568+i*.01 for i in range(31)]})
    roosevelt=pd.DataFrame({"date":days.strftime("%Y-%m-%d"),
      "lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29":[1285+i*.02 for i in range(31)]})
    bs={"dataset_129466_Banks_Lake_observed_July_daily_records":31}
    rs={"USGS_12436000_2024_07_daily_2400_observed_observations":31,
        "USGS_statistic_code":"32400"}
    return banks,roosevelt,bs,rs

def test_same_calendar_not_same_observation_instant():
    x,m=pair(*inputs())
    assert len(x)==31
    assert x.within_original_2024_july_28day_pypsa_window.sum()==28
    assert not m["daily_observations_synchronous"]
    assert not m["inter_reservoir_daily_actual_head_computed"]
    assert x.banks_change_from_july1_ft.iloc[0]==0

def test_wrong_usgs_statistic_is_not_daily_mean():
    a,b,x,y=inputs()
    y["USGS_statistic_code"]="00003"
    with pytest.raises(ValueError,match="USGS 2400"):
        pair(a,b,x,y)

def test_missing_date_not_filled():
    a,b,x,y=inputs()
    with pytest.raises(ValueError,match="Missing or duplicate"):
        pair(a,b.iloc[:-1],x,y)

def test_duplicate_date_not_filled():
    a,b,x,y=inputs()
    b.loc[30,"date"]="2024-07-30"
    with pytest.raises(ValueError,match="Missing or duplicate"):
        pair(a,b,x,y)
