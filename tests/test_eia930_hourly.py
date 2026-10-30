import pytest
from grid_resilience.eia930_hourly import normalize,fetch

def rows():
    return [{"period":"2024-07-01T00","respondent":ba,"value":"100"} for ba in ("AZPS","CISO")]

def test_good_hour():
    d=normalize(rows(),["AZPS","CISO"],"2024-07-01T00:00:00Z","2024-07-01T01:00:00Z")
    assert len(d)==2 and d.demand_mw.sum()==200

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

def test_requires_api_key_before_network():
    with pytest.raises(ValueError,match="EIA_API_KEY"):
        fetch(["AZPS"],"2024-07-01T00:00:00Z","2024-07-01T01:00:00Z",None)
