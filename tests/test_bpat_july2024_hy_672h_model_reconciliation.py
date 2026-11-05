import numpy as np
import pandas as pd
import pytest
from grid_resilience.bpat_july2024_hy_672h_model_reconciliation import summarize

def data():
    rows=[];old=[];dispatch=[]
    specs=[("HY_0MW_0MWh",0.,0.),
           ("HY_500MW_598947MWh",60.,50.),
           ("HY_2000MW_598947MWh",150.,100.),
           ("HY_2000MW_1497369MWh",200.,120.)]
    for label,gross,avoided in specs:
        for case in ("baseline","heat_only","wind_only","heat_wind"):
            for wk in range(1,5):
                dispatch.append({"resource_scenario":label,"scenario":case,
                       "week":wk,"hydro_dispatched_mwh":gross,
                       "hydro_peak_dispatch_mw":gross/168})
                for ba in ("AZPS","BPAT","CISO","SRP"):
                    val=300.+int(ba=="BPAT")*100.-int(ba=="BPAT")*avoided
                    rows.append({"resource_scenario":label,"scenario":case,"week":wk,
                                 "ba":ba,"modeled_unserved_mwh":val})
                    if label=="HY_0MW_0MWh":
                        old.append({"event_id":f"JULY2024_WEEK_{wk}",
                                    "network_variant":"isolated","scenario":case,
                                    "ba":ba,"unserved_energy_mwh":val})
    return pd.DataFrame(rows),pd.DataFrame(dispatch),pd.DataFrame(old)

def test_all_four_week_original_controls_identical():
    x,y,z,m=summarize(*data())
    assert len(x)==16 and len(y)==4 and len(z)==64
    assert m["max_absolute_hydro_free_control_replay_error_mwh"]==0.
    assert not m["observed_historical_outages_or_eens"]
    assert y.loc[y.resource_scenario.eq("HY_0MW_0MWh"),
                 "baseline_shortage_reduction_mwh"].iloc[0]==0

def test_false_source_original_replay_rejected():
    f,h,o=data()
    o.loc[0,"unserved_energy_mwh"]+=1
    with pytest.raises(ValueError,match="mismatch"):
        summarize(f,h,o)

def test_missing_hourly_cohort_scenario_fails():
    f,h,o=data()
    with pytest.raises(ValueError,match="Incomplete hydro"):
        summarize(f.iloc[:-1],h,o)

def test_energy_reduction_cannot_exceed_generated_hy():
    f,h,o=data()
    h.loc[h.resource_scenario.eq("HY_2000MW_598947MWh"),"hydro_dispatched_mwh"]=0
    with pytest.raises(ValueError,match="exceeds hydro"):
        summarize(f,h,o)
