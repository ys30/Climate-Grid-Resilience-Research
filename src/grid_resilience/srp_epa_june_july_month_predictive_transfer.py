"""June<->July 2024 source-unit out-of-month predictive transfer.

Train linear models on ONE month and evaluate on the other, only inside the
previously observed occupied temperature-demand-hour common-cell universe.
No date fixed effects in forecasting: held-out month's date indicators are
not learnable from training dates. Demand and same-hour ERA5 are treated as
observed contemporaneous covariates (not ex-ante forecasts).
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from grid_resilience.srp_epa_june_july_overlap_models import BINS,validate
from grid_resilience.srp_epa_june_july_2024_common_support import common_support

def matrix(frame, with_temp):
    h=frame.timestamp_utc.dt.tz_convert("Etc/GMT+7").dt.hour.to_numpy()
    demand=frame.srp_ba_demand_mw.to_numpy(float)/1000.
    columns=[np.ones(len(frame)),demand]
    columns.extend((h==i).astype(float) for i in range(1,24))
    if with_temp:
        columns.append(frame.temperature_2m_c.to_numpy(float))
    return np.column_stack(columns)


def score(train,test,outcome,with_temp):
    if outcome=="running":
        yt=np.where(train.operating_time.notna(),
                    (train.operating_time>0).astype(float),np.nan)
        yv=np.where(test.operating_time.notna(),
                    (test.operating_time>0).astype(float),np.nan)
    else:
        yt=np.where(train.operating_time.gt(0),train.gross_load_mw,np.nan)
        yv=np.where(test.operating_time.gt(0),test.gross_load_mw,np.nan)
    mt=np.isfinite(yt)
    mv=np.isfinite(yv)
    if mt.sum()<80 or mv.sum()<80:
        return {"status":"insufficient_operating_source_records",
                "train_n":int(mt.sum()),"test_n":int(mv.sum()),
                "mae":np.nan,"rmse":np.nan,"brier":np.nan}
    train_y=yt[mt];test_y=yv[mv]
    if outcome=="running" and len(np.unique(train_y))<2:
        return {"status":"constant_training_operating_outcome",
                "train_n":int(mt.sum()),"test_n":int(mv.sum()),
                "mae":np.nan,"rmse":np.nan,"brier":np.nan}
    x=matrix(train,with_temp)[mt]
    xt=matrix(test,with_temp)[mv]
    if np.linalg.matrix_rank(x)!=x.shape[1]:
        return {"status":"unidentified_design",
                "train_n":int(mt.sum()),"test_n":int(mv.sum()),
                "mae":np.nan,"rmse":np.nan,"brier":np.nan}
    beta=np.linalg.lstsq(x,train_y,rcond=None)[0]
    predictions=xt@beta
    if outcome=="running":
        predictions=np.clip(predictions,0,1)
    errors=predictions-test_y
    return {"status":"out_of_month_observed_covariate_evaluation",
            "train_n":int(mt.sum()),"test_n":int(mv.sum()),
            "mae":float(np.mean(np.abs(errors))),
            "rmse":float(np.sqrt(np.mean(errors**2))),
            "brier":float(np.mean(errors**2)) if outcome=="running" else np.nan}


def audit(june,july):
    a,b=validate(june,"June"),validate(july,"July")
    support,_=common_support(a,b)
    if len(support)!=10 or support.operating_gross_screen_pass.sum()!=6:
        raise ValueError("Verified 10-unit / six eligible-gross source gate changed")
    rows=[]
    for s in support.itertuples(index=False):
        p,unit=s.facility_id,s.epa_unit_id
        one=a.loc[a.facility_id.eq(p)&a.unit_id.eq(unit)]
        two=b.loc[b.facility_id.eq(p)&b.unit_id.eq(unit)]
        cells=set(one[BINS].itertuples(index=False,name=None))&set(
            two[BINS].itertuples(index=False,name=None))
        m1=one[BINS].apply(tuple,axis=1).isin(cells)
        m2=two[BINS].apply(tuple,axis=1).isin(cells)
        first=one.loc[m1].sort_values("timestamp_utc").reset_index(drop=True)
        second=two.loc[m2].sort_values("timestamp_utc").reset_index(drop=True)
        if len(first)!=s.june_joint_hours or len(second)!=s.july_joint_hours:
            raise ValueError("Frozen joint-cell source scope changed")
        for direction,train,test in (
            ("June_to_July",first,second),("July_to_June",second,first)):
            for outcome in ("running","conditional_gross_mw"):
                if outcome=="conditional_gross_mw" and not s.operating_gross_screen_pass:
                    continue
                base=score(train,test,outcome,False)
                augmented=score(train,test,outcome,True)
                if base["train_n"]!=augmented["train_n"] or base["test_n"]!=augmented["test_n"]:
                    raise ValueError("Models evaluated on unequal held-out target observations")
                eligible=base["status"]=="out_of_month_observed_covariate_evaluation" and augmented["status"]==base["status"]
                rows.append({
                    "facility_id":p,"epa_unit_id":unit,
                    "training_to_validation":direction,"outcome":outcome,
                    "train_n":base["train_n"],"test_n":base["test_n"],
                    "demand_hour_baseline_status":base["status"],
                    "demand_hour_temperature_status":augmented["status"],
                    "baseline_mae":base["mae"],"temperature_mae":augmented["mae"],
                    "baseline_rmse":base["rmse"],"temperature_rmse":augmented["rmse"],
                    "baseline_brier":base["brier"],"temperature_brier":augmented["brier"],
                    "rmse_improvement_baseline_minus_temperature":(
                        float(base["rmse"]-augmented["rmse"]) if eligible else np.nan),
                    "temperature_model_beats_baseline_rmse":bool(eligible and
                         augmented["rmse"]<base["rmse"]),
                    "results_reportable":bool(eligible)
                })
    out=pd.DataFrame(rows)
    if len(out)!=32 or out.groupby("training_to_validation").size().ne(16).any():
        raise ValueError("Expected 10 binary and 6 gross outcomes in each direction")
    m={
      "genuine_source_run":42092282072,
      "support_screen_run":42091711862,
      "common_cell_ols_run":42093112865,
      "outcome_types":["reported Operating Time > 0","EPA gross MW conditional on positive reported operation"],
      "train_test_split":"nonoverlapping source calendar months (June 2024 and July 2024); both directions",
      "training_and_testing_within_original_occupied_joint_cells":True,
      "joint_cell_selected_from_covariates_in_both_periods":True,
      "model": "per-EPA-unit linear prediction; intercept + observed contemporaneous EIA930 BA demand GW + MST hour dummies; augmented model adds contemporaneous observed ERA5 temperature",
      "no_unknown_heldout_month_date_fixed_effects":True,
      "heldout_weather_and_demand_are_observed_not_forecasted":True,
      "predictive_evaluation_is_not_operational_ex_ante_forecast":True,
      "conditional_gross_evaluated_on_observed_positive_operation_not_predicted_running_hours":True,
      "source_units_are_not_independent_meteorological_sites":True,
      "no_causal_equipment_derating_or_available_net_power":True,
      "historical_forced_outages_and_eens_not_inferred":True,
      "not_usable_as_calibrated_pypsa_temperature_capacity_curve":True}
    return out,m


def main():
    parser=argparse.ArgumentParser()
    for x in ("june-panel","july-panel","output"):
        parser.add_argument("--"+x,required=True)
    args=parser.parse_args()
    out,manifest=audit(
        pd.read_csv(args.june_panel,dtype={"facility_id":"string","unit_id":"string"}),
        pd.read_csv(args.july_panel,dtype={"facility_id":"string","unit_id":"string"}))
    target=Path(args.output);target.mkdir(parents=True,exist_ok=True)
    out.to_csv(target/"epa_june_july_observed_covariate_month_transfer_scores.csv",index=False)
    (target/"epa_june_july_observed_covariate_month_transfer_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print(out.to_string(index=False))


if __name__=="__main__":
    main()
