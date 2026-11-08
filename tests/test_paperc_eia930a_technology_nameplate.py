import pandas as pd
import pytest
from grid_resilience.paperc_eia930a_technology_nameplate import summarize,technology

BAS=("AZPS","BPAT","CISO","SRP")


def sample():
    monthly=[]
    joined=[]
    for i,ba in enumerate(BAS):
        plant=str(1000+i)
        monthly.extend([
            {"plant_id":plant,"generator_id":"G","eia860_plant_reported_ba":ba,
             "eia860_technology":"Natural Gas Fired Combined Cycle",
             "eia860_energy_source_1":"NG",
             "eia860_annual_operable_nameplate_mw":100.0},
            {"plant_id":plant,"generator_id":"W","eia860_plant_reported_ba":ba,
             "eia860_technology":"Onshore Wind Turbine",
             "eia860_energy_source_1":"WND",
             "eia860_annual_operable_nameplate_mw":50.0}])
        joined.append({"year":2024,"ba":ba,"eia930a_row":i,
             "plant_id":plant,"generator_id":"G",
             "monthly_860m_match_class":"matched_identity_same_plant_ba",
             "monthly_860m_nameplate_mw":100.0,
             "eia860_technology":"Natural Gas Fired Combined Cycle",
             "eia860_energy_source_1":"NG"})
    return pd.DataFrame(monthly),pd.DataFrame(joined)


def test_known_technology_categories():
    assert technology("Pumped Storage","WAT")=="pumped_hydro"
    assert technology("Batteries","MWH")=="battery_storage"
    assert technology("Solar Photovoltaic","SUN")=="solar"
    assert technology("Hydroelectric Conventional","WAT")=="hydro_nonpumped"
    assert technology("Wind Turbine","WND")=="wind"


def test_nameplate_fraction_uses_monthly_technology_ba_denominator():
    source,join=sample()
    table,counts,unmatched,meta=summarize(source,join,2024,"august")
    assert len(table)==4*13
    gas=table.loc[table.technology_class.eq("natural_gas")]
    assert gas.monthly_operating_nameplate_mw.eq(100).all()
    assert gas.matched_930a_monthly_nameplate_mw.eq(100).all()
    assert gas.monthly_roster_nameplate_fraction_matched.eq(1).all()
    wind=table.loc[table.technology_class.eq("wind")]
    assert wind.monthly_operating_nameplate_mw.eq(50).all()
    assert wind.matched_930a_monthly_nameplate_mw.eq(0).all()
    assert wind.monthly_roster_nameplate_fraction_matched.eq(0).all()
    assert meta["matched_nameplate_mw"]==400
    assert not meta["historical_eens_estimated"]
    assert not table.real_hourly_available_capacity_verified.any()


def test_unidentified_roster_row_never_joins_to_capacity():
    source,join=sample()
    join.loc[0,"monthly_860m_match_class"]="no_eia930a_source_identity"
    table,_,excluded,meta=summarize(source,join,2024,"august")
    assert len(excluded)==1 and meta["unmatched_930a_rows_kept_without_MW_inference"]==1
    assert table.loc[(table.ba=="AZPS")&(table.technology_class=="natural_gas"),
                     "matched_930a_monthly_nameplate_mw"].iloc[0]==0


def test_falsified_monthly_mw_fails():
    source,join=sample()
    join.loc[0,"monthly_860m_nameplate_mw"]=999.0
    with pytest.raises(ValueError,match="nameplate mismatch"):
        summarize(source,join,2024,"august")


def test_duplicate_claimed_unique_generator_fails():
    source,join=sample()
    join.loc[1,"plant_id"]=join.loc[0,"plant_id"]
    join.loc[1,"generator_id"]=join.loc[0,"generator_id"]
    with pytest.raises(ValueError,match="repeats"):
        summarize(source,join,2024,"august")
