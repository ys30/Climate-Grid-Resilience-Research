import numpy as np
import pandas as pd
import pytest
from grid_resilience.july2024_eia930_demand_hour_lag_diagnostic import audit

def example():
    t=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    d=pd.DataFrame([{"timestamp":ts,"ba":ba,"demand_mw":5000+100*np.sin(i*.1)+i}
        for ba in ("AZPS","BPAT","CISO","SRP") for i,ts in enumerate(t)])
    return d


def test_identical_values_best_at_zero_shift():
    d=example()
    all_lags,best,meta=audit(d,d.copy())
    assert len(all_lags)==20 and len(best)==4
    assert best.old_source_timestamp_shift_hours.eq(0).all()
    assert best.demand_mae_mw.eq(0).all()
    assert not meta["model_physical_calibration_or_historical_eens_claimed"]


def test_source_hour_convention_shift_recovered_without_padding():
    d=example()
    new=d.copy()
    for ba in new.ba.unique():
        idx=new.index[new.ba.eq(ba)]
        new.loc[idx,"demand_mw"]=np.roll(new.loc[idx,"demand_mw"].to_numpy(),1)
    _,best,_=audit(d,new)
    assert best.old_source_timestamp_shift_hours.eq(1).all()
    assert best.overlapping_real_hour_pairs.eq(167).all()
    assert best.demand_mae_mw.lt(1e-8).all()


def test_duplicate_observations_rejected():
    d=example()
    with pytest.raises(ValueError,match="Duplicated"):
        audit(pd.concat([d,d.iloc[[0]]]),d)
