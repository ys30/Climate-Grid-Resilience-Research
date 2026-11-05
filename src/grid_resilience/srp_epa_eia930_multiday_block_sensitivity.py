"""Exploratory moving-date-block length sensitivity for EPA/EIA930 source models.

Resample contiguous 2, 3 or 5 Arizona MST dates, not individual hourly rows.
Each selected date occurrence receives its own fixed-effect label; source hours
are never invented. Percentile ranges are *sensitivity diagnostics*, not
validated inferential confidence intervals or physical heat-derating estimates.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from grid_resilience.srp_epa_eia930_day_block_bootstrap import partial_temperature_coef
from grid_resilience.srp_epa_era5_eia930_demand_context import summarize as admit_sources

BLOCKS = (2, 3, 5)


def moving_day_indices(day_positions, width, rng):
    """Sample contiguous observed-day blocks without cross-month wraparound."""
    nday = len(day_positions)
    if not 1 <= width <= nday:
        raise ValueError("Invalid day-block width")
    selected = []
    while len(selected) < nday:
        start = int(rng.integers(0, nday-width+1))
        selected.extend(range(start, start+width))
    selected = selected[:nday]
    indices = np.concatenate([day_positions[i] for i in selected])
    group = np.concatenate([
        np.full(len(day_positions[i]), occurrence, dtype=int)
        for occurrence, i in enumerate(selected)
    ])
    return indices, group, selected


def analyze_unit(unit, *, reps=120, seed=20261105, widths=BLOCKS):
    if reps < 50:
        raise ValueError("At least 50 draws required")
    g = unit.sort_values("timestamp_utc").reset_index(drop=True).copy()
    local = g.timestamp_utc.dt.tz_convert("Etc/GMT+7")
    g["local_date"] = local.dt.strftime("%Y-%m-%d")
    g["local_hour"] = local.dt.hour
    dates = g.local_date.unique()
    if len(dates) != 31 or len(g) != 737:
        raise ValueError("Expected 31 exact MST dates and 737 source-matched hours")
    positions = [np.flatnonzero(g.local_date.to_numpy()==d) for d in dates]
    if [len(x) for x in positions] != [24]*30+[17]:
        raise ValueError("Unexpected 737 hour July UTC intersection shape")
    outcomes = {
        "reported_operation_lpm":np.where(
            g.operating_time.notna(), (g.operating_time>0).astype(float), np.nan),
        "gross_load_given_positive_operation_mw":np.where(
            g.operating_time.gt(0), g.gross_load_mw, np.nan).astype(float)
    }
    points = {key:partial_temperature_coef(g,y,g.local_date.to_numpy())
              for key,y in outcomes.items()}
    rows=[]
    for width in widths:
        if width not in BLOCKS:
            raise ValueError("Unsupported contiguous block width")
        rng = np.random.default_rng(seed+width)
        # Same selected contiguous dates for both outcomes within a unit.
        draws=[moving_day_indices(positions,width,rng) for _ in range(reps)]
        for outcome,y in outcomes.items():
            sample_n=int(np.isfinite(y).sum())
            admitted=[]
            if points[outcome] is not None:
                for indices,groups,_ in draws:
                    selected=g.iloc[indices].reset_index(drop=True)
                    estimate=partial_temperature_coef(selected,y[indices],groups)
                    if estimate is not None and np.isfinite(estimate):
                        admitted.append(estimate)
            enough=len(admitted)>=int(np.ceil(0.90*reps))
            low,high=(np.percentile(admitted,[2.5,97.5])
                      if enough else (np.nan,np.nan))
            rows.append({
                "outcome":outcome,"block_width_local_days":width,
                "source_valid_outcome_rows":sample_n,
                "point_estimate_per_c":points[outcome],
                "replicates_requested":reps,"replicates_admitted":len(admitted),
                "sensitivity_low_2_5":float(low),
                "sensitivity_high_97_5":float(high),
                "percentile_reportable":bool(enough),
                "excludes_zero_in_this_sensitivity":bool(enough and low*high>0),
            })
    return pd.DataFrame(rows)


def audit(epa,eia,*,reps=120,seed=20261105):
    admit_sources(epa,eia)
    x=epa.copy()
    x["facility_id"]=x.facility_id.astype("string").str.strip()
    x["unit_id"]=x.unit_id.astype("string").str.strip()
    x["timestamp_utc"]=pd.to_datetime(x.timestamp_utc,utc=True)
    for col in ("temperature_2m_c","operating_time","gross_load_mw"):
        x[col]=pd.to_numeric(x[col],errors="coerce")
    if not x.operating_time.dropna().between(0,1).all():
        raise ValueError("EPA operating fraction out of bounds")
    e=eia.loc[eia["Balancing Authority"].astype("string").str.strip().eq("SRP")].copy()
    e["timestamp_utc"]=pd.to_datetime(e["UTC Time at End of Hour"],
        format="%m/%d/%Y %I:%M:%S %p",utc=True)-pd.Timedelta(hours=1)
    e["srp_demand_mw"]=pd.to_numeric(e["Demand (MW)"],errors="raise")
    joined=x.merge(e[["timestamp_utc","srp_demand_mw"]],
       on="timestamp_utc",how="inner",validate="many_to_one")
    if len(joined)!=7370:
        raise ValueError("Unexpected total source-matched EPA unit-hours")
    parts=[]
    for (plant,unit),g in joined.groupby(["facility_id","unit_id"],sort=True):
        result=analyze_unit(g,reps=reps,seed=seed)
        result.insert(0,"epa_unit_id",str(unit))
        result.insert(0,"facility_id",str(plant))
        parts.append(result)
    out=pd.concat(parts,ignore_index=True)
    manifest={
        "original_source_pinned":"EPA ERA5 local July 744h; official EIA930 UTC July 744h",
        "source_hours_per_unit_in_intersection":737,
        "source_units":10,"local_dates":31,
        "day_block_widths":list(BLOCKS),"replicates_per_width":reps,
        "resampling":"noncircular moving blocks of consecutive MST dates, truncate to 31 source-day occurrences",
        "fixed_effects":"MST hour and independently relabeled MST date per sampled occurrence",
        "other_controls":"actual SRP BA EIA930 demand GW",
        "weather_data_shared_within_site":True,
        "independent_year_validation":False,
        "percentiles_are_exploratory_not_validated_confidence_intervals":True,
        "long_heatwave_dependence_may_exceed_5_days":True,
        "conditional_gross_load_dispatch_selected":True,
        "generator_net_mw_or_thermal_derating_causally_identified":False,
        "pypsa_eens_or_outage_calibration":False,
        "epa_to_eia_generator_physical_identity_admitted":False,
        "august_demand_source_filled":False,
    }
    return out,manifest


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--epa-era5-panel",required=True)
    parser.add_argument("--eia930-july",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--replicates",type=int,default=120)
    parser.add_argument("--seed",type=int,default=20261105)
    a=parser.parse_args()
    result,manifest=audit(
        pd.read_csv(a.epa_era5_panel,dtype={"facility_id":"string","unit_id":"string"}),
        pd.read_csv(a.eia930_july,dtype="string"),
        reps=a.replicates,seed=a.seed)
    folder=Path(a.output)
    folder.mkdir(parents=True,exist_ok=True)
    result.to_csv(folder/"epa_eia930_multiday_block_sensitivity.csv",index=False)
    (folder/"epa_eia930_multiday_block_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print(result.to_string(index=False))


if __name__=="__main__":
    main()
