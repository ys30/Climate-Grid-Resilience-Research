import pandas as pd
import pytest
from grid_resilience.bpat_july2024_hydro_cross_source_scope import audit, HOURS, HYFIELD

def inputs():
    a=pd.DataFrame([
        {"reported_ba":"BPAT","prime_mover":"HY","period":"2024-07",
         "net_generation_mwh":6000.0,"plant_month_rows":55,
         "coverage_status":"observed_source_rows"},
        {"reported_ba":"BPAT","prime_mover":"PS","period":"2024-07",
         "net_generation_mwh":-20.0,"plant_month_rows":1,
         "coverage_status":"observed_source_rows"}])
    b=pd.DataFrame({
        "Balancing Authority":"BPAT",
        "UTC Time at End of Hour":(HOURS+pd.Timedelta(hours=1)).strftime("%m/%d/%Y %I:%M:%S %p"),
        "Net Generation (MW)":200.0,
        HYFIELD:10.0})
    c=pd.DataFrame([{"ba":"BPAT","gas_mw":3000.,"wind_mw":2000.,
        "capacity_source":"GENERIC_THERMAL_PROXY_PARTIAL"}])
    return a,b,c

def test_original_scoped_hydro_coverage_and_signed_ps():
    rows,m=audit(*inputs())
    assert len(rows)==1 and m["official_eia930_complete_july_hour_count"]==744
    assert m["eia923_observed_page1_hy_plus_ps_signed_net_mwh"]==5980.
    assert m["eia930_observed_hydro_plus_pumped_group_net_mwh"]==7440.
    assert not m["source_reporting_grains_equivalent_certified"]
    assert not m["historical_blackouts_or_eens_identified"]

def test_missing_eia930_hydro_hour_not_filled():
    a,b,c=inputs()
    b[HYFIELD]=b[HYFIELD].astype(object)
    b.loc[0,HYFIELD]=""
    with pytest.raises(ValueError,match="Missing/blank"):
        audit(a,b,c)

def test_missing_monthly_ps_not_zero():
    a,b,c=inputs()
    with pytest.raises(ValueError,match="Missing or duplicate"):
        audit(a.iloc[:1],b,c)

def test_missing_official_hour_rejected():
    a,b,c=inputs()
    with pytest.raises(ValueError,match="grid incomplete"):
        audit(a,b.iloc[:-1],c)

def test_no_fabricated_full_fleet_label():
    a,b,c=inputs()
    c.loc[0,"capacity_source"]="PHYSICAL_FULL_FLEET"
    with pytest.raises(ValueError,match="partial gas/wind"):
        audit(a,b,c)

def test_malformed_monthly_number_rejected():
    a,b,c=inputs()
    a["net_generation_mwh"]=a["net_generation_mwh"].astype(object)
    a.loc[0,"net_generation_mwh"]="not numeric"
    with pytest.raises(ValueError):
        audit(a,b,c)
