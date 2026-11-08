import pandas as pd
import pytest
from grid_resilience.paperc_eia930_stable_fuel_cohorts import admitted,STABLE,BAS,COHORTS


def sample():
    rows=[]
    for year,dt in COHORTS.items():
        hours=pd.date_range(dt,periods=168,freq="h")
        for i,t in enumerate(hours):
            for ba in BAS:
                for fuel in STABLE:
                    missing=year==2024 and i==0 and ba=="CISO" and fuel=="Coal"
                    val=None if missing else 25.0 if fuel=="Natural Gas" else 0.
                    rows.append({"year":year,"utc_hour_start":t.isoformat(),
                        "ba":ba,"original_partition":(
                        "2023_Jul_Dec" if year==2023 else
                        "2024_Jan_Jun" if i<7 else "2024_Jul_Dec"),
                        "original_fuel_category":fuel,
                        "reported_fuel_mwh":val,"fuel_value_reported":not missing,
                        "reported_zero":val==0 if val is not None else False})
    return pd.DataFrame(rows),{"2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent":True}


def test_two_cohorts_and_complete_gas():
    detail,summary,meta=admitted(*sample())
    assert len(detail)==2*168*4*len(STABLE)
    assert len(summary)==24
    g=summary.loc[summary.stable_original_category.eq("Natural Gas")]
    assert len(g)==8 and g.full_168h_fuel_energy_comparison_eligible.all()
    assert g.full_168h_reported_energy_mwh.eq(4200).all()
    assert meta["2024_wind_solar_hydro_battery_taxonomy_not_harmonized"]


def test_absent_coal_cannot_be_completed_by_zero():
    detail,summary,_=admitted(*sample())
    v=summary[(summary.year==2024)&summary.ba.eq("CISO")&
              summary.stable_original_category.eq("Coal")].iloc[0]
    assert v.reported_hours==167 and v.blank_hours==1
    assert pd.isna(v.full_168h_reported_energy_mwh)
    assert detail[(detail.year==2024)&detail.ba.eq("CISO")&
                  detail.original_fuel_category.eq("Coal")].reported_fuel_mwh.isna().sum()==1


def test_forged_missing_fuel_value_rejected():
    df,m=sample()
    first=df.index[(df.year==2024)&df.ba.eq("CISO")&
                 df.original_fuel_category.eq("Coal")][0]
    df.loc[first,"reported_fuel_mwh"]=0.
    with pytest.raises(ValueError,match="silently filled"):
        admitted(df,m)


def test_incomplete_stable_hour_rejected():
    df,m=sample()
    with pytest.raises(ValueError,match="168"):
        admitted(df.iloc[:-1],m)


def test_invalid_schema_provenance_rejected():
    df,m=sample()
    m["2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent"]=False
    with pytest.raises(ValueError,match="taxonomy"):
        admitted(df,m)
