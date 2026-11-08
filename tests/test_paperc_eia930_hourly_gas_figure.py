import pandas as pd
import pytest
from grid_resilience.paperc_eia930_hourly_gas_figure import validate,BAS,YEARS


def sample():
    rows=[]
    for year,start in YEARS.items():
        for i,t in enumerate(pd.date_range(start,periods=168,freq="h")):
            for ba in BAS:
                rows.append({"year":year,"ba":ba,"utc_hour_start":t.isoformat(),
                "original_fuel_category":"Natural Gas",
                "reported_fuel_mwh":100.0,
                "fuel_value_reported":True,
                "original_partition":"Jul_Dec" if year==2023 or i>=7 else "Jan_Jun"})
    manifest={"2024_wind_solar_hydro_battery_taxonomy_not_harmonized":True,
              "actual_hourly_generation_is_not_available_capacity_or_EENS":True}
    return pd.DataFrame(rows),manifest


def test_distinct_utc_hour_cohorts_and_gas_generation():
    x=validate(*sample())
    assert len(x)==1344
    assert x.groupby(["year","ba"]).relative_study_hour.nunique().eq(168).all()
    assert x.reported_fuel_mwh.eq(100).all()
    assert x.source_original_gas_not_modeled_capacity.all()


def test_missing_reported_gas_rejected():
    x,m=sample()
    x.loc[0,"reported_fuel_mwh"]=float("nan")
    with pytest.raises(ValueError,match="Incomplete raw gas"):
        validate(x,m)


def test_wrong_2024_archive_partition_rejected():
    x,m=sample()
    y=x[x.year.eq(2024)].index[0]
    x.loc[y,"original_partition"]="Jul_Dec"
    with pytest.raises(ValueError,match="boundary"):
        validate(x,m)


def test_missing_physical_calibration_scope_rejected():
    x,m=sample()
    m["actual_hourly_generation_is_not_available_capacity_or_EENS"]=False
    with pytest.raises(ValueError,match="physical-scope"):
        validate(x,m)
