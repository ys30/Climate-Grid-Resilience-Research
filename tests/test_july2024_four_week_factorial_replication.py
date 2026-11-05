import numpy as np
import pandas as pd
import pytest
from grid_resilience.july2024_four_week_factorial_replication import summarize

def results():
    rows=[]
    for wk in range(1,5):
        for net in ("isolated","links_10pct"):
            for ba in ("AZPS","BPAT","CISO","SRP"):
                for case,val in (("baseline",100.),("heat_only",110.),
                                 ("wind_only",120.),("heat_wind",150.)):
                    rows.append({
                        "event_id":f"JULY2024_WEEK_{wk}",
                        "network_variant":net,"ba":ba,"scenario":case,
                        "unserved_energy_mwh":val+wk,
                        "shortage_hours":2,"peak_shortfall_mw":2.})
    return pd.DataFrame(rows)

def test_matched_four_factorial_contrast_exact_reconciliation():
    by_ba,comp=summarize(results())
    assert len(by_ba)==40 and len(comp)==4
    assert by_ba.loc[by_ba.ba.eq("SYSTEM"),"modeled_factorial_interaction_mwh"].eq(80.).all()
    assert comp.links_minus_isolated_interaction_mwh.eq(0).all()

def test_missing_one_scenario_fails():
    g=results().iloc[:-1]
    with pytest.raises(ValueError,match="factorial"):
        summarize(g)

def test_duplicate_legacy_ba_rows_fail():
    g=results()
    with pytest.raises(ValueError,match="Duplicate"):
        summarize(pd.concat([g,g.iloc[[0]]],ignore_index=True))

def test_fails_on_nonfinite_solver_shortage():
    g=results()
    g.loc[0,"unserved_energy_mwh"]=np.nan
    with pytest.raises(ValueError,match="Nonfinite"):
        summarize(g)

def test_16_scenarios_not_sufficient_without_four_real_weeks():
    g=results()
    with pytest.raises(ValueError,match="four distinct"):
        summarize(g.loc[g.event_id.eq("JULY2024_WEEK_1")])
