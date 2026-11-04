import pandas as pd
import pytest
from grid_resilience.srp_epa_era5_july_exposure_strata import summarize


def example():
    hours=pd.date_range("2024-07-01T07:00Z",periods=744,freq="h")
    frames=[]
    for site,units in (("141",("1","2")),("55129",("DBG1",)),
                       ("147",("K-7",))):
        for unit in units:
            temp=[31.]*200+[37.]*200+[42.]*337+[float("nan")]*7
            frames.append(pd.DataFrame({
                "facility_id":site,"unit_id":unit,"timestamp_utc":hours,
                "temperature_2m_c":temp,
                "era5_july_hour_matched":[True]*737+[False]*7,
                "operating_time":[1.]*300+[0.]*444,
                "gross_load_mw":[80.]*300+[float("nan")]*444}))
    return pd.concat(frames,ignore_index=True)


def test_descriptive_counts_and_weather_deduplication():
    a,w,m=summarize(example())
    assert len(a)==12
    assert a.groupby(["facility_id","epa_unit_id"]).source_weather_hour_count.sum().eq(737).all()
    assert w.groupby("facility_id").unique_site_weather_hours.sum().eq(737).all()
    assert w.loc[w.facility_id.eq("141"),"unique_site_weather_hours"].sum()==737
    assert not m["causal_thermal_derating_or_outage_identified"]
    assert m["gross_load_conditioned_on_positive_operation_only"]


def test_weather_value_missing_in_admitted_hour_rejected():
    df=example()
    df.loc[0,"temperature_2m_c"]=float("nan")
    with pytest.raises(ValueError,match="weather presence"):
        summarize(df)


def test_bad_source_calendar_match_rejected():
    df=example()
    df.loc[0,"era5_july_hour_matched"]=False
    with pytest.raises(ValueError,match="weather presence"):
        summarize(df)


def test_duplicate_epa_hour_rejected():
    df=example()
    with pytest.raises(ValueError,match="Duplicate"):
        summarize(pd.concat([df,df.iloc[[0]]],ignore_index=True))


def test_invalid_operating_fraction_rejected():
    df=example()
    df.loc[0,"operating_time"]=1.2
    with pytest.raises(ValueError,match="outside"):
        summarize(df)
