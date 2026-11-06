"""Observed official USACE/USBR/USGS July 2024 Grand Coulee paper appendix figures.

No output shown is a calibrated hydro-head, PS SOC or historical outage.
Two separate figure files; never plot physical site levels as one
electrical hydraulic head without station datum and time reconciliation.
"""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot(data,output):
    x=data.copy()
    x["date"]=pd.to_datetime(x.date)
    x=x.sort_values("date")
    assert len(x)==31 and x.date.nunique()==31
    need=["usace_banks_lake_pumping_electricity_mwh",
          "usace_banks_lake_reported_elev_ft",
          "elevation_ft",
          "lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29"]
    assert all(c in x for c in need)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)

    fig,ax=plt.subplots(figsize=(10.7,4.4),layout="constrained")
    ax.bar(x.date,x.usace_banks_lake_pumping_electricity_mwh,width=.85)
    ax.axvline(pd.Timestamp("2024-07-28 12:00"),linestyle="--",linewidth=1)
    ax.set_title("Grand Coulee / Banks Lake: reported daily pumping electricity, July 2024")
    ax.set_ylabel("Project-wide pumping electricity (MWh/day)")
    ax.set_xlabel("July 2024")
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.tick_params(axis="x",rotation=25)
    ax.grid(axis="y",alpha=.25)
    ax.text(.01,.98,"July 1–28: original PyPSA calendar window",transform=ax.transAxes,
            ha="left",va="top",fontsize=9)
    fig.text(.5,0.01,"USACE entire Banks Lake pumping installation; NOT verified PG7–PG12-only PS charging.",
        ha="center",fontsize=8)
    fig.savefig(out/"fig_usace_grand_coulee_july2024_actual_project_pump_mwh.png",dpi=185,bbox_inches="tight")
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(10.7,4.4),layout="constrained")
    ax.plot(x.date,x.usace_banks_lake_reported_elev_ft-x.usace_banks_lake_reported_elev_ft.iloc[0],
            marker="o",markersize=3,label="Banks Lake, USACE daily record")
    ax.plot(x.date,x.lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29-
            x.lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29.iloc[0],
            marker="s",markersize=3,label="Roosevelt Lake, USGS 32400 (24:00)")
    ax.axhline(0,linestyle=":",linewidth=1)
    ax.axvline(pd.Timestamp("2024-07-28 12:00"),linestyle="--",linewidth=1)
    ax.set_title("Observed within-reservoir elevation changes from July 1, 2024")
    ax.set_ylabel("Change from each reservoir's July 1 observed value (ft)")
    ax.set_xlabel("July 2024")
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.tick_params(axis="x",rotation=25)
    ax.legend(fontsize=8)
    ax.grid(alpha=.25)
    fig.text(.5,0.01,
         "Different source observation times; not an effective hydraulic head or stored energy MWh.",
         ha="center",fontsize=8)
    fig.savefig(out/"fig_grand_coulee_july2024_banks_roosevelt_observed_stage_changes.png",
                dpi=185,bbox_inches="tight")
    plt.close(fig)
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--joined-source",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    plot(pd.read_csv(a.joined_source),a.output)
