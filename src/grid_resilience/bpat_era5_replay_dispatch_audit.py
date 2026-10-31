"""Audit the matched PyPSA wind substitutions and their dispatch consequences."""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(root):
    p=Path(root)
    availability=pd.read_csv(p/"era5_29site_wind_availability.csv")
    replay=pd.read_csv(p/"observed_wind_replay_availability.csv")
    keys=["timestamp","ba","technology"]
    aligned=availability.merge(replay,on=keys,suffixes=("_era5","_replay"),validate="one_to_one")
    if len(aligned)!=len(availability) or len(aligned)!=len(replay):
        raise AssertionError("Missing model BA-hour-technology availability cells")
    changed=~aligned.availability_pu_era5.eq(aligned.availability_pu_replay)
    if not (aligned.loc[changed,"ba"].eq("BPAT")&aligned.loc[changed,"technology"].eq("wind")).all():
        raise AssertionError("Non-BPAT wind scenario configuration changed")
    rows=[]
    for scenario,subdir in [("era5","era5_wind_dispatch"),("replay","observed_wind_dispatch")]:
        gen=pd.read_csv(p/subdir/"generation_hourly.csv")
        wind=gen[(gen.ba=="BPAT")&(gen.technology=="wind")]
        if len(wind)!=696:raise AssertionError("BPAT wind generation hours incomplete")
        rows.append({"scenario":scenario,"wind_dispatched_mwh":float(wind.generation_mwh.sum()),
                     "wind_max_hourly_mwh":float(wind.generation_mwh.max())})
    summary=pd.DataFrame(rows)
    short=pd.read_csv(p/"bpat_era5_pypsa_conditional_shortfall.csv")
    bpat=short.loc[short.ba=="BPAT"].iloc[0]
    result={"changed_availability_cells":int(changed.sum()),"all_changed_cells_are_bpat_wind":True,
        "era5_wind_dispatched_mwh":float(summary.loc[summary.scenario=="era5","wind_dispatched_mwh"].iloc[0]),
        "replay_wind_dispatched_mwh":float(summary.loc[summary.scenario=="replay","wind_dispatched_mwh"].iloc[0]),
        "era5_minus_replay_shortfall_mwh":float(bpat.era5_minus_observed_replay_shortfall_mwh),
        "no_real_historical_shortfall_claim":True}
    (p/"bpat_era5_vs_replay_dispatch_audit.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--root",required=True)
    a=parser.parse_args();print(json.dumps(audit(a.root),indent=2))
if __name__=="__main__":main()
