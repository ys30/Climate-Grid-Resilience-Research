"""Fast source-boundary checks; PyPSA not required."""
import numpy as np
import pandas as pd
import pytest
from grid_resilience.exchange_boundary_preflight import validate_boundary

@pytest.fixture
def month():
    timestamps=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    return pd.DataFrame({"timestamp":timestamps,"demand_mw":50.0,
        "interchange_mw":[-70.0 if i%2==0 else 20.0 for i in range(744)]})

def test_signed_month(month):
    checked=validate_boundary(month.sample(frac=1,random_state=7),2024,1)
    assert len(checked)==744
    assert checked.observed_import_mw.sum()==372*70
    assert checked.observed_export_mw.sum()==372*20
    assert np.allclose(checked.observed_export_mw-checked.observed_import_mw,checked.interchange_mw)

@pytest.mark.parametrize("mutation",["missing","duplicate","shift","nan","infinite","negative_demand"])
def test_bad_source_fail_closed(month,mutation):
    x=month.copy()
    if mutation=="missing": x=x.iloc[:-1]
    elif mutation=="duplicate": x.loc[1,"timestamp"]=x.loc[0,"timestamp"]
    elif mutation=="shift": x["timestamp"]=x["timestamp"]+pd.Timedelta(hours=1)
    elif mutation=="nan": x.loc[0,"interchange_mw"]=np.nan
    elif mutation=="infinite": x.loc[0,"interchange_mw"]=np.inf
    elif mutation=="negative_demand": x.loc[0,"demand_mw"]=-1.0
    with pytest.raises(ValueError):
        validate_boundary(x,2024,1)

def test_leap_year():
    t=pd.date_range("2024-02-01",periods=696,freq="h",tz="UTC")
    x=pd.DataFrame({"timestamp":t,"demand_mw":1.0,"interchange_mw":0.0})
    assert len(validate_boundary(x,2024,2))==696
