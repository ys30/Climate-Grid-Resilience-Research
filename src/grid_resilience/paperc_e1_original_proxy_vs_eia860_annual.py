"""Paper C E1: year-specific EIA860 candidate roster vs original partial proxy.

This is an *inventory definition audit*, NOT an arithmetic correction to
hourly firm capacity. In particular, the old `gas_mw` field names an
EIA923-selected generic thermal proxy; it is NOT EIA860 gas-only nameplate.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
CORE=("coal","gas","oil","nuclear","hydro","solar","wind","geothermal")


def reconcile(annual, original, scope, vintage):
    source=scope["source_manifests"]
    if len(source)!=2 or sorted(m["source_year"] for m in source)!=[2023,2024]:
        raise ValueError("Expected audited two original annual EIA860 source vintages")
    year24=next(m for m in source if m["source_year"]==2024)
    if (year24["four_ba_operable_rows"]!=3268
            or year24["four_ba_selected_single_fuel_rows"]!=2625
            or year24["excluded_four_ba_rows"]!=643
            or year24["complete_physical_fleet_admitted"] is not False):
        raise ValueError("Annual candidate fleet admission scope changed")
    if (len(annual)==0 or annual.duplicated(["ba","technology"]).any()
            or set(annual.ba)!=set(BAS)
            or not set(annual.technology).issubset(CORE)
            or not set(annual.source_year)=={2024}):
        raise ValueError("Annual single-fuel original 2024 population invalid")
    if (len(original)!=4 or original.ba.duplicated().any()
            or set(original.ba)!=set(BAS)
            or not original.capacity_source.astype(str).str.contains("GENERIC_THERMAL_PROXY").all()
            or set(original.source_year)!={2024}):
        raise ValueError("Original frozen partial proxy source population invalid")
    for col in ["nameplate_capacity_mw","generator_rows"]:
        if not np.isfinite(pd.to_numeric(annual[col],errors="coerce")).all():
            raise ValueError("Annual candidate data non-finite")
    if (annual.nameplate_capacity_mw<=0).any():
        raise ValueError("Annual candidate MW must be positive")
    for col in ("gas_mw","wind_mw"):
        if not np.isfinite(pd.to_numeric(original[col],errors="coerce")).all():
            raise ValueError("Partial proxy MW invalid")
    if len(vintage)!=4 or set(vintage.ba)!=set(BAS) or not set(vintage.year)=={2024}:
        raise ValueError("Monthly source-vintage BA identity audit missing")
    if vintage.source_rows.sum()!=1960 or vintage.monthly_no_verified_identity.sum()!=231:
        raise ValueError("Monthly-vintage EIA930A population changed")
    if vintage.monthly_unmatched.sum()!=10 or vintage.monthly_ba_conflicts.sum()!=27:
        raise ValueError("Monthly source ID disagreement changed")
    required={"monthly_same_ba_matches","monthly_ambiguous","vintage_match_category_changes"}
    if not required.issubset(vintage):
        raise ValueError("EIA930A identity audit fields absent")
    pivot=annual.pivot(index="ba",columns="technology",values="nameplate_capacity_mw").reindex(
        index=BAS,columns=CORE).fillna(0)
    old=original.set_index("ba").reindex(BAS)
    aud=vintage.set_index("ba").reindex(BAS)
    rows=[]
    for ba in BAS:
        # Comparable rows may be defined only *within* the same annual roster,
        # never by subtracting the original EIA923-selected thermal proxy.
        records={
            "ba":ba,
            "annual_2024_technology_candidates_mw":float(pivot.loc[ba].sum()),
            "annual_2024_gas_only_nameplate_mw":float(pivot.loc[ba,"gas"]),
            "annual_2024_coal_nameplate_mw":float(pivot.loc[ba,"coal"]),
            "annual_2024_wind_nameplate_mw":float(pivot.loc[ba,"wind"]),
            "annual_2024_solar_nameplate_mw":float(pivot.loc[ba,"solar"]),
            "annual_2024_hydro_nameplate_mw":float(pivot.loc[ba,"hydro"]),
            "annual_2024_nuclear_nameplate_mw":float(pivot.loc[ba,"nuclear"]),
            "original_model_generic_thermal_proxy_mw":float(old.loc[ba,"gas_mw"]),
            "original_model_wind_proxy_mw":float(old.loc[ba,"wind_mw"]),
            "thermal_proxy_not_same_population_as_eia860_gas_only":True,
            "source_populations_additively_comparable":False,
            "verified_physical_hourly_available_capacity_mw":None,
            "eia930a_2024_annual_records":int(aud.loc[ba,"source_rows"]),
            "eia930a_aug2025_same_ba_id_matches":int(aud.loc[ba,"monthly_same_ba_matches"]),
            "eia930a_aug2025_unmatched":int(aud.loc[ba,"monthly_unmatched"]),
            "eia930a_aug2025_unverified_id":int(aud.loc[ba,"monthly_no_verified_identity"]),
            "eia930a_aug2025_ba_conflicts":int(aud.loc[ba,"monthly_ba_conflicts"]),
        }
        rows.append(records)
    result=pd.DataFrame(rows)
    assert len(result)==4
    flags={
        "scope":"Original annual EIA860 single-fuel nonstorage candidate nameplate versus EIA923-selected partial generic thermal/wind model inventory",
        "annual_2024_four_ba_operable_records":3268,
        "annual_2024_singlefuel_nonstorage_candidate_records":2625,
        "annual_2024_unadmitted_operable_records":643,
        "eia930a_2024_august2025_unverified_id_records":231,
        "nameplate_is_not_available_hourly_capacity":True,
        "old_gas_mw_is_generic_thermal_not_gas_only":True,
        "annual_candidates_and_original_model_proxy_are_not_additive":True,
        "physical_grid_capacity_complete":False,
        "new_pypsa_optimization_performed":False,
        "ready_for_e2_physical_fleet_substitution":False,
    }
    return result,flags


def main():
    p=argparse.ArgumentParser()
    for arg in ("annual","original-proxy","annual-scope","monthly-identity","output"):
        p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    res,scope=reconcile(pd.read_csv(a.annual),pd.read_csv(a.original_proxy),
                        json.loads(Path(a.annual_scope).read_text()),
                        pd.read_csv(a.monthly_identity))
    root=Path(a.output);root.mkdir(parents=True,exist_ok=True)
    res.to_csv(root/"paper_c_e1_original_proxy_vs_2024_annual_roster_scope.csv",index=False)
    (root/"paper_c_e1_original_proxy_vs_annual_scope.json").write_text(
        json.dumps(scope,indent=2)+"\n")
    print(res.to_string(index=False))
    print(json.dumps(scope,indent=2))


if __name__=="__main__":
    main()
