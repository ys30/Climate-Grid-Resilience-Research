import pandas as pd
import numpy as np
import pytest
from grid_resilience.bpat_july2024_intertemporal_hy_pypsa import (
    validate_source, SETTINGS)

def synthetic_source():
    hours=pd.date_range("2024-07-01T00:00:00Z",periods=672,freq="h")
    d=pd.DataFrame([(t,ba,5000.) for t in hours
         for ba in ("AZPS","BPAT","CISO","SRP")],
         columns=["timestamp","ba","demand_mw"])
    w=d[["timestamp","ba"]].copy()
    w["temperature_c"]=32.
    w["wind_availability"]=.5
    c=pd.DataFrame([{"ba":ba,"gas_mw":3000,"wind_mw":2000,
                    "capacity_source":"GENERIC_THERMAL_PROXY"}
         for ba in ("AZPS","BPAT","CISO","SRP")])
    return d,w,c

def test_exact_672h_original_input_identity():
    d,w,c=synthetic_source()
    x,y,z,t=validate_source(d,w,c,5989476.)
    assert len(t)==672 and len(x)==len(y)==2688
    assert len(z)==4 and len(SETTINGS)==4

def test_reject_missing_source_hours():
    d,w,c=synthetic_source()
    with pytest.raises(ValueError,match="672 source hours"):
        validate_source(d.iloc[:-1],w,c,5989476.)

def test_reject_different_source_month():
    d,w,c=synthetic_source()
    d["timestamp"]=pd.to_datetime(d.timestamp)+pd.Timedelta(days=30)
    with pytest.raises(ValueError,match="source UTC calendar"):
        validate_source(d,w,c,5989476.)

def test_reject_incorrect_eia923_hy_scale():
    d,w,c=synthetic_source()
    with pytest.raises(ValueError,match="independently verified"):
        validate_source(d,w,c,5989000.)

def test_no_fake_calibrated_capacity():
    d,w,c=synthetic_source()
    c.loc[0,"capacity_source"]="COMPLETE_CALIBRATED_HYDRO"
    with pytest.raises(ValueError,match="partial 2024"):
        validate_source(d,w,c,5989476.)
