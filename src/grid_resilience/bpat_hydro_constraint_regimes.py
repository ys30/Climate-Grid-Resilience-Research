"""Identify binding-pattern evidence from the crossed hydro × wind sensitivity grid.

Finite differences describe outcomes; they do not prove dual-variable binding.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def analyze(source,output):
    d=pd.read_csv(source)
    if len(d)!=12 or d.duplicated(["hydro_budget_fraction","hydro_power_fraction"]).any():
        raise ValueError("Need exactly 12 unique hydro grid cells")
    d=d.sort_values(["hydro_budget_fraction","hydro_power_fraction"]).reset_index(drop=True)
    e=sorted(d.hydro_budget_fraction.unique())
    p=sorted(d.hydro_power_fraction.unique())
    if len(e)!=4 or len(p)!=3:raise ValueError("Unexpected grid shape")
    rows=[]
    for case in ["era5","replay"]:
        grid=d.pivot(index="hydro_budget_fraction",columns="hydro_power_fraction",values=case)
        for energy in e:
            for power in p:
                val=float(grid.loc[energy,power])
                more_e=float(grid.loc[e[e.index(energy)+1],power]) if energy!=e[-1] else None
                more_p=float(grid.loc[energy,p[p.index(power)+1]]) if power!=p[-1] else None
                de=val-more_e if more_e is not None else None
                dp=val-more_p if more_p is not None else None
                if de is not None and de < -1e-3:raise AssertionError("Shortage increases with hydro energy")
                if dp is not None and dp < -1e-3:raise AssertionError("Shortage increases with hydro power")
                rows.append({"wind_source":case,"hydro_energy_fraction":energy,"hydro_power_fraction":power,
                             "shortfall_gwh":val/1000,
                             "incremental_energy_budget_benefit_gwh":de/1000 if de is not None else None,
                             "incremental_power_benefit_gwh":dp/1000 if dp is not None else None,
                             "zero_shortfall":val<1e-6})
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    result=pd.DataFrame(rows)
    result.to_csv(out/"hydro_constraint_finite_differences.csv",index=False)
    meta={"grid_cells":12,"wind_scenario_evaluations":24,
          "minimum_era5_minus_replay_shortfall_gwh":float(d.era5_minus_replay_shortfall_mwh.min()/1000),
          "maximum_era5_minus_replay_shortfall_gwh":float(d.era5_minus_replay_shortfall_mwh.max()/1000),
          "zero_shortfall_cells_era5":int((d.era5<1e-6).sum()),
          "zero_shortfall_cells_replay":int((d.replay<1e-6).sum()),
          "interpretation":"Forward finite differences measure effects of changing a hypothetical constraint; not solver shadow prices or physical binding proof.",
          "historical_calibration_completed":False}
    (out/"hydro_constraint_regimes_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    return meta

def main():
    a=argparse.ArgumentParser();a.add_argument("--input",required=True);a.add_argument("--output",required=True)
    x=a.parse_args();print(json.dumps(analyze(x.input,x.output),indent=2))
if __name__=="__main__":main()
