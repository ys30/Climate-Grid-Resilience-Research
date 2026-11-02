"""Synthetic regression covering import>local demand and outward exchange."""
import pandas as pd
from grid_resilience.srp_explicit_import_export import run

def main():
    timestamps=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    cap=pd.DataFrame([{"ba":"SRP","technology":"NG","capacity_mw":100,"marginal_cost":55}])
    for name,interchange,expected_import,expected_export in (
        ("large_import",-70,744*70,0),
        ("net_export",20,0,744*20)):
        data=pd.DataFrame({"timestamp":timestamps,"demand_mw":50.,"interchange_mw":interchange})
        result=run(data,cap,"SRP",2024,1)
        assert abs(result["scheduled_import_mwh"]-expected_import)<1e-6
        assert abs(result["scheduled_export_mwh"]-expected_export)<1e-6
        assert result["solver_status"]=="ok" and result["solver_condition"]=="optimal"
        assert abs(result["energy_balance_residual_mwh"])<1e-4
        assert result["unserved_mwh"]<1e-4
        if name=="net_export":
            assert result["spilled_mwh"]<1e-4
            assert abs(result["local_generation_mwh"]-744*70)<1e-4
        if name=="large_import":
            assert abs(result["spilled_mwh"]-744*20)<1e-4
            assert abs(result["local_generation_mwh"])<1e-4
        print(name,result)
    # Alternate import/export hours; check signed aggregation is not confused with gross flows.
    interchange=[-70 if i%2==0 else 20 for i in range(744)]
    mixed=pd.DataFrame({"timestamp":timestamps,"demand_mw":50.,"interchange_mw":interchange})
    result=run(mixed,cap,"SRP",2024,1)
    assert abs(result["scheduled_import_mwh"]-372*70)<1e-6
    assert abs(result["scheduled_export_mwh"]-372*20)<1e-6
    assert abs(result["net_interchange_mwh"]-(372*20-372*70))<1e-6
    assert abs(result["spilled_mwh"]-372*20)<1e-4
    assert abs(result["local_generation_mwh"]-372*70)<1e-4
    assert result["hours_with_spillage"]==372
    assert result["hours_with_unserved"]==0
    assert result["solver_condition"]=="optimal"
    assert abs(result["energy_balance_residual_mwh"])<1e-4
    print("mixed_import_export",result)
if __name__=="__main__":main()
