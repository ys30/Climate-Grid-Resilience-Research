"""Descriptive observed-demand exposure by weather-screening condition.

No causal claims or outage inference: contemporaneous demand may reflect many
drivers, and wind availability here is a model proxy derived from ERA5 speed.
"""
import argparse
from pathlib import Path
import pandas as pd

def summarize(path,output,heat_c=35,low_wind_cf=.2):
    x=pd.read_csv(path)
    need={"timestamp","ba","demand_mw","temperature_c","wind_availability"}
    if not need.issubset(x):raise ValueError("Missing matched hourly data fields")
    if x.empty or x[list(need)].isna().any().any():raise ValueError("Incomplete matched input")
    if x.duplicated(["timestamp","ba"]).any():raise ValueError("Duplicate BA-hours")
    x["demand_mw"]=pd.to_numeric(x.demand_mw,errors="raise")
    x["temperature_c"]=pd.to_numeric(x.temperature_c,errors="raise")
    x["wind_availability"]=pd.to_numeric(x.wind_availability,errors="raise")
    if x[["demand_mw","temperature_c","wind_availability"]].isna().any().any():raise ValueError("Invalid numeric input")
    if (x.demand_mw<=0).any() or not x.wind_availability.between(0,1).all():raise ValueError("Invalid values")
    x["heat"]=x.temperature_c.ge(heat_c)
    x["low_wind"]=x.wind_availability.le(low_wind_cf)
    x["compound"]=x.heat & x.low_wind
    rows=[]
    for ba,g in x.groupby("ba"):
        for label,mask in (("all",pd.Series(True,index=g.index)),("heat",g.heat),
                           ("low_wind",g.low_wind),("compound",g.compound),
                           ("neither",~(g.heat|g.low_wind))):
            selection=g.loc[mask]
            rows.append({"ba":ba,"condition":label,"hours":len(selection),
                         "mean_demand_mw":float(selection.demand_mw.mean()) if len(selection) else None,
                         "total_demand_mwh":float(selection.demand_mw.sum())})
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    result=pd.DataFrame(rows)
    result.to_csv(out,index=False)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    print(summarize(a.input,a.output).to_string(index=False))
if __name__=="__main__":main()
