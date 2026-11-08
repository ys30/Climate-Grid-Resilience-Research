import pandas as pd
import pytest
from grid_resilience.paperc_eia930a_eia860_generator_match import compare, _identity

BAS=("AZPS","BPAT","CISO","SRP")


def fixture():
    rec=[]
    for ba in BAS:
        rec.append({"year":2024,"ba":ba,
          "plant_id_source":str(100+BAS.index(ba)),
          "generator_id_source":"GT1","technology":"Natural Gas Fired Combined Cycle",
          "reported_nameplate_mw":100.,
          "eia860_generator_id_recognized":True})
    rec.append({"year":2024,"ba":"AZPS",
        "plant_id_source":"999","generator_id_source":"X1",
        "technology":"Onshore Wind Turbine","reported_nameplate_mw":20.,
        "eia860_generator_id_recognized":False})
    rec.append({"year":2024,"ba":"BPAT",
        "plant_id_source":"100","generator_id_source":"GT1",
        "technology":"Natural Gas Fired Combined Cycle","reported_nameplate_mw":90.,
        "eia860_generator_id_recognized":True})
    fleet=pd.DataFrame([{"plant_id":str(100+i),"generator_id":"GT1",
       "eia860_technology":"Natural Gas Fired Combined Cycle",
       "eia860_energy_source_1":"NG","eia860_prime_mover":"CC",
       "eia860_annual_operable_nameplate_mw":110.,
       "eia860_plant_reported_ba":ba} for i,ba in enumerate(BAS)])
    return pd.DataFrame(rec),fleet


def test_exact_id_ba_conflicts_and_unmatched_fallback_separated():
    x,y,m=compare(*fixture(),2024)
    assert len(x)==6
    assert set(y.ba)==set(BAS)
    az=y[y.ba.eq("AZPS")].iloc[0]
    assert az.source_identity_missing_rows==1
    assert az.exact_identity_and_same_ba_rows==1
    bp=y[y.ba.eq("BPAT")].iloc[0]
    assert bp.exact_identity_ba_conflict_rows==1
    assert bp.cross_ba_duplicate_plant_generator_keys==1
    assert m["cross_ba_duplicate_generator_identity_keys"]==1
    assert x.loc[x.match_class.eq("matched_identity_same_plant_ba"),
        "annual_nameplate_delta_930a_minus_860_mw"].eq(-10).all()
    assert not x.generator_online_hourly_or_available_mw_inferred.any()


def test_fallback_ids_not_accepted_even_if_fake_identity_matches():
    a,b=fixture()
    a.loc[a.eia860_generator_id_recognized.eq(False),"plant_id_source"]="100"
    a.loc[a.eia860_generator_id_recognized.eq(False),"generator_id_source"]="GT1"
    x,_,_=compare(a,b,2024)
    v=x.loc[x.eia930a_row.eq(4)].iloc[0]
    assert v.match_class=="no_eia930a_source_identity"


def test_duplicate_same_ba_generator_rejected():
    a,b=fixture()
    a=pd.concat([a,a.iloc[[0]]],ignore_index=True)
    with pytest.raises(ValueError,match="Duplicate EIA930A"):
        compare(a,b,2024)


def test_duplicate_eia860_generator_rejected():
    a,b=fixture()
    b=pd.concat([b,b.iloc[[0]]],ignore_index=True)
    with pytest.raises(ValueError,match="Ambiguous"):
        compare(a,b,2024)


def test_year_mismatch_rejected():
    a,b=fixture()
    with pytest.raises(ValueError,match="Wrong annual"):
        compare(a,b,2023)


def test_plant_numeric_conversion_preserves_generator_leading_zeros():
    assert _identity("123.0",True)=="123"
    assert _identity("001",False)=="001"
