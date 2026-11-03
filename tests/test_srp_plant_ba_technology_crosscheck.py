"""Source-fuel crosswalk tests use EIA-860-style generator fields."""
import pandas as pd
import pytest
from grid_resilience.srp_plant_ba_technology_crosscheck import classify

def fixture():
    roster=pd.DataFrame({
      "plant_id":["1","2","3","4","5","6"],
      "generator_id":["A","B","C","D","E","F"],
      "nameplate_capacity_mw":[100.,20.,50.,10.,30.,40.],
      "energy_source_1":["NG","SUN","NUC","MWH","NG","WAT"],
      "energy_source_2":["","","","","DFO",""],
      "multiple_fuels":["N","N","N","N","Y","N"],
      "prime_mover":["CT","PV","ST","BA","CT","PS"],
      "plant_reported_ba":["SRP"]*6
    })
    reference=pd.DataFrame({"technology":["gas","solar","nuclear"],
         "nameplate_capacity_mw":[100.,20.,50.],
         "generator_count":[1,1,1]})
    return roster,reference

def test_matches_independent_reference_without_storage_or_multi_fuel():
    a,b=fixture()
    rows,diff,summary=classify(a,b)
    assert summary["matched_reference_counts_and_capacities"] is True
    assert summary["eligible_selected_generator_count"]==3
    assert summary["eligible_selected_nameplate_mw"]==170
    assert summary["roster_class_counts"]["storage_excluded"]==1
    assert summary["roster_class_counts"]["unmapped_primary_energy_source"]==1
    assert summary["roster_class_counts"]["multifuel_or_secondary_fuel"]==1
    assert summary["roster_class_capacity_mw"]["included"]==170.
    assert summary["roster_class_capacity_mw"]["storage_excluded"]==40.
    assert summary["roster_class_capacity_mw"]["unmapped_primary_energy_source"]==10.
    assert summary["roster_class_capacity_mw"]["multifuel_or_secondary_fuel"]==30.
    assert sum(x["generator_count"] for x in summary["roster_class_details"].values())==6
    assert sum(x["nameplate_mw"] for x in summary["roster_class_details"].values())==250.


def test_reference_mismatch_is_observable_not_hidden():
    a,b=fixture()
    b.loc[0,"nameplate_capacity_mw"]=101
    _,diff,summary=classify(a,b)
    assert summary["matched_reference_counts_and_capacities"] is False
    assert abs(diff.nameplate_difference_mw).sum()==1

def test_duplicate_generator_ids_fail_closed():
    a,b=fixture()
    a.loc[1,["plant_id","generator_id"]]=["1","A"]
    with pytest.raises(ValueError,match="Duplicate roster"):
        classify(a,b)

def test_nonfinite_capacity_fails():
    a,b=fixture()
    a.loc[0,"nameplate_capacity_mw"]=float("inf")
    with pytest.raises(ValueError,match="Invalid source"):
        classify(a,b)

def test_mixed_ba_roster_fails_before_aggregation():
    a,b=fixture()
    a.loc[1,"plant_reported_ba"]="AZPS"
    with pytest.raises(ValueError,match="outside the requested BA"):
        classify(a,b)

def test_wrong_reference_ba_fails():
    a,b=fixture()
    b["ba"]="SRP"
    b.loc[1,"ba"]="AZPS"
    with pytest.raises(ValueError,match="another BA"):
        classify(a,b)

def test_normalized_duplicate_plant_identity_fails():
    a,b=fixture()
    a.loc[1,["plant_id","generator_id"]]=["0001","A"]
    with pytest.raises(ValueError,match="Duplicate roster"):
        classify(a,b)

def test_missing_roster_ba_fails():
    a,b=fixture()
    a.loc[0,"plant_reported_ba"]=None
    with pytest.raises(ValueError,match="Missing roster identity"):
        classify(a,b)

@pytest.mark.parametrize("bad_value",[float("nan"),float("inf"),-1.0])
def test_invalid_reference_capacity_fails(bad_value):
    a,b=fixture()
    b.loc[0,"nameplate_capacity_mw"]=bad_value
    with pytest.raises(ValueError,match="independent reference"):
        classify(a,b)

def test_noninteger_reference_counts_fail():
    a,b=fixture()
    b["generator_count"]=b["generator_count"].astype(float)
    b.loc[0,"generator_count"]=1.5
    with pytest.raises(ValueError,match="Noninteger reference"):
        classify(a,b)

def test_empty_reference_fails():
    a,b=fixture()
    with pytest.raises(ValueError,match="Empty independent reference"):
        classify(a,b.iloc[:0])

def test_valid_reference_still_matches_after_strict_checks():
    a,b=fixture()
    _,comparison,summary=classify(a,b)
    assert summary["matched_reference_counts_and_capacities"] is True
    assert comparison.nameplate_difference_mw.abs().max()<1e-8

def test_source_roster_capacity_conserves_across_all_classes():
    a,b=fixture()
    rows,comparison,summary=classify(a,b)
    assert sum(summary["roster_class_counts"].values())==len(rows)
    assert abs(sum(summary["roster_class_capacity_mw"].values())-
               rows.nameplate_capacity_mw.sum())<1e-8
    assert summary["roster_class_details"]["included"]["generator_count"]==3

def test_reference_mismatch_does_not_change_source_conservation():
    a,b=fixture()
    b.loc[0,"nameplate_capacity_mw"]=999.
    rows,_,summary=classify(a,b)
    assert summary["matched_reference_counts_and_capacities"] is False
    assert sum(summary["roster_class_counts"].values())==len(rows)
    assert abs(sum(summary["roster_class_capacity_mw"].values())-
               rows.nameplate_capacity_mw.sum())<1e-8
