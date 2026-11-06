import pytest
from grid_resilience.grand_coulee_roosevelt_july2024_source_intake import SOURCES

def test_original_usgs_station_and_elevation_parameter():
    s=SOURCES["usgs_lake_roosevelt_daily"]
    assert "12436000" in s and "62614" in s
    assert "2024-07-01" in s and "2024-07-31" in s

def test_independent_usbr_month_end_forebay_item():
    s=SOURCES["usbr_grand_coulee_monthly_forebay"]
    assert "itemId=5253" in s
    assert "2024-06-28" in s
    assert "2024-08-04" in s
