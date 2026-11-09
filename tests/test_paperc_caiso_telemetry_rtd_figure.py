import pandas as pd
import pytest
from grid_resilience.paperc_caiso_telemetry_rtd_figure import analyze

def fixture():
    rows=[]
    for year,date in ((2023,"2023-07-10"),(2024,"2024-07-01")):
        for k,t in enumerate(pd.date_range(date,periods=2016,freq="5min",tz="UTC")):
            missing=year==2023 and k in (5,6)
            rows.append({"year":year,"utc_5min_start":t.isoformat(),
               "total_batteries_5min_mw":float(k%100-50),
               "standalone_batteries_5min_mw":float(k%100-55),
               "hybrid_batteries_5min_mw":5.,
               "rtd_lesr_en_preliminary_market_value":None if missing else float(k%100-50)*1.1,
               "market_record_present":not missing})
    m={"market_EN_is_preliminary_not_settlement_metering":True,
       "rtd_lesr_is_market_resource_type_not_identical_scope":True}
    return pd.DataFrame(rows),m

def test_source_utc_coverage_and_predeclared_lag_sensitivity():
    d,s=analyze(*fixture())
    assert len(d)==4032 and len(s)==10
    assert set(s.rtd_market_utc_shift_minutes_for_sensitivity)=={-10,-5,0,5,10}
    assert s.loc[(s.year==2024)&(s.rtd_market_utc_shift_minutes_for_sensitivity==0),
                 "paired_source_five_minute_points"].iloc[0]==2016
    assert not s.real_dispatch_error_calibrated.any()

def test_no_imputed_missing_market_values():
    d,m=fixture()
    d.loc[5,"rtd_lesr_en_preliminary_market_value"]=0.
    with pytest.raises(ValueError,match="filled"):
        analyze(d,m)

def test_source_provenance_required():
    d,m=fixture()
    m["rtd_lesr_is_market_resource_type_not_identical_scope"]=False
    with pytest.raises(ValueError,match="Resource scope"):
        analyze(d,m)
