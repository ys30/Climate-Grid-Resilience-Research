import numpy as np
import pandas as pd
import pytest
from grid_resilience.srp_epa_2024_january_july_observed_seasonal import (
    EXPECTED_UNITS, january_join, compare,
)


def synthetic():
    utc_jan=pd.date_range("2024-01-01T07:00:00Z",periods=744,freq="h")
    utc_jul=pd.date_range("2024-07-01T07:00:00Z",periods=744,freq="h")
    p=[];q=[]
    for plant,units in EXPECTED_UNITS.items():
        for u in sorted(units):
            p.append(pd.DataFrame({
                "facility_id":plant,"unit_id":u,
                "date_local_standard":(utc_jan-pd.Timedelta(hours=7)).strftime("%Y-%m-%d"),
                "hour_local_standard":(utc_jan-pd.Timedelta(hours=7)).hour,
                "operating_time":np.ones(744),
                "gross_load_mw":np.ones(744)*100,
                "heat_input_mmbtu":np.ones(744)*500
            }))
            q.append(pd.DataFrame({
                "facility_id":plant,"unit_id":u,"timestamp_utc":utc_jul,
                "temperature_2m_c":np.ones(744)*40,
                "operating_time":np.ones(744),
                "gross_load_mw":np.ones(744)*110,
                "era5_full_local_july_matched":True
            }))
    w=pd.concat([pd.DataFrame({
        "plant_id":plant,"technology":"gas",
        "timestamp_utc":pd.date_range("2024-01-01T00:00:00Z",periods=744,freq="h"),
        "temperature_2m_c":np.ones(744)*10})
        for plant in EXPECTED_UNITS],ignore_index=True)
    return pd.concat(p,ignore_index=True),w,pd.concat(q,ignore_index=True)


def test_historical_source_clock_737_and_cohort_comparison():
    e,w,j=synthetic()
    joined=january_join(e,w)
    assert len(joined)==7440
    assert joined.observed_utc_month_weather_matched.sum()==7370
    result,delta,m=compare(joined,j)
    assert len(result)==20 and len(delta)==10
    assert delta.july_minus_january_temperature_c.eq(30).all()
    assert delta.july_minus_january_conditional_gross_load_mw.eq(10).all()
    assert not m["transfer_validation_of_july_temperature_slope"]
    assert not m["causal_heat_derating_or_eens_estimated"]


def test_reject_duplicate_source_hour():
    e,w,_=synthetic()
    with pytest.raises(ValueError,match="Duplicate source"):
        january_join(pd.concat([e,e.iloc[[0]]],ignore_index=True),w)


def test_reject_missing_epa_unit_or_hour():
    e,w,_=synthetic()
    with pytest.raises(ValueError,match="Incomplete original EPA January"):
        january_join(e.iloc[:-1],w)


def test_reject_missing_plant_weather():
    e,w,_=synthetic()
    with pytest.raises(ValueError,match="missing or duplicated"):
        january_join(e,w.loc[w.plant_id.ne("147")])


def test_missing_source_operating_not_zero_filled():
    e,w,j=synthetic()
    e.loc[0,"operating_time"]=np.nan
    observed=january_join(e,w)
    assert pd.isna(observed.loc[0,"operating_time"])
    frame,_,_=compare(observed,j)
    assert len(frame)==20


def test_reject_non_january_month():
    e,w,_=synthetic()
    e.loc[0,"date_local_standard"]="2024-07-01"
    with pytest.raises(ValueError,match="Invalid January"):
        january_join(e,w)


def test_july_source_calendar_cannot_be_shorter_than_january():
    e,w,j=synthetic()
    with pytest.raises(ValueError,match="Unequal or incomplete"):
        compare(january_join(e,w),j.iloc[:-8])
