import csv
from datetime import datetime,timedelta,timezone
from grid_resilience.eia930_fuel_decomposition import audit,FUELS,BAS,FMT

def test_all_blank_fuel_categories_are_not_zero_reconciliation(tmp_path):
    p=tmp_path/"eia.csv"
    fields=["Balancing Authority","UTC Time at End of Hour","Net Generation (MW)"]+["Net Generation (MW) from "+f for f in FUELS]
    with p.open("w",newline="") as file:
        w=csv.DictWriter(file,fieldnames=fields);w.writeheader()
        t=datetime(2024,2,1,tzinfo=timezone.utc)
        for ba in BAS:
            for hour in range(696):
                row={"Balancing Authority":ba,
                     "UTC Time at End of Hour":(t+timedelta(hours=hour+1)).strftime(FMT),
                     "Net Generation (MW)":"100"}
                row.update({col:"" for col in fields[3:]})
                w.writerow(row)
    result=audit(p,tmp_path/"out")
    assert result["comparison_complete"] is False
    for ba in BAS:
        assert result["by_ba"][ba]["comparable_hours"]==0
        assert result["by_ba"][ba]["signed_delta_mwh"] is None
