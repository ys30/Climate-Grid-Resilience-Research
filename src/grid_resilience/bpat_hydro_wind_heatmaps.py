"""Create auditable heatmap data and figures for crossed BPAT hydro/wind runs."""
import argparse,json
from pathlib import Path
import pandas as pd

def summarize(source,output):
    df=pd.read_csv(source)
    energies=[0.05,0.25,0.50,1.0]
    powers=[0.10,0.20,0.30]
    if len(df)!=12 or df.duplicated(["hydro_budget_fraction","hydro_power_fraction"]).any():
        raise ValueError("Expected precisely 12 independent hydro configurations")
    if set(zip(df.hydro_budget_fraction.round(5),df.hydro_power_fraction.round(5)))!=set((e,p) for e in energies for p in powers):
        raise ValueError("Missing hydro scenario grid cells")
    if not {"era5","replay","era5_minus_replay_shortfall_mwh"}.issubset(df):
        raise ValueError("Missing wind scenario results")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    scenarios={"era5_shortfall_gwh":df.era5/1000,"replay_shortfall_gwh":df.replay/1000,
               "era5_minus_replay_shortfall_gwh":df.era5_minus_replay_shortfall_mwh/1000}
    for name,values in scenarios.items():
        d=df[["hydro_budget_fraction","hydro_power_fraction"]].copy()
        d["value_gwh"]=values
        m=d.pivot(index="hydro_budget_fraction",columns="hydro_power_fraction",values="value_gwh").sort_index().sort_index(axis=1)
        m.to_csv(out/(name+"_matrix.csv"))
    # One consistent scale for comparing both shortfall heatmaps; delta has its own range.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    max_short=float(max(df.era5.max(),df.replay.max())/1000)
    for name in scenarios:
        table=pd.read_csv(out/(name+"_matrix.csv"),index_col=0)
        fig,ax=plt.subplots(figsize=(7,4.7))
        vmax=max_short if not name.startswith("era5_minus") else None
        im=ax.imshow(table.to_numpy(),origin="lower",aspect="auto",vmin=0 if vmax is not None else None,vmax=vmax)
        ax.set_xticks(range(3),[f"{p:.0%}" for p in powers])
        ax.set_yticks(range(4),[f"{e:.0%}" for e in energies])
        ax.set_xlabel("Hourly hydro power availability (assumed)")
        ax.set_ylabel("Monthly hydro energy budget fraction (assumed)")
        ax.set_title(name.replace("_"," ")+" (GWh)")
        fig.colorbar(im,ax=ax,label="Modeled shortfall (GWh)")
        fig.tight_layout();fig.savefig(out/(name+".png"),dpi=160);plt.close(fig)
    manifest={"paired_scenarios":12,"pypsa_solves":24,
              "plots":["era5_shortfall_gwh.png","replay_shortfall_gwh.png","era5_minus_replay_shortfall_gwh.png"],
              "comparable_era5_replay_color_scale":True,
              "historical_outage_claim":False,
              "hydro_constraints_observed":False}
    (out/"crossed_hydro_wind_plot_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(summarize(a.input,a.output),indent=2))
if __name__=="__main__":main()
