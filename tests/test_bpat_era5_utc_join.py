"""Regression test: equivalent UTC hours in ERA5 and EIA-930 must join."""
import tempfile
from pathlib import Path
import pandas as pd
from grid_resilience.bpat_era5_wind_shape_comparison import compare

with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    ts=pd.date_range("2024-02-01",periods=696,freq="h",tz="UTC")
    proxy=pd.DataFrame({"timestamp":ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "ba":"BPAT","proxy_availability_pu":[0.05+(i%20)*0.01 for i in range(696)]})
    obs=pd.DataFrame({"timestamp":[t.isoformat() for t in ts],
                      "reported_wind_mw":[100+(i%20)*20 for i in range(696)]})
    capacity=pd.DataFrame({"ba":["BPAT"],"technology":["wind"],"nameplate_capacity_mw":[2000.]})
    for name,df in (("proxy.csv",proxy),("wind.csv",obs),("capacity.csv",capacity)):
        df.to_csv(root/name,index=False)
    result=compare(root/"proxy.csv",root/"wind.csv",root/"capacity.csv",root/"out")
    assert result["hours"]==696 and result["pearson_hourly_correlation"]>0.999
    assert (root/"out/bpat_era5_point_vs_reported_wind_hourly.csv").exists()
print("UTC-normalized ERA5/EIA-930 hourly join regression passed")
