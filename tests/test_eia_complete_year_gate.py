import pandas as pd
from grid_resilience.eia_complete_year_gate import select

def test_rejects_incomplete_and_retains_full_year(tmp_path):
    p=tmp_path/"matrix.csv"
    rows=[]
    for tech in ("wind","solar"):
        for month in range(1,13):
            present=tech=="wind" or month!=5
            rows.append({"ba":"CISO","technology":tech,"period":f"2024-{month:02d}",
                "generation_mwh":1 if present else None,"record_present":present})
    pd.DataFrame(rows).to_csv(p,index=False)
    result=select(p,tmp_path/"out")
    assert result["complete_groups"]==1
    assert result["excluded_groups"][0]["months_present"]==11
    assert len(pd.read_csv(tmp_path/"out"/"complete_year_candidate_diagnostics.csv"))==12
