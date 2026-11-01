import pandas as pd
from grid_resilience.feb2024_capacity_margin_audit import audit

def test_peak_break_even_availability_and_margin(tmp_path):
    demand=tmp_path/"d.csv";capacity=tmp_path/"c.csv";shortfall=tmp_path/"s.csv"
    pd.DataFrame([{"ba":"AZPS","demand_mw":100},{"ba":"AZPS","demand_mw":80}]).to_csv(demand,index=False)
    pd.DataFrame([{"ba":"AZPS","capacity_mw":125}]).to_csv(capacity,index=False)
    pd.DataFrame([{"ba":"AZPS","scenario":"s70","availability_fraction_assumed":0.7,"unserved_energy_mwh":4},
                  {"ba":"AZPS","scenario":"s90","availability_fraction_assumed":0.9,"unserved_energy_mwh":0}]).to_csv(shortfall,index=False)
    audit(demand,capacity,shortfall,tmp_path/"out")
    a=pd.read_csv(tmp_path/"out"/"screening_ba_capacity_margin.csv")
    assert set(a.peak_break_even_availability_fraction)=={0.8}
    assert a.loc[a.scenario=="s70","availability_exceeds_peak_break_even"].iloc[0]==False
    assert a.loc[a.scenario=="s90","availability_exceeds_peak_break_even"].iloc[0]==True
