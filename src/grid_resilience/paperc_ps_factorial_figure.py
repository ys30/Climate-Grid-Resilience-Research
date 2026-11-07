"""Paper C source-archived model-only figure and audited table.

Four assumed Grand Coulee PS access levels x four July 2024 hazard cases.
Not calibrated hydropower availability, actual blackout or EENS.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

CASES = ("baseline", "heat_only", "wind_only", "heat_wind")
SPEC = (
    ("PS_0MW_0MWh_eta100", 0, 0.0, 0.0),
    ("PS_78MW_314MWh_eta80", 25, 78.5, 314.0),
    ("PS_157MW_628MWh_eta80", 50, 157.0, 628.0),
    ("PS_314MW_1256MWh_eta80", 100, 314.0, 1256.0),
)


def prepare(system, scope, audited):
    """Fail closed on incomplete provenance or scenario-grid changes."""
    if (scope.get("model_hours_single_contiguous_horizon") != 672 or
        scope.get("historically_calibrated_capacity_or_outage_or_eens") is not False or
        scope.get("isolated_only_no_hypothetical_interties") is not True or
        scope.get("pumped_storage_separate_closed_zero_soc") is not True):
        raise ValueError("Unapproved model scope")
    if (audited.get("groups_checked") != 16 or
        audited.get("hours_per_group") != 672 or
        audited.get("measured_ps_equipment_operation") is not False or
        audited.get("historical_eens_identified") is not False):
        raise ValueError("Independent SOC audit incomplete")
    for key in ("resource_scenario", "scenario", "total_model_shortage_mwh"):
        if key not in system:
            raise ValueError("Missing system-model result field")
    if len(system) != 16 or system.duplicated(["resource_scenario", "scenario"]).any():
        raise ValueError("Expect unique complete 4x4 source-model factorial")
    if set(system.resource_scenario) != {s[0] for s in SPEC} or set(system.scenario) != set(CASES):
        raise ValueError("Unexpected scenario identities")
    numeric = pd.to_numeric(system.total_model_shortage_mwh, errors="coerce")
    if not np.isfinite(numeric).all() or (numeric < 0).any():
        raise ValueError("Non-finite or negative modeled gap")
    expected_specs = {(float(a),float(b),float(c)) for a,b,c in scope["ps_sensitivity_configurations"]}
    if expected_specs != {(mw,mwh,1.0 if pct==0 else .8) for _,pct,mw,mwh in SPEC}:
        raise ValueError("Unapproved assumed PS settings")
    verified = {(x["resource_scenario"], x["scenario"]) for x in audited.get("groups", [])
                if x.get("energy_balance_audited") is True and x.get("historically_calibrated") is False}
    if verified != {(a,case) for a,_,_,_ in SPEC for case in CASES}:
        raise ValueError("Missing independent audit group or calibration guard")
    pivot = system.assign(total_model_shortage_mwh=numeric).pivot(
        index="resource_scenario",columns="scenario",values="total_model_shortage_mwh")
    rows = []
    for label,pct,mw,mwh in SPEC:
        row={"assumed_access_pct":pct, "assumed_charge_discharge_mw":mw,
             "assumed_energy_mwh":mwh, "historical_calibration_certified":False}
        for c in CASES:
            row[c+"_modeled_gap_mwh"]=float(pivot.loc[label,c])
        row["interaction_mwh"]=(row["heat_wind_modeled_gap_mwh"]-
                                row["heat_only_modeled_gap_mwh"]-
                                row["wind_only_modeled_gap_mwh"]+
                                row["baseline_modeled_gap_mwh"])
        rows.append(row)
    t=pd.DataFrame(rows)
    t["baseline_gap_reduction_vs_zero_access_mwh"]=t.loc[0,"baseline_modeled_gap_mwh"]-t["baseline_modeled_gap_mwh"]
    return t


def render(table, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out=Path(output)
    out.mkdir(parents=True,exist_ok=True)
    x=table.assumed_access_pct.to_numpy()
    fig,(ax,ax2)=plt.subplots(2,1,figsize=(7.4,7.1),layout="constrained")
    for col,label in (("baseline_modeled_gap_mwh","Baseline"),
                      ("heat_only_modeled_gap_mwh","Heat only"),
                      ("wind_only_modeled_gap_mwh","Wind only"),
                      ("heat_wind_modeled_gap_mwh","Heat + wind")):
        ax.plot(x,table[col]/1e6,marker="o",label=label)
    ax.set_title("A  Conditional system shortfall in four hazard scenarios",loc="left")
    ax.set_ylabel("Modeled supply gap (million MWh / 672 h)")
    ax.legend(ncol=2,fontsize=8,frameon=False)
    ax.grid(axis="y",alpha=.2)
    ax2.plot(x,table.interaction_mwh/1000,marker="o")
    ax2.axhline(0,linewidth=.8,linestyle="--",color="gray")
    ax2.set_title("B  Heat–wind factorial interaction",loc="left")
    ax2.set_ylabel("Second difference (thousand MWh)")
    ax2.set_xlabel("Hypothetical Grand Coulee PS nameplate access (%)")
    ax2.grid(axis="y",alpha=.2)
    for a in (ax,ax2):
        a.set_xticks([0,25,50,100])
        a.set_xlim(-4,104)
    fig.text(.5,-.015,
        "Four isolated BAs; partial fleet and hypothetical 4h PS (80% roundtrip) + HY budget. "
        "Neither observed generator dispatch nor historical EENS.",
        ha="center",va="top",fontsize=8,wrap=True)
    fig.savefig(out/"fig_paperc_672h_hypothetical_ps_factorial.png",dpi=220,bbox_inches="tight")
    fig.savefig(out/"fig_paperc_672h_hypothetical_ps_factorial.pdf",bbox_inches="tight")
    plt.close(fig)
    table.to_csv(out/"table_paperc_672h_hypothetical_ps_factorial.csv",index=False)
    return out


def main():
    p=argparse.ArgumentParser()
    for name in ("system","scope","audit","output"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    table=prepare(pd.read_csv(a.system),
                  json.loads(Path(a.scope).read_text()),
                  json.loads(Path(a.audit).read_text()))
    render(table,a.output)
    print(table.to_string(index=False))


if __name__=="__main__":
    main()
