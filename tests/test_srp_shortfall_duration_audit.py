"""Fast synthetic contract tests for modeled shortfall duration audit."""
import numpy as np
import pandas as pd
import pytest
from grid_resilience.srp_shortfall_duration_audit import summarize

def baseline():
    t=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    a=np.zeros(744)
    a[:24]=100.
    return pd.DataFrame({"timestamp_utc":t.astype(str),
        "modeled_unserved_mw":a,"bus_balance_residual_mw":0.0})

def test_summary_tracks_24h_screen_gap():
    m=summarize(baseline())
    assert m["hours"]==744
    assert m["modeled_unserved_mwh"]==2400
    assert m["hours_with_modeled_unserved"]==24
    assert m["days_with_modeled_unserved"]==1
    assert m["maximum_utc_day"]=="2024-01-01"
    assert m["historical_outages_observed"] is False

def test_no_screen_gap():
    x=baseline();x["modeled_unserved_mw"]=0
    r=summarize(x)
    assert r["top_decile_hours_share_of_unserved_energy"] is None
    assert r["maximum_utc_day"] is None

@pytest.mark.parametrize("change",["missing","duplicate","negative","nonfinite","imbalanced"])
def test_invalid_diagnostics_rejected(change):
    x=baseline()
    if change=="missing":x=x.iloc[:-1]
    elif change=="duplicate":x.loc[1,"timestamp_utc"]=x.loc[0,"timestamp_utc"]
    elif change=="negative":x.loc[0,"modeled_unserved_mw"]=-1
    elif change=="nonfinite":x.loc[0,"modeled_unserved_mw"]=np.inf
    elif change=="imbalanced":x.loc[0,"bus_balance_residual_mw"]=1.
    with pytest.raises(ValueError):
        summarize(x)
