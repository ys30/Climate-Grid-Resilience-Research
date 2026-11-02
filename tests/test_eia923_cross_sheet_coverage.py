import pandas as pd
import pytest
from grid_resilience.eia923_cross_sheet_coverage import audit

def inputs():
    p4=pd.DataFrame({"plant_id":["0007","8"],"generator_id":["A","B"],"prime_mover":["ST","CT"],"reported_ba":["SRP","AZPS"],"period":["2024-01"]*2})
    hy=pd.DataFrame({"plant_id":["7"],"prime_mover":["HY"],"reported_ba":["SRP"],"period":["2024-01"]})
    ps=pd.DataFrame({"plant_id":["9"],"prime_mover":["PS"],"reported_ba":["SRP"],"period":["2024-01"]})
    return p4,hy,ps

def test_plant_id_normalization_and_distinct_source_grain():
    r=audit(*inputs())
    assert r["page1_plants_also_in_page4"]==1
    assert not r["full_fleet_crosswalk_certified"]

def test_duplicate_generator_month_fails():
    p4,hy,ps=inputs()
    with pytest.raises(ValueError,match="Duplicate Page 4"):
        audit(pd.concat([p4,p4.iloc[[0]]]),hy,ps)

def test_wrong_hydro_technology_fails():
    p4,hy,ps=inputs()
    hy.loc[0,"prime_mover"]="PS"
    with pytest.raises(ValueError,match="technology mismatch"):
        audit(p4,hy,ps)
