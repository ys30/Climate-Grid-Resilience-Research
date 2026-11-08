"""Supplementary figure: EIA930A roster identity-matched fraction of cited EIA860M nameplate.

Shows *administrative identity matching* by BA and technology, not an annual
physical coverage ratio, dispatch, or grid reliability.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
TECH=("natural_gas","wind","solar","hydro_nonpumped","pumped_hydro",
      "nuclear","coal","battery_storage","other")
LABELS=("Gas","Wind","Solar","Hydro","Pumped hydro","Nuclear","Coal","Battery","Other")


def audited_matrix(by_year,manifests):
    if set(by_year)!={2023,2024} or {int(m["year"]) for m in manifests}!={2023,2024}:
        raise ValueError("Both source-year manifest records required")
    outputs={}
    for year,frame in by_year.items():
        meta=next(x for x in manifests if x["year"]==year)
        required={"ba","technology_class","monthly_operating_nameplate_mw",
                  "matched_930a_monthly_nameplate_mw","monthly_roster_nameplate_fraction_matched",
                  "real_hourly_available_capacity_verified"}
        if not required.issubset(frame) or len(frame)!=52 or (
            frame.duplicated(["ba","technology_class"]).any()):
            raise ValueError("Four BA × 13 technology source cohort not intact")
        if set(frame.ba)!=set(BAS) or frame.real_hourly_available_capacity_verified.any():
            raise ValueError("Source/physical coverage gate failed")
        denom=frame.monthly_operating_nameplate_mw.sum()
        numer=frame.matched_930a_monthly_nameplate_mw.sum()
        if not np.isclose(denom,meta["monthly_total_nameplate_mw"],atol=1e-4):
            raise ValueError("Original monthly roster denominator is inconsistent")
        if not np.isclose(numer,meta["matched_nameplate_mw"],atol=1e-4):
            raise ValueError("Matched monthly source nameplate inconsistent")
        mat=np.full((len(BAS),len(TECH)),np.nan)
        for i,ba in enumerate(BAS):
            for j,tech in enumerate(TECH):
                r=frame[(frame.ba==ba)&(frame.technology_class==tech)].iloc[0]
                if r.monthly_operating_nameplate_mw>0:
                    expected=r.matched_930a_monthly_nameplate_mw/r.monthly_operating_nameplate_mw
                    if not np.isclose(r.monthly_roster_nameplate_fraction_matched,expected,atol=1e-6):
                        raise ValueError("Unverified class coverage fraction")
                    mat[i,j]=expected
        outputs[year]=mat
    return outputs


def save(matrices,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dest=Path(out);dest.mkdir(parents=True,exist_ok=True)
    cmap=plt.get_cmap("viridis").copy()
    cmap.set_bad("#e6e6e6")
    fig,axes=plt.subplots(2,1,figsize=(10,6.7),layout="constrained")
    for year,ax in zip((2023,2024),axes):
        m=matrices[year]
        im=ax.imshow(m,vmin=0,vmax=1,cmap=cmap,aspect="auto")
        ax.set_xticks(np.arange(len(TECH)),LABELS,rotation=20,ha="right")
        ax.set_yticks(np.arange(len(BAS)),BAS)
        ax.set_title(f"{year} EIA-930A cohort vs cited 2025 EIA-860M monthly roster",loc="left")
        for i in range(len(BAS)):
            for j in range(len(TECH)):
                val=m[i,j]
                ax.text(j,i,"N/A" if np.isnan(val) else f"{100*val:.0f}%",
                        ha="center",va="center",fontsize=8,
                        color="white" if np.isfinite(val) and val<.40 else "black")
    fig.colorbar(im,ax=axes,label="EIA-930A exact-ID matched nameplate / EIA-860M Operating nameplate",
                 fraction=.026,pad=.02)
    fig.text(.5,-.015,"N/A: no positive monthly nameplate denominator; source roster matching ONLY. "
             "Not 2023/2024 hourly available MW, physical generation share, or calibrated EENS.",
             ha="center",fontsize=8,wrap=True)
    for ext in ("png","pdf"):
        fig.savefig(dest/f"fig_paperc_ba_technology_source_vintage_nameplate.{ext}",
                    dpi=230,bbox_inches="tight")
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    for year in (2023,2024):
        p.add_argument("--source"+str(year),required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    frames={year:pd.read_csv(getattr(a,"source"+str(year))) for year in (2023,2024)}
    meta=json.loads(Path(a.manifest).read_text())
    matrices=audited_matrix(frames,meta)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    save(matrices,out)
    for year in (2023,2024):
        pd.DataFrame(matrices[year],index=BAS,columns=TECH).to_csv(
            out/f"source_only_technology_nameplate_matching_fraction_{year}.csv")
    (out/"source_scoped_figure_manifest.json").write_text(json.dumps({
        "years":[2023,2024],
        "source_unit":"EIA860M 2025 preliminary monthly Operating nameplate MW",
        "eia930a_source_vintage_hours_comparable":False,
        "physical_adequacy_or_EENS_calibrated":False
    },indent=2)+"\n")


if __name__=="__main__":
    main()
