"""Publication supplement: source-reported completeness of 2024 Jul-Dec fuel schema.

Only reporting completeness for the original EIA-930 161-hour
post-reclassification partition. No physical fleet or output inferred.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
LABELS=(
 "Wind without Integrated Battery Storage",
 "Wind with Integrated Battery Storage",
 "Solar without Integrated Battery Storage",
 "Solar with Integrated Battery Storage",
 "Hydropower Excluding Pumped Storage",
 "Pumped Storage",
 "Battery Storage"
)
SHORT=("Wind, no integrated storage","Wind + integrated storage",
       "Solar, no integrated storage","Solar + integrated storage",
       "Conventional hydro","Pumped storage","Battery storage")


def matrix(table,scope):
    if scope.get("legacy_and_modern_schema_mwh_not_automatically_additive") is not True:
        raise ValueError("Source taxonomy comparability prohibition absent")
    required={"year","ba","source_half","original_category_label","source_hours",
              "reported_hours","blank_hours","reported_fraction",
              "cross_2024_schema_full_168h_fuel_total_certified"}
    if not required.issubset(table):
        raise ValueError("Original source category reporting fields missing")
    data=table.loc[(table.year==2024)&table.source_half.eq("Jul_Dec")&
                   table.original_category_label.isin(LABELS)].copy()
    if len(data)!=28 or data.duplicated(["ba","original_category_label"]).any():
        raise ValueError("Incomplete 4BA x 7 modern fuel-label source table")
    if not data.source_hours.eq(161).all():
        raise ValueError("Wrong original 2024 modern partition duration")
    if not data.reported_hours.add(data.blank_hours).eq(161).all():
        raise ValueError("Original source reporting counts do not reconcile")
    if data.cross_2024_schema_full_168h_fuel_total_certified.any():
        raise ValueError("Forbidden cross-schema historical fuel total")
    out=np.empty((len(LABELS),len(BAS)))
    for i,label in enumerate(LABELS):
        for j,ba in enumerate(BAS):
            r=data.loc[data.ba.eq(ba)&data.original_category_label.eq(label)].iloc[0]
            v=r.reported_hours/161
            if not np.isclose(v,r.reported_fraction,rtol=0,atol=1e-10):
                raise ValueError("Reported fraction differs from official source count")
            out[i,j]=v
    return out


def render(m,target):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    target=Path(target);target.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(9.3,5.4),layout="constrained")
    im=ax.imshow(m,vmin=0,vmax=1,cmap="viridis",aspect="auto")
    ax.set_xticks(np.arange(4),BAS)
    ax.set_yticks(np.arange(7),SHORT)
    for i in range(len(LABELS)):
        for j in range(len(BAS)):
            v=m[i,j]
            ax.text(j,i,f"{round(v*161)}/161",ha="center",va="center",
                    color="white" if v<0.50 else "black",fontsize=9)
    ax.set_title("Original EIA-930 fuel-category reporting completeness · Jul 2024",loc="left")
    cb=fig.colorbar(im,ax=ax,pad=.02,shrink=.8)
    cb.set_label("Fraction of 161 source hours with numeric reported values")
    fig.text(.5,-.018,
        "Original 2024 Jul-Dec schema, UTC 7 Jul study days excluding first 7h from Jan-Jun. "
        "Blank is NOT zero output; source reporting completeness is NOT physical technology availability.",
        fontsize=8,ha="center",wrap=True)
    for ext in ("png","pdf"):
        fig.savefig(target/f"fig_paperc_2024_renewable_storage_fuel_reporting.{ext}",
                    bbox_inches="tight",dpi=230)
    plt.close(fig)
    pd.DataFrame(m,index=LABELS,columns=BAS).to_csv(
        target/"table_paperc_2024_modern_fuel_nonblank_fraction.csv")


def main():
    p=argparse.ArgumentParser()
    for k in ("source","manifest","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    mat=matrix(pd.read_csv(a.source),json.loads(Path(a.manifest).read_text()))
    render(mat,a.output)
    p=Path(a.output)
    (p/"fuel_reporting_figure_scope.json").write_text(json.dumps({
        "source_part":"2024_Jul_Dec","source_hours_per_ba":161,
        "first_seven_utc_hours_kept_in_legacy_schema":True,
        "blank_is_not_zero":True,"modern_fuel_columns_not_2024_168h_harmonized":True,
        "hourly_physical_energy_supply_or_EENS_validated":False
    },indent=2)+"\n")
    print(pd.DataFrame(mat,index=LABELS,columns=BAS))


if __name__=="__main__":main()
