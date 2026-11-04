import pandas as pd
import pytest

from grid_resilience.srp_thermal_plant_weather_sites import select


def example():
    g=pd.DataFrame({
        "plant_id":["01","1","2","3","4","5"],
        "generator_id":["A","B","C","D","E","F"],
        "energy_source_1":["NG","NG","SUB","NG","SUB","NG"],
        "prime_mover":["GT","CT","ST","GT","ST","PS"],
        "nameplate_capacity_mw":[100.,40.,80.,30.,20.,500.]})
    p=pd.DataFrame({
        "plant_id":["1","2","3","4","5"],
        "plant_reported_ba":["SRP","SRP","SRP","SRP","SRP"],
        "latitude":[33.,34.,None,35.,34.],
        "longitude":[-111.,-112.,None,-110.,-113.]})
    return g,p


def test_deduplicated_generator_grain_and_missing_coordinates_in_denominator():
    g,p=example()
    selected,population,m=select(g,p,max_plants=1)
    gas=m["coverage_by_technology"]["gas"]
    coal=m["coverage_by_technology"]["coal"]
    assert gas["source_generator_count"]==3
    assert gas["source_nameplate_mw"]==170.
    assert gas["coordinate_covered_mw"]==140.
    assert gas["selected_nameplate_mw"]==140.
    assert coal["source_nameplate_mw"]==100.
    assert coal["selected_nameplate_mw"]==80.
    assert len(selected)==2
    assert (population.valid_coordinate==False).sum()==1
    assert not m["annual_plant_ba_is_dispatch_right"]
    assert not m["temperature_exposure_is_not_plant_derating"] is False


def test_duplicate_generator_identity_rejected():
    g,p=example()
    with pytest.raises(ValueError,match="Duplicate"):
        select(pd.concat([g,g.iloc[[0]]],ignore_index=True),p)


def test_unexpected_storage_source_excluded():
    g,p=example()
    sites,all_plants,m=select(g,p)
    assert 500. not in all_plants.nameplate_mw.tolist()
    assert all_plants.nameplate_mw.sum()==270.


def test_no_valid_coordinate_fails():
    g,p=example()
    p["latitude"]=None
    with pytest.raises(ValueError,match="No geolocated"):
        select(g,p)
