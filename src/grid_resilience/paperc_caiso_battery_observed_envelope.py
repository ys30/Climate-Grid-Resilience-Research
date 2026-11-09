"""Paper C CAISO battery five-minute observed power envelope (not SOC).

Use only source-audited Today's Outlook 2023/24 signed 5min Total batteries
and stand-alone batteries. The envelope is an empirical *operating-pattern*
screen for CISO, not a certified installed p_nom, usable MWh, availability,
maximum possible duration, minimum dispatch, efficiency, or physical EENS.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

DATES={2023:"2023-07-10T00:00:00Z",2024:"2024-07-01T00:00:00Z"}
SOURCES={"total":"total_batteries_5min_mw",
         "standalone":"standalone_batteries_5min_mw",
         "hybrid":"hybrid_batteries_5min_mw"}
DURATION_STEP_HOURS=5/60
QUANTILES=(.50,.90,.95,.99)


def _runs(mask):
    """Duration (in minutes) of contiguous five-minute signed-power runs."""
    out=[]
    n=0
    for yes in mask:
        if bool(yes):
            n+=1
        elif n:
            out.append(n*5)
            n=0
    if n:
        out.append(n*5)
    return out


def compute(frame, source_scope):
    if not source_scope.get("market_EN_is_preliminary_not_settlement_metering"):
        raise ValueError("Original independent-source audit context absent")
    if not source_scope.get("telemetry_total_batteries_includes_hybrid_scope"):
        raise ValueError("Source includes hybrid reporting differences")
    keys={"year","utc_5min_start",*SOURCES.values(),
          "fuelsource_batteries_5min_mw"}
    if not keys.issubset(frame):
        raise ValueError("Missing original five-minute CAISO power source fields")
    panel=frame[list(keys)].copy()
    panel["utc_5min_start"]=pd.to_datetime(panel.utc_5min_start,utc=True)
    if panel.duplicated(["year","utc_5min_start"]).any():
        raise ValueError("Repeated original telemetry five-minute key")
    if set(panel.year)!={2023,2024}:
        raise ValueError("Missing historical comparison cohort")
    for column in (*SOURCES.values(),"fuelsource_batteries_5min_mw"):
        panel[column]=pd.to_numeric(panel[column],errors="raise")
        if not np.isfinite(panel[column]).all():
            raise ValueError("Missing or nonfinite original source value")
    if not np.allclose(panel.total_batteries_5min_mw,
                       panel.fuelsource_batteries_5min_mw,
                       rtol=0,atol=0):
        # Require source alignment of Today's Outlook total batteries with the
        # independent fuel-category feed, not stand-alone + hybrid equality.
        raise ValueError("Today's Outlook battery and fuelsource historical feeds disagree")
    records=[]
    hourly=[]
    daily=[]
    for year,start in DATES.items():
        a=panel.loc[panel.year.eq(year)].sort_values("utc_5min_start").copy()
        expected=pd.date_range(start,periods=2016,freq="5min")
        if len(a)!=2016 or not a.utc_5min_start.reset_index(drop=True).equals(
            pd.Series(expected,name="utc_5min_start")
        ):
            raise ValueError("Missing, duplicated or shifted original five-minute cohort")
        a["utc_hour_start"]=a.utc_5min_start.dt.floor("h")
        a["utc_date"]=a.utc_5min_start.dt.strftime("%Y-%m-%d")
        for label,column in SOURCES.items():
            vals=a[column].to_numpy()
            charge=np.maximum(-vals,0)
            discharge=np.maximum(vals,0)
            plus=_runs(vals>0)
            minus=_runs(vals<0)
            item={
                "year":year,"series":label,"source_points":len(vals),
                "observed_max_discharge_mw":float(discharge.max()),
                "observed_max_charge_mw":float(charge.max()),
                "observed_positive_interval_count":int((vals>0).sum()),
                "observed_negative_interval_count":int((vals<0).sum()),
                "observed_zero_interval_count":int((vals==0).sum()),
                "observed_descriptive_positive_mwh":float(discharge.sum()*DURATION_STEP_HOURS),
                "observed_descriptive_negative_charge_mwh":float(charge.sum()*DURATION_STEP_HOURS),
                "longest_consecutive_positive_minutes":max(plus,default=0),
                "longest_consecutive_negative_minutes":max(minus,default=0),
                "number_positive_runs":len(plus),
                "number_negative_runs":len(minus),
                "matched_battery_soc_mwh_inferred":False,
                "certified_storage_power_rating_mw_inferred":False,
                "hypothetical_reliability_model_calibrated":False,
            }
            for q in QUANTILES:
                pct=str(int(q*100))
                item["discharge_positive_only_p"+pct+"_mw"]=(
                    float(np.quantile(vals[vals>0],q)) if (vals>0).any() else None)
                item["charge_positive_magnitude_only_p"+pct+"_mw"]=(
                    float(np.quantile(-vals[vals<0],q)) if (vals<0).any() else None)
            records.append(item)
            sub=a[["utc_hour_start","utc_date",column]].copy()
            hr=sub.groupby("utc_hour_start",as_index=False).agg(
                numeric_five_minute_points=(column,"count"),
                mean_signed_mw=(column,"mean"),
                max_observed_discharge_mw=(column,"max"),
                min_observed_signed_mw=(column,"min"))
            if len(hr)!=168 or not hr.numeric_five_minute_points.eq(12).all():
                raise ValueError("An original 12-point UTC hour was not complete")
            for r in hr.itertuples():
                hourly.append({
                    "year":year,"series":label,"utc_hour_start":r.utc_hour_start.isoformat(),
                    "n_source_5min_points":int(r.numeric_five_minute_points),
                    "mean_signed_observed_mw":float(r.mean_signed_mw),
                    "max_observed_discharge_mw":max(0.,float(r.max_observed_discharge_mw)),
                    "max_observed_charge_mw":max(0.,-float(r.min_observed_signed_mw)),
                    "operational_observation_not_storageunit_max_hours":True})
            for utc_date,group in sub.groupby("utc_date"):
                signed=group[column].to_numpy()
                daily.append({"year":year,"series":label,"utc_date":utc_date,
                    "observed_five_minute_points":len(signed),
                    "observed_positive_mwh":float(np.maximum(signed,0).sum()/12),
                    "observed_negative_charge_mwh":float(np.maximum(-signed,0).sum()/12),
                    "max_observed_discharge_mw":max(0.,float(signed.max())),
                    "max_observed_charge_mw":max(0.,-float(signed.min())),
                    "not_measured_battery_soc_or_firm_capacity":True})
    report=pd.DataFrame(records)
    hour=pd.DataFrame(hourly)
    day=pd.DataFrame(daily)
    meta={
        "study_years":[2023,2024],"source_ba":"CISO (CAISO outlook)",
        "hours_per_year":168,"five_minute_records_per_year":2016,
        "empirical_power_envelope_is_observed_behavior_not_technical_rating":True,
        "five_minute_positive_negative_signed_mwh_is_descriptive_not_SOC":True,
        "observed_run_length_is_not_storage_duration_capability":True,
        "hybrid_and_standalone_series_not_proven_additive":True,
        "no_storage_energy_mwh_initial_soc_or_efficiency_inferred":True,
        "no_pypsa_historical_ens_or_reliability_calibrated":True,
    }
    return report,hour,day,meta


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--source-manifest",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    report,hours,days,meta=compute(
        pd.read_csv(args.source),
        json.loads(Path(args.source_manifest).read_text()))
    out=Path(args.output)
    out.mkdir(parents=True,exist_ok=True)
    report.to_csv(out/"caiso_battery_observed_5min_power_envelope_summary.csv",index=False)
    hours.to_csv(out/"caiso_battery_observed_hourly_power_envelope.csv",index=False)
    days.to_csv(out/"caiso_battery_observed_utc_day_power_envelope.csv",index=False)
    (out/"caiso_battery_observation_scope_and_reliability_gate.json").write_text(
        json.dumps(meta,indent=2)+"\n")
    print("SOURCE VERIFIED OBSERVED POWER ENVELOPES",report.to_string(index=False))
    print("UTC DAY TELEMETRY HOURS",days.groupby(["year","series"]).observed_five_minute_points.sum().to_string())


if __name__=="__main__":
    main()
