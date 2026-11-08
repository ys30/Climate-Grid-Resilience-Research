import pandas as pd
import pytest

from grid_resilience.paperc_2024_bilateral_shadow_balance import compare

BAS=("AZPS","BPAT","CISO","SRP")


def data():
    hours=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    a,b=[],[]
    for t in hours:
        for ba in BAS:
            absent=ba=="CISO"
            a.append({"utc_hour_start":t.isoformat(),"ba":ba,
                "demand_mw":100.0,"net_generation_mw":120.0,
                "net_interchange_mw":None if absent else 20.0,
                "raw_triplet_present":not absent})
            b.append({"utc_hour_start":t.isoformat(),"ba":ba,
                "sum_reported_bilateral_mw":20.0,
                "bilateral_all_present_counterparty_values_reported":True,
                "balance_total_interchange_reported":not absent})
    return pd.DataFrame(a),pd.DataFrame(b)


def test_candidate_residual_only_does_not_replace_source():
    hourly,s=compare(*data())
    c=s[s.ba=="CISO"].iloc[0]
    assert c.original_total_interchange_missing_hours==168
    assert c.source_missing_with_bilateral_sum_hours==168
    assert c.candidate_shadow_arithmetic_closing_missing_total_hours==168
    assert hourly.loc[hourly.ba.eq("CISO"),"net_interchange_mw"].isna().all()
    assert not s.physical_transmission_or_EENS_calibrated.any()


def test_nonclosing_candidate_does_not_imply_outage():
    a,b=data()
    b.loc[b.ba.eq("CISO"),"sum_reported_bilateral_mw"]=30
    _,s=compare(a,b)
    c=s[s.ba=="CISO"].iloc[0]
    assert c.candidate_shadow_arithmetic_nonclosing_missing_total_hours==168
    assert c.candidate_shadow_signed_residual_on_missing_total_hours_mwh==-1680
    assert not c.physical_transmission_or_EENS_calibrated


def test_missing_bilateral_does_not_become_zero():
    a,b=data()
    b.loc[0,"bilateral_all_present_counterparty_values_reported"]=False
    _,s=compare(a,b)
    assert s.loc[s.ba.eq("AZPS"),"source_missing_with_bilateral_sum_hours"].iloc[0]==0


def test_duplicates_not_admitted():
    a,b=data()
    b.loc[0,"utc_hour_start"]=b.loc[4,"utc_hour_start"]
    with pytest.raises(ValueError,match="Duplicate"):
        compare(a,b)


def test_missing_source_hour_rejected():
    a,b=data()
    with pytest.raises(ValueError,match="168h x 4BA"):
        compare(a.iloc[:-1],b)
