import numpy as np
import pandas as pd
import pytest
from grid_resilience.paperc_reciprocity_temporal import analyze,PAIRS


def sample():
    rows=[]
    for t in pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h"):
        for a,b in PAIRS:
            signed=0. if (a,b)==("BPAT","CISO") else 15.
            rows.append({"utc_hour_start":t.isoformat(),"ba_a":a,"ba_b":b,
                         "both_direction_values_present":True,
                         "signed_reciprocity_sum_mw":signed,
                         "absolute_reciprocity_sum_mw":abs(signed)})
    for i in range(6888-len(rows)):
        rows.append({"utc_hour_start":f"external_{i}","ba_a":"BPAT",
                     "ba_b":"OTHER","both_direction_values_present":False,
                     "signed_reciprocity_sum_mw":np.nan,
                     "absolute_reciprocity_sum_mw":np.nan})
    manifest={"unordered_pair_hour_keys":6888,"pair_groups":41,
              "historical_eens_validated":False,"missing_direction_never_converted_to_zero":True}
    return pd.DataFrame(rows),manifest


def test_six_pair_hour_temporal_and_source_partition_contract():
    pair,daily,hours,part,source=analyze(*sample())
    assert len(pair)==6 and len(daily)==42 and len(hours)==144
    assert pair.first_partition_hours.eq(7).all()
    assert pair.second_partition_hours.eq(161).all()
    assert pair.loc[pair.ba_b.eq("CISO")&pair.ba_a.eq("BPAT"),
                    "absolute_pair_discrepancy_mwh"].iloc[0]==0.
    assert not pair.physical_transmission_loss_identified.any()


def test_missing_source_direction_retains_missing_not_zero():
    d,m=sample()
    d.loc[0,"both_direction_values_present"]=False
    d.loc[0,"signed_reciprocity_sum_mw"]=np.nan
    d.loc[0,"absolute_reciprocity_sum_mw"]=np.nan
    p,_,_,_,_=analyze(d,m)
    x=p.loc[p.ba_a.eq("BPAT")&p.ba_b.eq("GRID")].iloc[0]
    assert x.missing_direction_hours==1
    assert x.both_numeric_hours==167


def test_missing_direction_numeric_value_rejected():
    d,m=sample()
    d.loc[0,"both_direction_values_present"]=False
    with pytest.raises(ValueError,match="zero"):
        analyze(d,m)


def test_missing_source_cohort_rejected():
    d,m=sample()
    with pytest.raises(ValueError,match="6,888"):
        analyze(d.iloc[:-1],m)


def test_incorrect_annual_source_period_rejected():
    d,m=sample()
    d.loc[0,"utc_hour_start"]="2023-07-01T00:00:00Z"
    with pytest.raises(ValueError,match="UTC calendar"):
        analyze(d,m)
