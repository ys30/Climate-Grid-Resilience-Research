import pandas as pd
import pytest
from grid_resilience.paperc_eia930_fuel_reporting_figure import matrix,BAS,LABELS

def sample():
    rows=[]
    for ba in BAS:
        for label in LABELS:
            count=161 if "without Integrated" in label else 0
            rows.append({"year":2024,"ba":ba,"source_half":"Jul_Dec",
                "original_category_label":label,"source_hours":161,
                "reported_hours":count,"blank_hours":161-count,
                "reported_fraction":count/161,
                "cross_2024_schema_full_168h_fuel_total_certified":False})
    return pd.DataFrame(rows),{"legacy_and_modern_schema_mwh_not_automatically_additive":True}

def test_modern_schema_reports_only_present_cells():
    m=matrix(*sample())
    assert m.shape==(7,4)
    assert m[0,:].sum()==4
    assert m[1,:].sum()==0
    assert m[6,:].sum()==0

def test_missing_category_not_treated_as_zero():
    d,s=sample()
    d.loc[0,"reported_hours"]=0
    with pytest.raises(ValueError,match="reconcile"):
        matrix(d,s)

def test_forged_168h_harmonization_rejected():
    d,s=sample()
    d.loc[0,"cross_2024_schema_full_168h_fuel_total_certified"]=True
    with pytest.raises(ValueError,match="Forbidden"):
        matrix(d,s)

def test_missing_source_label_rejected():
    d,s=sample()
    with pytest.raises(ValueError,match="Incomplete"):
        matrix(d.iloc[:-1],s)
