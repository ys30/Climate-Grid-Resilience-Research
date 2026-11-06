"""A source-complete paired daily 2024 July Banks Lake and Roosevelt lake observation panel.

Matching *calendar dates* is not matching measurement instants. Banks
daily-instant 19:00 UTC and USGS 32400 observation at 2400 are distinct
daily observation definitions. Do not subtract site levels as physical
net hydraulic head without common vertical datum and pump intake survey.
Within-site changes relative to July 1 are descriptive only.
"""
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np

def pair(banks,roosevelt,banks_scope,roosevelt_scope):
    a=banks.copy();b=roosevelt.copy()
    need_a={"date","elevation_ft","source_record_timestamp"}
    need_b={"date","lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29"}
    if not need_a.issubset(a) or not need_b.issubset(b):
        raise ValueError("Original Banks / Roosevelt data source columns absent")
    if banks_scope["dataset_129466_Banks_Lake_observed_July_daily_records"]!=31 or (
        roosevelt_scope["USGS_12436000_2024_07_daily_2400_observed_observations"]!=31) or (
        roosevelt_scope["USGS_statistic_code"]!="32400"):
        raise ValueError("Source original dates or actual USGS 2400 statistic not admitted")
    a["date"]=pd.to_datetime(a.date,errors="raise")
    b["date"]=pd.to_datetime(b.date,errors="raise")
    expected=pd.date_range("2024-07-01",periods=31,freq="D")
    for label,d in (("banks",a),("roosevelt",b)):
        if len(d)!=31 or d.date.duplicated().any() or not pd.DatetimeIndex(d.date.sort_values()).equals(expected):
            raise ValueError(f"Missing or duplicate original {label} observed dates")
    a["banks_elevation_daily_instant_ft"]=pd.to_numeric(a.elevation_ft,errors="coerce")
    b["roosevelt_elevation_at_2400_ft_ngvd29"]=pd.to_numeric(
        b.lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29,errors="coerce")
    if not np.isfinite(a.banks_elevation_daily_instant_ft.to_numpy(float)).all() or not np.isfinite(
        b.roosevelt_elevation_at_2400_ft_ngvd29.to_numpy(float)).all():
        raise ValueError("Missing official observed daily levels, not filled")
    paired=a[["date","banks_elevation_daily_instant_ft"]].merge(
        b[["date","roosevelt_elevation_at_2400_ft_ngvd29"]],
        on="date",how="inner",validate="one_to_one").sort_values("date")
    paired["banks_change_from_july1_ft"]=paired.banks_elevation_daily_instant_ft-paired.banks_elevation_daily_instant_ft.iloc[0]
    paired["roosevelt_change_from_july1_ft"]=paired.roosevelt_elevation_at_2400_ft_ngvd29-paired.roosevelt_elevation_at_2400_ft_ngvd29.iloc[0]
    paired["within_original_2024_july_28day_pypsa_window"]=paired.date.le(pd.Timestamp("2024-07-28"))
    m={
      "original_banks_lake_RISE_item_id":129466,
      "original_roosevelt_USGS_site_id":"12436000",
      "paired_july_observed_calendar_dates":len(paired),
      "original_pypsa_july_model_dates":int(paired.within_original_2024_july_28day_pypsa_window.sum()),
      "extra_july_days_outside_28day_model":3,
      "upper_daily_source_time":"USBR Banks daily instantaneous 19:00 UTC (source observed)",
      "lower_daily_source_time":"USGS 32400 observation at 2400",
      "daily_observations_synchronous":False,
      "common_vertical_datum_and_pump_head_verified":False,
      "inter_reservoir_daily_actual_head_computed":False,
      "observed_reservoir_stage_to_volume_curve_available":False,
      "irrigation_inflow_and_pumping_balances_observed":False,
      "real_PS_usable_energy_MWh_estimated":False,
      "pypsa_ps_4h_80percent_measured":False,
      "first_28day_observed_stage_trace_not_hourly_generation":True}
    return paired,m

def main():
    parser=argparse.ArgumentParser()
    for n in ("banks-daily","roosevelt-daily","banks-scope","roosevelt-scope","output"):
        parser.add_argument("--"+n,required=True)
    a=parser.parse_args()
    p,m=pair(pd.read_csv(a.banks_daily),pd.read_csv(a.roosevelt_daily),
          json.loads(Path(a.banks_scope).read_text()),
          json.loads(Path(a.roosevelt_scope).read_text()))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    p.to_csv(out/"july2024_banks_roosevelt_31day_observed_elevation_levels_and_within_site_changes.csv",index=False)
    (out/"july2024_dual_reservoir_observations_scope_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print("SOURCE-VERIFIED 2024 JULY BANKS/ROOSEVELT DAILY STAGE PAIRS, NOT NET PUMP HEAD")
    print(p.to_string(index=False))
    print(json.dumps(m,indent=2))
if __name__=="__main__":main()
