import pandas as pd
import pytest
from grid_resilience.bpat_july2024_intertemporal_hy_pypsa import validate_source
from grid_resilience.bpat_july2024_hy_ps_soc_pypsa import SETTINGS, HY_POWER, HY_BUDGET

def test_ps_scenarios_are_distinct_and_closed_initial_state():
    assert SETTINGS==((0.,0.,1.),(500.,2000.,.80),(1000.,4000.,.80),(1000.,4000.,.90))
    assert HY_POWER==2000. and HY_BUDGET==598947.6

def test_genuine_source_validation_reused():
    hours=pd.date_range("2024-07-01T00:00:00Z",periods=672,freq="h")
    rows=[(t,b) for t in hours for b in ("AZPS","BPAT","CISO","SRP")]
    d=pd.DataFrame(rows,columns=["timestamp","ba"]).assign(demand_mw=1000.)
    w=d[["timestamp","ba"]].assign(temperature_c=32.,wind_availability=.4)
    c=pd.DataFrame({"ba":["AZPS","BPAT","CISO","SRP"],"gas_mw":[1000]*4,
       "wind_mw":[100]*4,"capacity_source":["GENERIC_THERMAL_PROXY"]*4})
    assert len(validate_source(d,w,c,5989476.)[3])==672
    with pytest.raises(ValueError):
        validate_source(d.iloc[:-1],w,c,5989476.)
