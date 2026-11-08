"""Year-specific EIA-860 gas/wind model-candidate adapter.

Annual nameplate inventory is *not* hourly dispatchable/firm generator output.
This creates an additional, separate model sensitivity, not a historical
calibration or a replacement for the frozen 2024 proxy experiment.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
CATEGORIES=("gas","wind")


def adapt(inventory,year):
    need={"ba","technology","source_year","nameplate_capacity_mw"}
    if not need.issubset(inventory):
        raise ValueError("Missing official annual BA fuel inventory schema")
    if year not in (2023,2024) or set(pd.to_numeric(inventory.source_year))!={year}:
        raise ValueError("Annual EIA860 inventory year does not match model year")
    if inventory.duplicated(["ba","technology"]).any() or not set(inventory.ba).issubset(BAS):
        raise ValueError("Duplicate or unexpected BA fuel records")
    rows=[]
    for ba in BAS:
        take=inventory.loc[inventory.ba.eq(ba)].set_index("technology")
        if not set(CATEGORIES).issubset(take.index):
            raise ValueError(f"Missing year-specific gas/wind candidate: {ba}")
        vals=pd.to_numeric(take.loc[list(CATEGORIES),"nameplate_capacity_mw"],errors="coerce")
        if not np.isfinite(vals).all() or (vals<=0).any():
            raise ValueError("Nonpositive or nonfinite annual generator nameplate")
        rows.append({"ba":ba,"gas_mw":float(vals.loc["gas"]),
                     "wind_mw":float(vals.loc["wind"]),"source_year":year,
                     "capacity_source":f"EIA860_{year}_OPERABLE_PLANT_BA_GAS_WIND_NAMEPLATE_CANDIDATE_NOT_FIRM_MW"})
    return pd.DataFrame(rows)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inventory",required=True)
    p.add_argument("--year",required=True,type=int)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=adapt(pd.read_csv(a.inventory),a.year)
    dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(dest,index=False)
    (dest.with_suffix(".scope.json")).write_text(json.dumps({
        "annual_eia860_source_year":a.year,
        "technologies_included":["gas","wind"],
        "excluded_generation_technologies_present_in_official_inventory":True,
        "all_nameplate_capacity_hypothetically_available_every_model_hour":True,
        "hourly_available_capacity_calibrated":False,
        "full_fleet_or_historical_eens_calibrated":False,
        "real_transfer_ratings_verified":False},indent=2)+chr(10))
    print(result.to_string(index=False))


if __name__=="__main__":
    main()
