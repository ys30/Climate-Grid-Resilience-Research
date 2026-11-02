import pandas as pd
import pytest
from grid_resilience.page4_fuel_descriptive_comparison import compare

def test_exact_identity_with_both_fuel_columns():
    page4=pd.DataFrame([
      dict(plant_id="0001",generator_id="A",reported_ba="SRP",period="2024-01",generation_mwh=100,energy_source_1="OTHER"),
      dict(plant_id="1",generator_id="B",reported_ba="SRP",period="2024-01",generation_mwh=0,energy_source_1="OTHER")])
    review=pd.DataFrame([
      dict(plant_id="1",generator_id="A",screening_candidate=True,energy_source_1="NG"),
      dict(plant_id="1",generator_id="B",screening_candidate=False,energy_source_1="SUB")])
    model=pd.DataFrame([dict(ba="SRP",technology="NG",modeled_generation_mwh=120)])
    result,meta=compare(page4,review,model)
    assert len(result)==1
    assert result.iloc[0].fuel=="NG"
    assert result.iloc[0].page4_matched_net_mwh==100
    assert meta["page4_observed_total_mwh"]==100
    assert meta["calibration_certified"] is False

def test_missing_inventoried_fuel_rejected():
    page4=pd.DataFrame([dict(plant_id="1",generator_id="A",reported_ba="SRP",period="2024-01",generation_mwh=12)])
    review=pd.DataFrame([dict(plant_id="1",generator_id="A",screening_candidate=True,energy_source_1=None)])
    model=pd.DataFrame([dict(ba="SRP",technology="NG",modeled_generation_mwh=20)])
    with pytest.raises(ValueError,match="Missing fuel"):
      compare(page4,review,model)
