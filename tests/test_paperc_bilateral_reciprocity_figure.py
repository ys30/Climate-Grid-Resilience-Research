import pandas as pd
import pytest
from grid_resilience.paperc_bilateral_reciprocity_figure import select


def dataset():
    d=[]
    for t in pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h"):
        for a,b,abs_value in (("AZPS","CISO",3.0),("BPAT","CISO",0.0)):
            d.append({"utc_hour_start":t.isoformat(),"ba_a":a,"ba_b":b,
                      "both_direction_values_present":True,
                      "absolute_reciprocity_sum_mw":abs_value})
    # Source cohort is larger than selected internal pairs.
    for i in range(6552):
        d.append({"utc_hour_start":f"external_hour_{i}",
                  "ba_a":"BPAT","ba_b":"OUTSIDE",
                  "both_direction_values_present":False,
                  "absolute_reciprocity_sum_mw":None})
    return pd.DataFrame(d),{"unordered_pair_hour_keys":6888,"pair_groups":41,
                             "historical_eens_validated":False}


def test_source_gated_two_pair_fig_data():
    x,m=dataset()
    s=select(x,m)
    assert len(s)==2
    assert s.pair_hours.eq(168).all()
    assert s.sum_absolute_reciprocal_discrepancy_mwh.max()==504
    assert not s.reporting_is_physical_line_capacity.any()


def test_no_false_zero_for_missing_counterdirection():
    x,m=dataset()
    x.loc[0,"both_direction_values_present"]=False
    with pytest.raises(ValueError,match="zero"):
        select(x,m)


def test_source_manifest_must_match():
    x,m=dataset()
    m["historical_eens_validated"]=True
    with pytest.raises(ValueError,match="source"):
        select(x,m)
