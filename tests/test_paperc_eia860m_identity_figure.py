import pandas as pd
import pytest
from grid_resilience.paperc_eia860m_identity_figure import calculate

def sources():
    annual={}
    monthly={}
    for year in (2023,2024):
        annual[year]=pd.DataFrame([{"year":year,"ba":ba,"eia930a_schedule2_rows":100,
            "exact_identity_and_same_ba_rows":80}
            for ba in ("AZPS","BPAT","CISO","SRP")])
        monthly[year]=pd.DataFrame([{"year":year,"ba":ba,"source_rows":100,
            "monthly_same_ba_matches":85,"vintage_match_category_changes":5}
            for ba in ("AZPS","BPAT","CISO","SRP")])
    meta=[{"year":y,"actual_hourly_dispatch_or_EENS_calibrated":False} for y in (2023,2024)]
    return annual,monthly,meta

def test_identity_fraction_is_roster_rows_not_capacity():
    result=calculate(*sources())
    assert len(result)==8
    assert result.annual_same_ba_exact_fraction.eq(.8).all()
    assert result.monthly_same_ba_exact_fraction.eq(.85).all()
    assert result.percentage_point_change_annual_to_monthly.round(3).eq(5).all()
    assert not result.hourly_available_mw_or_EENS_identified.any()

def test_nonidentical_denominator_rejected():
    a,m,scope=sources()
    m[2024].loc[0,"source_rows"]=99
    with pytest.raises(ValueError,match="denominator"):
        calculate(a,m,scope)

def test_bad_provenance_rejected():
    a,m,scope=sources()
    scope[0]["actual_hourly_dispatch_or_EENS_calibrated"]=True
    with pytest.raises(ValueError,match="manifest"):
        calculate(a,m,scope)
