import pandas as pd
from grid_resilience.eia930_import_dependence_audit import audit

def test_net_import_share_and_accounting_flags(tmp_path):
    interchange=tmp_path/"interchange.csv";demand=tmp_path/"demand.csv"
    pd.DataFrame([
        {"ba":"AZPS","period":"2024-02","reported_interchange_mwh":-100,
         "generation_minus_demand_mwh":-100,"discrepancy_mwh":0},
        {"ba":"BPAT","period":"2024-02","reported_interchange_mwh":200,
         "generation_minus_demand_mwh":150,"discrepancy_mwh":-50}
    ]).to_csv(interchange,index=False)
    pd.DataFrame([
        {"ba":"AZPS","timestamp":"2024-02-01T00:00:00+00:00","demand_mw":400},
        {"ba":"BPAT","timestamp":"2024-02-01T00:00:00+00:00","demand_mw":500}
    ]).to_csv(demand,index=False)
    m=audit(interchange,demand,tmp_path/"out")
    x=pd.read_csv(tmp_path/"out"/"reported_interchange_dependence_2024_02.csv")
    row=x.loc[x.ba=="AZPS"].iloc[0]
    assert row.reported_net_import_mwh==100
    assert row.net_import_share_of_demand==0.25
    assert m["accounting_flagged_bas"]==["BPAT"]
    assert m["net_imported_bas"]==["AZPS"]
    assert m["physical_transfer_capacity_inferred"] is False
