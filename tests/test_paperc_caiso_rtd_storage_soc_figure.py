import pandas as pd
import pytest
from grid_resilience.paperc_caiso_rtd_storage_soc_figure import evaluate,STUDIES

def sample(remove_one=False):
    data=[]
    for year,start in STUDIES.items():
        for t in pd.date_range(start,periods=168,freq="h"):
            for typ in ("EN","SOC"):
                for i in range(1,13):
                    if remove_one and year==2023 and i==12 and t.hour==0:
                        continue
                    data.append({"eia930_study_year":year,
                                 "utc_hour_start_from_local_trade_date":t.isoformat(),
                                 "market":"RTD","resource_type":"LESR",
                                 "output_type":typ,"interval_index":i,
                                 "original_market_value":5. if typ=="EN" else 500.})
    scope={"utc_hour_join_uses_los_angeles_summer_dst":True,
           "market_result_source_not_actual_metered_charge_discharge":True}
    return pd.DataFrame(data),scope

def test_original_full_rtd_interval_count():
    d,m,scope=evaluate(*sample())
    assert len(d)==672 and len(m)==0
    assert d.recorded_5min_intervals.eq(12).all()
    assert d.complete_twelve_intervals.all()
    assert not scope["reliability_or_eens_calibrated"]

def test_missing_interval_kept_blank_not_zero():
    d,m,_=evaluate(*sample(remove_one=True))
    assert len(m)==14
    assert m.original_value_preserved_missing.all()
    assert d.loc[~d.complete_twelve_intervals,
                 "mean_raw_market_value_complete_hour_only"].isna().all()

def test_duplicate_interval_rejected():
    x,scope=sample()
    x=pd.concat([x,x.iloc[[0]]],ignore_index=True)
    with pytest.raises(ValueError,match="Repeated"):
        evaluate(x,scope)

def test_wrong_market_provenance_rejected():
    x,scope=sample()
    scope["market_result_source_not_actual_metered_charge_discharge"]=False
    with pytest.raises(ValueError,match="market"):
        evaluate(x,scope)
