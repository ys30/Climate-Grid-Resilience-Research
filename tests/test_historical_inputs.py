import pandas as pd
import pytest
from grid_resilience.historical_inputs import prepare

def make_inputs(tmp_path):
    hours=["2024-07-01T00:00:00Z","2024-07-01T01:00:00Z"]
    demand=pd.DataFrame([{"timestamp":t,"ba":b,"demand_mw":100} for t in hours for b in ("AZPS","CISO")])
    weather=pd.DataFrame([{"timestamp":t,"ba":b,"temperature_c":34,"wind_availability":.5} for t in hours for b in ("AZPS","CISO")])
    capacity=pd.DataFrame([{"ba":b,"gas_mw":100,"wind_mw":40,"source_year":2024,"capacity_source":"audited_EIA860_projection"} for b in ("AZPS","CISO")])
    paths=[]
    for name,data in (("d",demand),("w",weather),("c",capacity)):
        p=tmp_path/f"{name}.csv";data.to_csv(p,index=False);paths.append(p)
    return paths

def test_prepares_manifest(tmp_path):
    d,w,c=make_inputs(tmp_path)
    m=prepare(d,w,c,tmp_path/"out","event1")
    assert m["hours"]==2 and m["bas"]==["AZPS","CISO"]
    assert (tmp_path/"out"/"input_provenance.json").exists()

def test_rejects_missing_hour(tmp_path):
    d,w,c=make_inputs(tmp_path)
    frame=pd.read_csv(w).iloc[:-1]
    frame.to_csv(w,index=False)
    with pytest.raises(ValueError,match="Incomplete BA-hour"):
        prepare(d,w,c,tmp_path/"out","event1")

def test_rejects_unprovenanced_capacity(tmp_path):
    d,w,c=make_inputs(tmp_path)
    frame=pd.read_csv(c).drop(columns="capacity_source")
    frame.to_csv(c,index=False)
    with pytest.raises(ValueError,match="capacity missing"):
        prepare(d,w,c,tmp_path/"out","event1")
