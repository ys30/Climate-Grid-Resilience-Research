import numpy as np
import pandas as pd
import pytest
from grid_resilience.paperc_2024_hour_matched_model_scope import audit

BAS=("AZPS","BPAT","CISO","SRP")


def fixture():
    stamps=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    rows=[]
    modeled=[]
    for i,t in enumerate(stamps):
        for ba in BAS:
            rows.append({"timestamp":t.isoformat(),"ba":ba,
                         "partition":"2024_Jan_Jun" if i<7 else "2024_Jul_Dec",
                         "net_mwh":100.0,"gas_mwh":40.0})
            modeled.append({"timestamp":t.isoformat(),"ba":ba,
                            "scenario":"baseline","technology":"generic_thermal_proxy",
                            "generation_mwh":30.0})
    return pd.DataFrame(rows),pd.DataFrame(modeled)


def test_168h_four_ba_hour_keys_and_source_scope():
    detail,summary=audit(*fixture())
    assert len(detail)==672 and len(summary)==4
    assert summary.matched_hours.eq(168).all()
    assert summary.eia930_raw_ba_natural_gas_mwh.eq(6720).all()
    assert summary.model_generic_thermal_proxy_baseline_mwh.eq(5040).all()
    assert summary.descriptive_signed_proxy_minus_gas_mwh.eq(-1680).all()
    assert not summary.population_and_technology_equivalence_verified.any()


def test_missing_model_hour_fails():
    a,b=fixture()
    with pytest.raises(ValueError,match="Model 672"):
        audit(a,b.iloc[:-1])


def test_missing_source_gas_fails_without_imputation():
    a,b=fixture()
    a.loc[0,"gas_mwh"]=np.nan
    with pytest.raises(ValueError,match="Missing source-observed"):
        audit(a,b)


def test_source_partition_mismatch_fails():
    a,b=fixture()
    a.loc[0,"partition"]="2024_Jul_Dec"
    with pytest.raises(ValueError,match="partition"):
        audit(a,b)


def test_model_keys_cannot_fake_complete_hours():
    a,b=fixture()
    b.loc[0,"timestamp"]=b.loc[4,"timestamp"]
    with pytest.raises(ValueError,match="Model 672"):
        audit(a,b)
