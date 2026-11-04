import pandas as pd
import pytest
from grid_resilience.srp_multitech_ba_coverage_gate import audit


def source():
    annual=pd.DataFrame({
        "plant_id":["001","1","2","3"],
        "generator_id":["A","B","C","D"],
        "plant_reported_ba":["SRP","SRP","SRP","AZPS"],
        "prime_mover":["GT","ST","PS","GT"],
        "energy_source_1":["NG","SUB","WAT","NG"],
        "nameplate_capacity_mw":[100.,50.,25.,60.]
    })
    page4=pd.DataFrame({
        "plant_id":["1","2","7"],"generator_id":["A","C","Z"],
        "reported_ba":["SRP"]*3,"period":["2024-01"]*3,
        "generation_mwh":[120.,-5.,18.]
    })
    return annual,page4


def test_reverse_ba_scope_and_tech_counts_conserve_signed_generation():
    a,p=source()
    rows,by,missing,m=audit(a,p)
    assert m["annual_plant_ba_operable_generator_count"]==3
    assert m["annual_and_page4_matched_generators"]==2
    assert m["annual_not_in_page4_generators"]==1
    assert m["page4_outside_annual_plant_ba_generator_count"]==1
    assert m["page4_total_reported_ba_signed_mwh"]==133.
    assert m["page4_matched_annual_signed_mwh"]==115.
    assert m["page4_outside_annual_plant_ba_signed_mwh"]==18.
    assert m["model_supply_technology_assigned_mw"]==150.
    assert set(by.technology)=={"gas","coal","excluded_unmodeled"}
    assert len(missing)==1
    assert not m["page4_absence_is_evidence_of_shutdown"]
    assert not m["ba_ownership_calibrated"]


def test_duplicate_annual_generator_fails_closed():
    a,p=source()
    with pytest.raises(ValueError,match="Duplicate annual"):
        audit(pd.concat([a,a.iloc[[0]]],ignore_index=True),p)


def test_duplicate_monthly_generator_fails_closed():
    a,p=source()
    with pytest.raises(ValueError,match="Duplicate Page4"):
        audit(a,pd.concat([p,p.iloc[[0]]],ignore_index=True))


def test_invalid_page4_generation_is_not_silently_zero():
    a,p=source()
    p.loc[0,"generation_mwh"]=float("nan")
    with pytest.raises(ValueError,match="Invalid Page4"):
        audit(a,p)


def test_absent_generator_month_does_not_enter_source_generation():
    a,p=source()
    rows,by,_,m=audit(a,p)
    coal=by.loc[by.technology.eq("coal")].iloc[0]
    assert coal.not_in_page4_generator_count==1
    assert coal.page4_matched_generator_count==0
    assert pd.isna(coal.page4_matching_signed_mwh)
    assert m["generation_month_missing_must_not_be_imputed_zero"]
