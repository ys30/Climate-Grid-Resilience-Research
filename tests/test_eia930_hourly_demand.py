import json
import pandas as pd
import pytest
from grid_resilience.eia930_hourly_demand import normalize

def source(tmp_path,missing=False):
    f=tmp_path/"api.json"
    rows=[{"period":t.strftime("%Y-%m-%dT%H"),"respondent":ba,"type":"D","value":"50"}
          for t in pd.date_range("2024-02-01",periods=3,freq="h",tz="UTC")
          for ba in ("CISO","AZPS","BPAT","SRP")]
    if missing: rows.pop()
    f.write_text(json.dumps({"response":{"total":len(rows),"data":rows}}))
    return f

def test_hourly_eia_demand_normalizes(tmp_path):
    result=normalize(source(tmp_path),tmp_path/"out","2024-02-01T00","2024-02-01T02")
    assert result["records"]==12
    assert result["historical_calibration_certified"] is False

def test_missing_ba_hour_rejected(tmp_path):
    with pytest.raises(ValueError,match="Incomplete BA-hour"):
        normalize(source(tmp_path,True),tmp_path/"out","2024-02-01T00","2024-02-01T02")

def test_pagination_rejected(tmp_path):
    f=source(tmp_path)
    d=json.loads(f.read_text());d["response"]["total"]=100;f.write_text(json.dumps(d))
    with pytest.raises(ValueError,match="Paginated"):
        normalize(f,tmp_path/"out","2024-02-01T00","2024-02-01T02")
