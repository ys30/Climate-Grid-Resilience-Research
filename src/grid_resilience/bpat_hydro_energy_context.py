"""Audit monthly observed hydro+pumped energy versus model demand and shortage.

This is an energy accounting comparison ONLY. It does not equate reported
net production with firm, dispatchable hydropower or add energy constraints.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(observed_hourly,demand_csv,shortfall_csv,output):
    h=pd.read_csv(observed_hourly);d=pd.read_csv(demand_csv);s=pd.read_csv(shortfall_csv)
    required={"timestamp","reported_hydro_and_pumped_net_mw"}
    if not required.issubset(h):raise ValueError("Missing hourly observed hydro")
    if h.timestamp.duplicated().any():raise ValueError("Duplicate hydro hour")
    bp=d[d.ba=="BPAT"].copy()
    if bp.timestamp.duplicated().any() or len(bp)!=len(h):raise ValueError("BPAT demand hour mismatch")
    matched=bp.merge(h,on="timestamp",how="outer",validate="one_to_one",indicator=True)
    if not matched._merge.eq("both").all():raise ValueError("Demand and hydro hourly keys differ")
    short=s[s.ba=="BPAT"]
    if len(short)!=1:raise ValueError("BPAT shortfall absent or duplicated")
    hydro=float(matched.reported_hydro_and_pumped_net_mw.sum())
    demand=float(matched.demand_mw.sum())
    shortage=float(short.iloc[0].unserved_energy_mwh)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    m={"month":"2024-02","reported_mixed_hydro_pumped_net_mwh":hydro,
       "reported_bpat_demand_mwh":demand,"isolated_no_hydro_model_shortfall_mwh":shortage,
       "mixed_reported_hydro_as_share_of_demand":hydro/demand,
       "model_shortfall_as_share_of_demand":shortage/demand,
       "observed_monthly_energy_is_not_firm_dispatch_budget":True,
       "observed_hydro_pumped_hourly_is_not_model_generation_profile":True,
       "hydro_energy_constraint_implemented":False,
       "historical_calibration_certified":False,
       "warning":"Monthly EIA-930 observed hydro+pumped net output is descriptive; it does not certify incremental hydropower, hourly feasibility, pumped storage state of charge or water availability."}
    (out/"bpat_hydro_energy_context.json").write_text(json.dumps(m,indent=2)+"\n")
    return m
def main():
    p=argparse.ArgumentParser()
    for k in ("observed-hourly","demand","shortfall","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    print(json.dumps(audit(a.observed_hourly,a.demand,a.shortfall,a.output),indent=2))
if __name__=="__main__":main()
