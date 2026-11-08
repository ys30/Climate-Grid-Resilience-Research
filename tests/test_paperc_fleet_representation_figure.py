import pandas as pd
import pytest
from grid_resilience.paperc_fleet_representation_figure import compare_models


def data():
    frozen=pd.DataFrame([{"network_variant":v,
         "july2023_interaction_model_mwh":100.,
         "july2024_interaction_model_mwh":200.,
         "frozen_2024_partial_fleet_used_in_2023":True,
         "real_grid_calibration":False,"historical_eens":False}
         for v in ("isolated","links_10pct")])
    annual=pd.DataFrame([{"source_year":year,"variant":v,
         "interaction_model_mwh":300.,
         "year_specific_eia860_nameplate_used":True,
         "all_historical_generation_fleet_calibrated":False,
         "historical_eens_or_outages_identified":False}
         for year in (2023,2024) for v in ("isolated","links_10pct")])
    return frozen,annual


def test_full_verified_grid_comparison():
    out=compare_models(*data())
    assert len(out)==4
    assert out.scenario_difference_mwh.tolist()==[200.,200.,100.,100.]
    assert out.model_only_not_historical_eens.all()


def test_missing_year_rejected():
    f,a=data()
    with pytest.raises(ValueError,match="Incomplete annual"):
        compare_models(f,a.iloc[:-1])


def test_calibration_claim_rejected():
    f,a=data()
    a["all_historical_generation_fleet_calibrated"]=True
    with pytest.raises(ValueError,match="Calibrated"):
        compare_models(f,a)
