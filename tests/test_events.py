import pandas as pd
import pytest
from grid_resilience.events import identify

def sample():
    hours=pd.date_range("2024-07-01",periods=12,freq="h",tz="UTC")
    return pd.DataFrame([{"timestamp":t,"ba":ba,"temperature_c":36 if i<8 else 25,
                          "wind_availability":.1 if i<8 else .8}
                         for i,t in enumerate(hours) for ba in ("CISO","AZPS")])

def test_identifies_compound_and_single_hazards():
    d=identify(sample(),min_hours=6)
    assert set(d.event_type)=={"heat","low_wind","compound"}
    assert d.active_hours.eq(8).all()

def test_incomplete_hour_is_rejected():
    with pytest.raises(ValueError,match="Incomplete"):
        identify(sample().iloc[:-1])

def test_single_ba_does_not_meet_coherence():
    x=sample()
    x.loc[x.ba.eq("AZPS"),"temperature_c"]=25
    x.loc[x.ba.eq("AZPS"),"wind_availability"]=.8
    assert identify(x,min_bas=2).empty
