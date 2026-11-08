"""Q1-ready descriptive roster version comparison: strictly source-verified generator ID rows.

The denominator is EIA-930A raw Schedule 2 reporting rows, NOT true fleet,
online capacity, peak supply, hourly generator coverage, or EENS.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
BAS=("AZPS","BPAT","CISO","SRP")


def calculate(annual_summaries,monthly_summaries,source_meta):
    if set(annual_summaries)!=set(monthly_summaries)!={2023,2024}:
        raise ValueError("Both 2023 and 2024 source-year comparisons required")
    if {int(m["year"]) for m in source_meta}!={2023,2024} or any(m["actual_hourly_dispatch_or_EENS_calibrated"] for m in source_meta):
        raise ValueError("Missing audited original-source monthly manifest")
    rows=[]
    for year in (2023,2024):
        annual=annual_summaries[year]
        monthly=monthly_summaries[year]
        for frame in (annual,monthly):
            if set(frame.ba)!=set(BAS) or len(frame)!=4:
                raise ValueError("Unmatched EIA-930A four BA source population")
        j=annual.merge(monthly,on=["year","ba"],validate="one_to_one",
                       suffixes=("_annual","_monthly"))
        if not j.eia930a_schedule2_rows.eq(j.source_rows).all():
            raise ValueError("Monthly-versus-annual source-row denominator differs")
        for r in j.itertuples():
            d=int(r.source_rows)
            if d<=0:raise ValueError("Invalid original source rows")
            rows.append({"year":year,"ba":r.ba,"eia930a_raw_schedule2_rows":d,
                "annual_same_ba_exact_rows":int(r.exact_identity_and_same_ba_rows),
                "monthly_same_ba_exact_rows":int(r.monthly_same_ba_matches),
                "annual_same_ba_exact_fraction":r.exact_identity_and_same_ba_rows/d,
                "monthly_same_ba_exact_fraction":r.monthly_same_ba_matches/d,
                "percentage_point_change_annual_to_monthly":
                     100*(r.monthly_same_ba_matches-r.exact_identity_and_same_ba_rows)/d,
                "source_rows_with_changed_match_class":int(r.vintage_match_category_changes),
                "source_row_denominator_not_physical_fleet":True,
                "hourly_available_mw_or_EENS_identified":False})
    return pd.DataFrame(rows)


def render(result,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    target=Path(out);target.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(9.0,4.7),layout="constrained")
    values=[result[(result.year.eq(year))&result.ba.eq(ba)].iloc[0]
            for year in (2023,2024) for ba in BAS]
    x=np.arange(len(values))
    old=np.array([z.annual_same_ba_exact_fraction for z in values])*100
    new=np.array([z.monthly_same_ba_exact_fraction for z in values])*100
    width=.38
    ax.bar(x-width/2,old,width,label="Annual EIA-860 Operable")
    ax.bar(x+width/2,new,width,label="Cited 2025 EIA-860M preliminary monthly")
    ax.set_xticks(x,[f"{z.ba}\n{z.year}" for z in values])
    ax.set_ylim(0,105)
    ax.set_ylabel("Exact same-BA generator ID rows / EIA-930A Schedule 2 rows (%)")
    ax.set_title("Reported-generator identity coverage differs by official inventory vintage",loc="left")
    ax.legend(ncol=2,loc="lower center",frameon=False,fontsize=8)
    ax.grid(axis="y",alpha=.2)
    ax.set_axisbelow(True)
    fig.text(.5,-.025,"Annual raw EIA-930A row denominator; BA code and exact plant/generator IDs required. "
             "Not physical fleet coverage, online MW, real grid adequacy or EENS.",
             ha="center",fontsize=8,wrap=True)
    for ext in ("png","pdf"):
        fig.savefig(target/f"fig_paperc_eia930a_annual_vs_cited_monthly_identity.{ext}",
                    dpi=220,bbox_inches="tight")
    plt.close(fig)
    result.to_csv(target/"table_paperc_eia930a_annual_vs_cited_monthly_identity.csv",index=False)


def main():
    p=argparse.ArgumentParser()
    for year in (2023,2024):
        p.add_argument(f"--annual{year}",required=True)
        p.add_argument(f"--monthly{year}",required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    an={year:pd.read_csv(getattr(a,"annual"+str(year))) for year in (2023,2024)}
    mo={year:pd.read_csv(getattr(a,"monthly"+str(year))) for year in (2023,2024)}
    scope=json.loads(Path(a.manifest).read_text())
    result=calculate(an,mo,scope)
    render(result,a.output)
    print(result.to_string(index=False))


if __name__=="__main__":main()
