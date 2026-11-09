import pandas as pd
import pytest
from grid_resilience.paperc_caiso_battery_counterfactual_bridge import scenario_matrix, save

def fixture():
    rows=[]
    for y in (2023,2024):
        for kind in ("total","standalone","hybrid"):
            rows.append({"year":y,"series":kind,"source_points":2016,
                "certified_storage_power_rating_mw_inferred":False,
                "matched_battery_soc_mwh_inferred":False,
                "discharge_positive_only_p95_mw":4000.,
                "charge_positive_magnitude_only_p95_mw":2500.,
                "discharge_positive_only_p99_mw":5000.,
                "charge_positive_magnitude_only_p99_mw":3000.})
    return pd.DataFrame(rows)

def test_explicit_counterfactual_not_capacity_or_soc():
    t=scenario_matrix(fixture())
    assert len(t)==32 and t.scenario_id.nunique()==32
    assert set(t.power_mw)=={2500.,3000.}
    assert (t.energy_mwh/t.power_mw).isin([2.,4.]).all()
    assert t.efficiency_store.eq(.9).all()
    assert t.observed_quantile_is_not_technical_power_rating.all()
    assert t.energy_mwh_assumed_not_source_measured.all()
    assert not t.observed_EENS_inferred.any()

def test_pypsa_storageunit_csv_has_required_fields(tmp_path):
    t=save(fixture(),tmp_path)
    assert len(list((tmp_path/"storageunit_csv").glob("*.csv")))==32
    file=tmp_path/"storageunit_csv"/(t.scenario_id.iloc[0]+".csv")
    input=pd.read_csv(file)
    assert set(input.columns)=={"ba","power_mw","energy_mwh",
             "efficiency_store","efficiency_dispatch","initial_soc_fraction"}
    assert input.ba.tolist()==["CISO"]

def test_uncertified_negative_source_or_null_rejected():
    a=fixture()
    a.loc[0,"charge_positive_magnitude_only_p95_mw"]=-2.
    with pytest.raises(ValueError,match="Invalid source"):
        scenario_matrix(a)

def test_false_claim_of_certified_power_rejected():
    a=fixture()
    a.loc[0,"certified_storage_power_rating_mw_inferred"]=True
    with pytest.raises(ValueError,match="Unjustified"):
        scenario_matrix(a)

def test_incomplete_source_days_rejected():
    a=fixture()
    a.loc[0,"source_points"]=2015
    with pytest.raises(ValueError,match="Incomplete"):
        scenario_matrix(a)
