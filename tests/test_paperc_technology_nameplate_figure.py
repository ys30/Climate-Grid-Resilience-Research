import pandas as pd
import pytest
from grid_resilience.paperc_technology_nameplate_figure import audited_matrix,BAS,TECH

def make():
    frames={}
    meta=[]
    categories=["natural_gas","wind","solar","hydro_nonpumped","pumped_hydro","nuclear",
                "coal","battery_storage","other_storage","petroleum","geothermal","other","unknown"]
    for year in (2023,2024):
        rows=[]
        for ba in BAS:
            for tech in categories:
                has=tech=="natural_gas"
                rows.append({"ba":ba,"technology_class":tech,
                    "monthly_operating_nameplate_mw":100.0 if has else 0.0,
                    "matched_930a_monthly_nameplate_mw":50.0 if has else 0.0,
                    "monthly_roster_nameplate_fraction_matched":0.5 if has else float("nan"),
                    "real_hourly_available_capacity_verified":False})
        frames[year]=pd.DataFrame(rows)
        meta.append({"year":year,"monthly_total_nameplate_mw":400,
                     "matched_nameplate_mw":200})
    return frames,meta

def test_source_fraction_and_zero_denominator_na():
    result=audited_matrix(*make())
    assert result[2023].shape==(4,9)
    assert (result[2024][:,0]==.5).all()
    assert pd.isna(result[2024][:,1:]).all()

def test_fake_physical_claim_rejected():
    f,m=make()
    f[2024].loc[0,"real_hourly_available_capacity_verified"]=True
    with pytest.raises(ValueError,match="physical"):
        audited_matrix(f,m)

def test_wrong_denominator_rejected():
    f,m=make()
    m[0]["monthly_total_nameplate_mw"]=401
    with pytest.raises(ValueError,match="denominator"):
        audited_matrix(f,m)
