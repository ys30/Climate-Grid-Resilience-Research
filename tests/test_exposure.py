import pandas as pd
import pytest
from grid_resilience.exposure import summarize

def test_compound_exposure(tmp_path):
    x=pd.DataFrame([
        {"timestamp":"2024-07-01T00:00Z","ba":"CISO","demand_mw":100,"temperature_c":36,"wind_availability":.1},
        {"timestamp":"2024-07-01T01:00Z","ba":"CISO","demand_mw":80,"temperature_c":25,"wind_availability":.8},
    ])
    p=tmp_path/"in.csv";x.to_csv(p,index=False)
    r=summarize(p,tmp_path/"out.csv")
    assert r.set_index("condition").loc["compound","hours"]==1
    assert r.set_index("condition").loc["compound","total_demand_mwh"]==100
    assert r.set_index("condition").loc["all","hours"]==2

def test_reject_duplicate(tmp_path):
    x=pd.DataFrame([{"timestamp":"2024-07-01T00:00Z","ba":"CISO","demand_mw":100,
                     "temperature_c":36,"wind_availability":.1}]*2)
    p=tmp_path/"in.csv";x.to_csv(p,index=False)
    with pytest.raises(ValueError,match="Duplicate"):
        summarize(p,tmp_path/"out.csv")
