import pandas as pd
import pytest
from grid_resilience.eia860_adapter import adapt

def sample(tmp_path):
    rows=[]
    for ba in ("CISO","AZPS","BPAT","SRP"):
        for technology,mw in (("thermal",100),("wind",30),("solar",20),("storage",10)):
            rows.append({"ba":ba,"technology":technology,"capacity_mw":mw,"source_year":2024})
    p=tmp_path/"eia860.csv"
    pd.DataFrame(rows).to_csv(p,index=False)
    return p

def test_maps_only_supported_and_declares_exclusions(tmp_path):
    manifest=adapt(sample(tmp_path),tmp_path/"out")
    d=pd.read_csv(tmp_path/"out"/"capacity.csv")
    assert len(d)==4 and d.gas_mw.eq(100).all()
    assert manifest["excluded_nameplate_mw"]==120
    assert "GENERIC_THERMAL_PROXY" in d.capacity_source.iloc[0]

def test_rejects_incomplete_ba(tmp_path):
    p=sample(tmp_path)
    d=pd.read_csv(p).query("ba != 'SRP'")
    d.to_csv(p,index=False)
    with pytest.raises(ValueError,match="BA coverage"):
        adapt(p,tmp_path/"out")

def test_rejects_wrong_source_year(tmp_path):
    p=sample(tmp_path)
    d=pd.read_csv(p);d.loc[0,"source_year"]=2023;d.to_csv(p,index=False)
    with pytest.raises(ValueError,match="year mismatch"):
        adapt(p,tmp_path/"out")

def test_rejects_missing_thermal(tmp_path):
    p=sample(tmp_path)
    d=pd.read_csv(p).query("not (ba == 'AZPS' and technology == 'thermal')")
    d.to_csv(p,index=False)
    with pytest.raises(ValueError,match="thermal and wind"):
        adapt(p,tmp_path/"out")
