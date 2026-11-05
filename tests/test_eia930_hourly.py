import pytest
from grid_resilience.eia930_hourly import normalize,fetch
from grid_resilience.eia930_hour_convention import api_hour_ending_bounds

def rows():
    # End-hour 01:00 describes model hour 00:00–01:00 UTC.
    return [{"period":"2024-07-01T01","respondent":ba,"value":"100"} for ba in ("AZPS","CISO")]

def test_good_hour():
    d=normalize(rows(),["AZPS","CISO"],"2024-07-01T00:00:00Z","2024-07-01T01:00:00Z")
    assert len(d)==2 and d.demand_mw.sum()==200
    assert d.timestamp.dt.strftime("%Y-%m-%dT%H").eq("2024-07-01T00").all()

def test_hour_ending_00_not_wrongly_labeled_hour_start():
    with pytest.raises(ValueError,match="Incomplete"):
        normalize([{"period":"2024-07-01T00","respondent":ba,"value":"100"}
                   for ba in ("AZPS","CISO")],
                  ["AZPS","CISO"],"2024-07-01T00:00:00Z","2024-07-01T01:00:00Z")

def test_rejects_missing_ba():
    with pytest.raises(ValueError,match="Incomplete"):
        normalize(rows()[:1],["AZPS","CISO"],"2024-07-01T00:00:00Z","2024-07-01T01:00:00Z")

def test_rejects_duplicate():
    with pytest.raises(ValueError,match="Duplicate"):
        normalize(rows()+rows()[:1],["AZPS","CISO"],"2024-07-01T00:00:00Z","2024-07-01T01:00:00Z")

def test_rejects_nonpositive():
    r=rows();r[0]["value"]="0"
    with pytest.raises(ValueError,match="nonpositive"):
        normalize(r,["AZPS","CISO"],"2024-07-01T00:00:00Z","2024-07-01T01:00:00Z")

def test_api_query_inclusive_ends_after_last_model_hour():
    st,en=api_hour_ending_bounds("2024-07-01T00:00Z","2024-07-08T00:00Z")
    assert st.strftime("%Y-%m-%dT%H")=="2024-07-01T01"
    assert en.strftime("%Y-%m-%dT%H")=="2024-07-08T00"

def test_requires_api_key_before_network():
    with pytest.raises(ValueError,match="EIA_API_KEY"):
        fetch(["AZPS"],"2024-07-01T00:00:00Z","2024-07-01T01:00:00Z",None)
