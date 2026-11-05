import pytest
from grid_resilience.usbr_rise_banks_lake_july2024_discovery import (
    inspect, request_url, SOURCES)

def test_source_url_is_explicit_2024_original_daily_banks():
    x=request_url(SOURCES["banks_lake_daily"]["item_id"])
    assert "itemId=129466" in x and "2024-06-28" in x
    assert "2024-08-04" in x

def test_source_headers_preview():
    x=inspect(b"date,elevation_ft,qualifier\n2024-07-01,1570.1,A\n2024-07-02,1570.2,A\n")
    assert x["row_count_including_header"]==3
    assert x["header"][1]=="elevation_ft"

def test_json_payload_fails_closed():
    with pytest.raises(ValueError,match="Expected CSV"):
        inspect(b'{"errors":[{"detail":"bad source"}]}')

def test_html_payload_fails_closed():
    with pytest.raises(ValueError,match="Expected CSV"):
        inspect(b"<html><body>request unavailable</body></html>")

def test_empty_source_fails_closed():
    with pytest.raises(ValueError):
        inspect(b"")
