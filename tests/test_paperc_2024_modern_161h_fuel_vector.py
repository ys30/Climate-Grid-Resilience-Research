import pandas as pd
import pytest
from grid_resilience.paperc_2024_modern_161h_fuel_vector import audit,FUELS,BAS,START,HOURS

def sample():
    b=[]; f=[]
    for ba in BAS:
        for i in range(HOURS):
            t=START+pd.Timedelta(hours=i)
            b.append({"ba":ba,"utc_hour_start":t.isoformat(),
                      "source_partition":"2024_Jul_Dec","net_generation_mw":100.,
                      "demand_mw":100.,"net_interchange_mw":None if ba=="CISO" else 0.})
            for label in FUELS:
                null=(ba=="BPAT" and label=="Coal")
                f.append({"year":2024,"ba":ba,"utc_hour_start":t.isoformat(),
                          "original_partition":"Jul_Dec","original_fuel_category":label,
                          "fuel_value_reported":not null,
                          "reported_fuel_mwh":None if null else 10.})
    scope={"2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent":True,
           "blank_never_assumed_zero":True}
    return pd.DataFrame(b),pd.DataFrame(f),scope

def test_no_cross_schema_fake_total():
    hourly,summary,scope=audit(*sample())
    assert len(hourly)==644
    assert summary.set_index("ba").loc["BPAT","hours_six_components_all_numeric"]==0
    assert summary.set_index("ba").loc["AZPS","hours_six_components_all_numeric"]==161
    assert hourly.loc[hourly.ba=="BPAT","sum_six_original_reported_components_mwh"].isna().all()
    assert summary.loc[summary.ba=="AZPS","net_minus_selected_components_same_hours_mwh"].iloc[0]==6440.
    assert scope["net_minus_selected_categories_not_necessarily_unreported_generation"]

def test_reported_blank_cannot_be_filled():
    b,f,s=sample()
    i=f[(f.ba=="BPAT") & f.original_fuel_category.eq("Coal")].index[0]
    f.loc[i,"reported_fuel_mwh"]=0.
    with pytest.raises(ValueError,match="Null original"):
        audit(b,f,s)

def test_source_category_duplicate_rejected():
    b,f,s=sample()
    f=pd.concat([f,f.iloc[[0]]],ignore_index=True)
    with pytest.raises(ValueError,match="Duplicate"):
        audit(b,f,s)

def test_missing_modern_utc_hour_rejected():
    b,f,s=sample()
    with pytest.raises(ValueError,match="keys incomplete"):
        audit(b.iloc[:-1],f,s)

def test_missing_source_taxonomy_gate_rejected():
    b,f,s=sample()
    s["blank_never_assumed_zero"]=False
    with pytest.raises(ValueError,match="blank-not-zero"):
        audit(b,f,s)
