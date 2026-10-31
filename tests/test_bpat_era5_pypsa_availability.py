"""Check 29-site proxy only changes BPAT wind and normalizes UTC."""
from pathlib import Path
import tempfile
import pandas as pd
from grid_resilience.bpat_era5_pypsa_availability import inject
with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    t=pd.date_range("2024-02-01",periods=696,freq="h",tz="UTC")
    base=pd.DataFrame([{"timestamp":ts.isoformat(),"ba":ba,"technology":tech,"availability_pu":0.8}
      for ts in t for ba,tech in [("BPAT","wind"),("BPAT","solar"),("CISO","wind")]])
    weather=pd.DataFrame({"timestamp":t.strftime("%Y-%m-%dT%H:%M:%SZ"),
      "capacity_weighted_proxy_availability_pu":[0.2]*696})
    base.to_csv(root/"base.csv",index=False);weather.to_csv(root/"weather.csv",index=False)
    result=inject(root/"base.csv",root/"weather.csv",root/"out")
    assert result["replaced_bpat_wind_hours"]==696
    x=pd.read_csv(root/"out/era5_29site_wind_availability.csv")
    assert x.loc[(x.ba=="BPAT")&(x.technology=="wind"),"availability_pu"].eq(0.2).all()
    assert x.loc[~((x.ba=="BPAT")&(x.technology=="wind")),"availability_pu"].eq(0.8).all()
print("ERA5-to-PyPSA availability UTC and unchanged-input test passed")
