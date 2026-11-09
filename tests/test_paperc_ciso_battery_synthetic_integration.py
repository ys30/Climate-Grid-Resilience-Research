import pandas as pd
import pytest
from grid_resilience.paperc_ciso_battery_synthetic_integration import verify_config

def test_counterfactual_pypsa_single_csv_schema(tmp_path):
    f=tmp_path/"case.csv"
    pd.DataFrame([{"ba":"CISO","power_mw":4930.,"energy_mwh":9860.,
        "efficiency_store":.9,"efficiency_dispatch":.9,"initial_soc_fraction":.25}]
        ).to_csv(f,index=False)
    x=verify_config(f)
    assert x.power_mw==4930.
    assert x.initial_soc_fraction==.25

def test_wrong_storage_duration_is_not_silently_accepted(tmp_path):
    f=tmp_path/"bad.csv"
    pd.DataFrame([{"ba":"CISO","power_mw":4930.,"energy_mwh":100.,
        "efficiency_store":.9,"efficiency_dispatch":.9,"initial_soc_fraction":.25}]
        ).to_csv(f,index=False)
    with pytest.raises(ValueError,match="candidate"):
        verify_config(f)
