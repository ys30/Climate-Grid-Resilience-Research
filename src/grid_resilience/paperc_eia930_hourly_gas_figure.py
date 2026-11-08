"""Publish 4-BA source-native natural-gas 168-hour EIA930 reported generation.

Two nonaligned July study weeks are shown as independent relative-hour
observations: the figure is descriptive, not a controlled 2023/24
climate change effect or modeled generator-available capability.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
YEARS={2023:"2023-07-10T00:00:00Z",2024:"2024-07-01T00:00:00Z"}


def validate(hourly,manifest):
    if not manifest.get("2024_wind_solar_hydro_battery_taxonomy_not_harmonized"):
        raise ValueError("Original source type revision provenance missing")
    if not manifest.get("actual_hourly_generation_is_not_available_capacity_or_EENS"):
        raise ValueError("Missing physical-scope prohibition")
    needed={"year","ba","utc_hour_start","original_fuel_category",
            "reported_fuel_mwh","fuel_value_reported","original_partition"}
    if not needed.issubset(hourly):
        raise ValueError("Missing source native BA-hour original category")
    a=hourly.loc[hourly.original_fuel_category.eq("Natural Gas")].copy()
    a["utc_hour_start"]=pd.to_datetime(a.utc_hour_start,utc=True)
    for year,begin in YEARS.items():
        for ba in BAS:
            part=a[(a.year==year)&(a.ba==ba)].copy()
            if len(part)!=168 or part.utc_hour_start.nunique()!=168:
                raise ValueError("Original natural gas 168 hourly cells incomplete")
            expected=set(pd.date_range(begin,periods=168,freq="h"))
            if set(part.utc_hour_start)!=expected:
                raise ValueError("Original gas UTC hour key range incorrect")
            if part.reported_fuel_mwh.isna().any() or not part.fuel_value_reported.astype(str).str.lower().eq("true").all():
                raise ValueError("Incomplete raw gas source observation")
            if year==2024 and (part.original_partition.eq("Jan_Jun").sum()!=7 or
                               part.original_partition.eq("Jul_Dec").sum()!=161):
                raise ValueError("Raw source year boundary lost")
    if len(a)!=1344:raise ValueError("Missing 8 original week x BA cohorts")
    a["relative_study_hour"]=a.apply(lambda r:int(
        (r.utc_hour_start-pd.Timestamp(YEARS[int(r.year)])).total_seconds()/3600),axis=1)
    a["source_original_gas_not_modeled_capacity"]=True
    return a


def graph(detail,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dest=Path(out);dest.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(2,2,figsize=(10,6.7),sharex=True,layout="constrained")
    for ax,ba in zip(axes.flat,BAS):
        for year in (2023,2024):
            part=detail[(detail.ba.eq(ba))&(detail.year.eq(year))].sort_values("relative_study_hour")
            ax.plot(part.relative_study_hour,part.reported_fuel_mwh,
                    linewidth=1.35,label=f"{year} (different July dates)")
        ax.set_title(ba,loc="left",fontweight="bold")
        ax.set_xlabel("Hours since each cohort's UTC week start")
        ax.set_ylabel("Original EIA-930 reported natural gas (MWh/h)")
        ax.grid(alpha=.2)
        ax.set_axisbelow(True)
    fig.legend(*axes.flat[0].get_legend_handles_labels(),
               loc="outside upper center",ncol=2,frameon=False)
    fig.suptitle("BA-reported hourly natural gas generation — two different 7-day cohorts")
    fig.text(.5,-.015,
        "2023: Jul 10–16; 2024: Jul 1–7 UTC. Curves do not align by calendar date. "
        "Source reported generation is not available plant capacity, physical shortages or EENS.",
        ha="center",fontsize=8,wrap=True)
    for ext in ("png","pdf"):
        fig.savefig(dest/f"fig_paperc_eia930_fourba_original_hourly_natural_gas.{ext}",
                    dpi=220,bbox_inches="tight")
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    for arg in ("source","manifest","output"):p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    detail=validate(pd.read_csv(a.source),json.loads(Path(a.manifest).read_text()))
    dest=Path(a.output);dest.mkdir(parents=True,exist_ok=True)
    detail.to_csv(dest/"paperc_original_hourly_natural_gas_2023_2024_fourba.csv",index=False)
    graph(detail,dest)
    scope={"original_source_hourly_records":len(detail),
           "different_2023_2024_weeks":True,
           "year_2024_7plus161_original_source_hours_preserved":True,
           "generator_level_hourly_capacity_or_EENS_verified":False}
    (dest/"source_gas_hourly_figure_scope.json").write_text(json.dumps(scope,indent=2)+"\n")

if __name__=="__main__":main()
