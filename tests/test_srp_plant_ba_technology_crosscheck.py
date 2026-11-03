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
