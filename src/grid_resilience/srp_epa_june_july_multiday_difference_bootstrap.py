"""Multi-day moving-block sensitivity of June–July common-cell source slopes.

Each selected local-date block contains consecutive *original* MST calendar
dates, with no wrap at the month boundary. The original supported
2°C-500MW-4h joint-cell sample is frozen before sampling. June and July are
drawn independently per source unit. Percentile spans are only descriptive
sensitivity ranges, not validated statistical confidence intervals.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from grid_resilience.srp_epa_eia930_day_block_bootstrap import partial_temperature_coef
from grid_resilience.srp_epa_eia930_multiday_block_sensitivity import moving_day_indices
from grid_resilience.srp_epa_june_july_common_support_bootstrap import selected_source_month
from grid_resilience.srp_epa_june_july_overlap_models import BINS, validate
from grid_resilience.srp_epa_june_july_2024_common_support import common_support

WIDTHS=(2,3,5)


def within_month_blocks(frame, draws, width, rng):
    """Draw consecutive local dates, while honoring excluded source-hour gaps."""
    if width not in WIDTHS:
        raise ValueError("Unapproved moving-block length")
    dates=frame.local_date.unique()
    if len(dates)<10:
        raise ValueError("Insufficient observed calendar-date support")
    positions=[np.flatnonzero(frame.local_date.to_numpy()==d) for d in dates]
    if any(not len(q) for q in positions):
        raise ValueError("Empty observed date block")
    return [moving_day_indices(positions,width,rng)[:2] for _ in range(draws)]


def audit(june,july,baseline,*,replicates=120,seed=20261105,widths=WIDTHS):
    if replicates<50:
        raise ValueError("Require at least 50 paired moving-block draws")
    if any(w not in WIDTHS for w in widths) or not widths:
        raise ValueError("Unsupported prespecified block lengths")
    if len(set(widths))!=len(widths):
        raise ValueError("Duplicate block widths")
    a,b=validate(june,"June"),validate(july,"July")
    support,_=common_support(a,b)
    eligible=support.loc[support.operating_gross_screen_pass]
    if len(eligible)!=6:
        raise ValueError("Original six positive-operation source units changed")
    fields={"facility_id","epa_unit_id","month",
            "gross_temperature_mw_per_c","gross_model_status"}
    if not fields.issubset(baseline) or len(baseline)!=20:
        raise ValueError("Original common-cell regression baseline required")
    truth=baseline.copy()
    truth["facility_id"]=truth.facility_id.astype("string").str.strip()
    truth["epa_unit_id"]=truth.epa_unit_id.astype("string").str.strip()
    if truth.duplicated(["facility_id","epa_unit_id","month"]).any():
        raise ValueError("Duplicate baseline source unit/month")
    results=[]
    for s in eligible.itertuples(index=False):
        site,unit=s.facility_id,s.epa_unit_id
        sources={
            "June":a.loc[a.facility_id.eq(site)&a.unit_id.eq(unit)],
            "July":b.loc[b.facility_id.eq(site)&b.unit_id.eq(unit)]}
        common=set(sources["June"][BINS].itertuples(index=False,name=None)) & set(
            sources["July"][BINS].itertuples(index=False,name=None))
        panels={}
        for month,original in sources.items():
            g,outcome=selected_source_month(original,common)
            if len(g)!=(s.june_joint_hours if month=="June" else s.july_joint_hours):
                raise ValueError("Changed original joint-source observations")
            point=partial_temperature_coef(g,outcome,g.local_date.to_numpy())
            control=truth.loc[truth.facility_id.eq(site)&truth.epa_unit_id.eq(unit)&
                              truth.month.eq(month)]
            if len(control)!=1 or control.iloc[0].gross_model_status!="descriptive_ols_only":
                raise ValueError("Missing admitted original source OLS coefficient")
            if point is None or not np.isclose(
                    point,float(control.iloc[0].gross_temperature_mw_per_c),
                    rtol=1e-6,atol=1e-6):
                raise ValueError("Within-date FWL differs from prior full source OLS")
            panels[month]=(g,outcome,point)
        original_delta=panels["July"][2]-panels["June"][2]
        for width in widths:
            # Fixed reproducible source-unit+width seed; do not draw within hours.
            rng=np.random.default_rng(seed+int(site)+sum(map(ord,unit))+width*100000)
            pair_draws={}
            for month in ("June","July"):
                g,_,_=panels[month]
                pair_draws[month]=within_month_blocks(g,replicates,width,rng)
            accepted=[]
            for iteration in range(replicates):
                coefficients={}
                for month in ("June","July"):
                    g,response,_=panels[month]
                    indices,day_ids=pair_draws[month][iteration]
                    chosen=g.iloc[indices].reset_index(drop=True)
                    estimate=partial_temperature_coef(chosen,response[indices],day_ids)
                    if estimate is None or not np.isfinite(estimate):
                        break
                    coefficients[month]=estimate
                if len(coefficients)==2:
                    accepted.append(coefficients["July"]-coefficients["June"])
            n_accepted=len(accepted)
            admissible=n_accepted>=int(np.ceil(.90*replicates))
            low,high=(np.percentile(accepted,[2.5,97.5])
                      if admissible else (np.nan,np.nan))
            results.append({
                "facility_id":site,"epa_unit_id":unit,
                "block_width_consecutive_local_dates":width,
                "june_gross_source_valid_rows":int(np.isfinite(panels["June"][1]).sum()),
                "july_gross_source_valid_rows":int(np.isfinite(panels["July"][1]).sum()),
                "june_original_temperature_coefficient_mw_per_c":panels["June"][2],
                "july_original_temperature_coefficient_mw_per_c":panels["July"][2],
                "july_minus_june_original_coefficient_mw_per_c":float(original_delta),
                "paired_moving_block_draws_requested":replicates,
                "paired_moving_block_draws_admitted":n_accepted,
                "descriptive_2_5_percentile_mw_per_c":float(low),
                "descriptive_97_5_percentile_mw_per_c":float(high),
                "exploratory_percentile_reportable":bool(admissible),
                "exploratory_span_excludes_zero":bool(admissible and low*high>0)})
    out=pd.DataFrame(results)
    if len(out)!=6*len(widths) or set(out.block_width_consecutive_local_dates)!=set(widths):
        raise ValueError("Unexpected cohort or block-width output")
    summary=[]
    for (site,unit),group in out.groupby(["facility_id","epa_unit_id"],sort=True):
        publishable=group.loc[group.exploratory_percentile_reportable]
        all_pass=bool(len(publishable)==len(widths))
        all_above=bool(all_pass and publishable.descriptive_2_5_percentile_mw_per_c.gt(0).all())
        all_below=bool(all_pass and publishable.descriptive_97_5_percentile_mw_per_c.lt(0).all())
        summary.append({
            "facility_id":site,"epa_unit_id":unit,
            "original_july_minus_june_mw_per_c":group.iloc[0].july_minus_june_original_coefficient_mw_per_c,
            "block_widths_requested":len(widths),
            "block_widths_reportable":len(publishable),
            "all_block_widths_reportable":all_pass,
            "direction_stable_across_all_widths_descriptively":bool(all_above or all_below),
            "blocked_or_crosses_zero_in_at_least_one_width":not (all_above or all_below)})
    manifest={
       "real_source_june_july_join_run":42092282072,
       "original_source_common_cell_ols_run":42093112865,
       "one_day_source_bootstrap_run":42099599060,
       "source_months":["2024-06","2024-07"],
       "source_eligible_units":6,"block_widths_in_local_dates":list(widths),
       "paired_draws_per_width":replicates,"random_seed":seed,
       "source_temperature_bin_c":2,"srp_demand_bin_mw":500,"local_hour_bin_h":4,
       "original_joint_cells_fixed_before_resampling":True,
       "noncircular_moving_date_blocks_no_month_wrap":True,
       "month_blocks_independent_no_hourly_iid_resampling":True,
       "repeated_day_blocks_separately_relabel_date_fixed_effects":True,
       "original_point_coefficient_matches_source_ols":True,
       "resampling_admission_fraction_minimum":0.9,
       "descriptive_percentiles_not_validated_confidence_intervals":True,
       "longer_than_five_day_heatwave_dependence_unresolved":True,
       "no_independent_colocated_unit_weather_assumption":True,
       "gross_source_outcome_selected_on_positive_operation":True,
       "causal_thermal_derating_or_eia_net_mw_estimated":False,
       "observed_eens_or_forced_outages_identified":False,
       "independent_out_of_month_prediction_test_performed":False}
    return out,pd.DataFrame(summary),manifest


def main():
    p=argparse.ArgumentParser()
    for key in ("june-panel","july-panel","baseline","output"):
        p.add_argument("--"+key,required=True)
    p.add_argument("--replicates",type=int,default=120)
    p.add_argument("--seed",type=int,default=20261105)
    args=p.parse_args()
    result,summary,manifest=audit(
        pd.read_csv(args.june_panel,dtype={"facility_id":"string","unit_id":"string"}),
        pd.read_csv(args.july_panel,dtype={"facility_id":"string","unit_id":"string"}),
        pd.read_csv(args.baseline,dtype={"facility_id":"string","epa_unit_id":"string"}),
        replicates=args.replicates,seed=args.seed)
    root=Path(args.output);root.mkdir(parents=True,exist_ok=True)
    result.to_csv(root/"epa_june_july_common_support_multiday_coef_difference.csv",index=False)
    summary.to_csv(root/"epa_june_july_multiday_width_stability_summary.csv",index=False)
    (root/"epa_june_july_multiday_bootstrap_scope_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print("SOURCE_2_3_5_DAY_DIFFERENCE")
    print(result.to_string(index=False))
    print("SOURCE_BLOCK_WIDTH_STABILITY")
    print(summary.to_string(index=False))


if __name__=="__main__":
    main()
