import numpy as np
import pandas as pd
import pytest
from grid_resilience.paperc_caiso_battery_observed_envelope import compute

def fixture():
    rows=[]
    for year,day in ((2023,"2023-07-10"),(2024,"2024-07-01")):
        for k,t in enumerate(pd.date_range(day,periods=2016,freq="5min",tz="UTC")):
            x=100. if k%24<12 else -50.
            rows.append({"year":year,"utc_5min_start":t.isoformat(),
                "total_batteries_5min_mw":x,
                "standalone_batteries_5min_mw":x-2,
                "hybrid_batteries_5min_mw":2.,
                "fuelsource_batteries_5min_mw":x})
    return pd.DataFrame(rows),{
        "market_EN_is_preliminary_not_settlement_metering":True,
        "telemetry_total_batteries_includes_hybrid_scope":True}

def test_complete_observed_envelope_with_runs_but_no_soc():
    summary,hours,days,meta=compute(*fixture())
    assert len(summary)==6 and len(hours)==2*3*168
    assert len(days)==2*3*7
    r=summary[(summary.year==2024)&(summary.series=="total")].iloc[0]
    assert r.source_points==2016
    assert r.observed_max_discharge_mw==100
    assert r.observed_max_charge_mw==50
    assert r.observed_positive_interval_count==1008
    assert r.observed_descriptive_positive_mwh==8400
    assert r.observed_descriptive_negative_charge_mwh==4200
    assert r.longest_consecutive_positive_minutes==60
    assert r.longest_consecutive_negative_minutes==60
    assert meta["no_storage_energy_mwh_initial_soc_or_efficiency_inferred"]
    assert not summary.certified_storage_power_rating_mw_inferred.any()

def test_partial_five_minute_source_not_zero_filled():
    a,m=fixture()
    with pytest.raises(ValueError,match="cohort"):
        compute(a.iloc[1:],m)

def test_conflicting_original_fuel_source_not_accepted():
    a,m=fixture()
    a.loc[1,"fuelsource_batteries_5min_mw"]+=12
    with pytest.raises(ValueError,match="disagree"):
        compute(a,m)

def test_infinite_numeric_source_fails():
    a,m=fixture()
    a.loc[2,"total_batteries_5min_mw"]=np.inf
    with pytest.raises(ValueError,match="nonfinite"):
        compute(a,m)

def test_missing_provenance_rejected():
    a,m=fixture()
    m["telemetry_total_batteries_includes_hybrid_scope"]=False
    with pytest.raises(ValueError,match="hybrid"):
        compute(a,m)
