import pandas as pd
import pytest
from grid_resilience.paperc_e1_original_proxy_vs_eia860_annual import BAS, reconcile


def fixtures():
    rows=[]
    for ba in BAS:
        for tech,mw in (("coal",100.),("gas",200.),("wind",30.),("solar",40.)):
            rows.append(dict(ba=ba,technology=tech,nameplate_capacity_mw=mw,
                             generator_rows=1,source_year=2024))
    proxy=pd.DataFrame([dict(ba=ba,gas_mw=900,wind_mw=30,source_year=2024,
                             capacity_source="EIA860_partial_nameplate_GENERIC_THERMAL_PROXY")
                        for ba in BAS])
    scope=dict(source_manifests=[
        dict(source_year=2023),dict(source_year=2024,
            four_ba_operable_rows=3268,four_ba_selected_single_fuel_rows=2625,
            excluded_four_ba_rows=643,complete_physical_fleet_admitted=False)])
    vintage=pd.DataFrame([dict(year=2024,ba=ba,source_rows=n,
            monthly_no_verified_identity=unverified,
            monthly_unmatched=unmatched,monthly_ba_conflicts=conflicts,
            monthly_same_ba_matches=n-unverified-unmatched-conflicts,
            monthly_ambiguous=0,vintage_match_category_changes=0)
        for ba,n,unverified,unmatched,conflicts in
        zip(BAS,[133,298,1434,95],[4,0,225,2],[2,0,8,0],[12,6,9,0])])
    return pd.DataFrame(rows),proxy,scope,vintage


def test_annual_roster_scope_and_original_thermal_proxy_are_not_added():
    res,m=reconcile(*fixtures())
    assert len(res)==4
    assert all(res.annual_2024_gas_only_nameplate_mw==200)
    assert all(res.original_model_generic_thermal_proxy_mw==900)
    assert not res.source_populations_additively_comparable.any()
    assert m["physical_grid_capacity_complete"] is False


def test_missing_original_proxy_ba_is_rejected():
    a,b,c,d=fixtures()
    with pytest.raises(ValueError,match="partial proxy"):
        reconcile(a,b.iloc[:-1],c,d)


def test_duplicate_annual_technology_is_rejected():
    a,b,c,d=fixtures()
    with pytest.raises(ValueError,match="Annual"):
        reconcile(pd.concat([a,a.iloc[[0]]],ignore_index=True),b,c,d)


def test_unverified_eia930a_id_population_must_not_be_silenced():
    a,b,c,d=fixtures()
    d.loc[d.ba=="CISO","monthly_no_verified_identity"]=0
    with pytest.raises(ValueError,match="population changed"):
        reconcile(a,b,c,d)


def test_incomplete_2024_operable_roster_is_not_certified():
    a,b,c,d=fixtures()
    c["source_manifests"][1]["complete_physical_fleet_admitted"]=True
    with pytest.raises(ValueError,match="scope changed"):
        reconcile(a,b,c,d)
