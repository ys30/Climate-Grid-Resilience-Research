"""Solver-independent validation for hourly EIA-930 interchange boundaries.

The model distinguishes net export (+) from net import (-). Source records
must cover an entire UTC month, exactly once per hour.
"""
import calendar
import numpy as np
import pandas as pd

def validate_boundary(balance, year, month):
    required={"timestamp","demand_mw","interchange_mw"}
    if not required.issubset(balance.columns):
        raise ValueError("Missing boundary fields: "+str(sorted(required-set(balance.columns))))
    b=balance.copy()
    b["timestamp"]=pd.to_datetime(b["timestamp"],utc=True,errors="raise")
    for key in ("demand_mw","interchange_mw"):
        b[key]=pd.to_numeric(b[key],errors="raise")
    if b[["timestamp","demand_mw","interchange_mw"]].isna().any().any():
        raise ValueError("Missing boundary data")
    if not np.isfinite(b[["demand_mw","interchange_mw"]].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite boundary data")
    if (b["demand_mw"]<0).any():
        raise ValueError("Negative demand")
    expected=pd.date_range(f"{year}-{month:02d}-01",
        periods=calendar.monthrange(year,month)[1]*24,freq="h",tz="UTC")
    if len(b)!=len(expected) or b["timestamp"].duplicated().any():
        raise ValueError("Incomplete or duplicate UTC hours")
    actual=pd.DatetimeIndex(b["timestamp"].sort_values())
    if not actual.equals(expected):
        raise ValueError("Incomplete UTC month, or wrong UTC timestamp")
    b=b.set_index("timestamp").reindex(expected)
    b["observed_import_mw"]=(-b["interchange_mw"]).clip(lower=0)
    b["observed_export_mw"]=b["interchange_mw"].clip(lower=0)
    if not np.allclose(b["observed_export_mw"]-b["observed_import_mw"],
                       b["interchange_mw"],atol=1e-10,rtol=0):
        raise ValueError("Signed interchange decomposition failed")
    return b
