"""Source-audited year-specific EIA-860 nameplate candidates; NOT hourly availability."""
import argparse
import io
import json
import zipfile
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from .eia860_generator_extract import HEADERS
from .eia860_generator_join import FUEL_TO_TECH

BAS={"AZPS","BPAT","CISO","SRP"}


def _worksheet(archive, contains, tab):
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if contains in Path(n).name and n.lower().endswith(".xlsx")]
        if len(names)!=1:
            raise ValueError(f"Ambiguous official workbook {contains}: {names}")
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        try:
            ws=wb[tab]
            it=ws.iter_rows(values_only=True)
            next(it)
            headers=[str(x).strip() if x is not None else "" for x in next(it)]
            if len(headers)!=len(set(headers)):
                raise ValueError("Ambiguous official workbook headers")
            records=list(it)
            return headers,records
        finally:
            wb.close()


def extract_year(archive, year):
    if year not in (2023,2024):
        raise ValueError("Only EIA-860 source year 2023/2024 admitted")
    ghead,grows=_worksheet(archive,"3_1_Generator","Operable")
    phead,prows=_worksheet(archive,"2___Plant","Plant")
    fields=["Plant Code","Balancing Authority Code"]
    if any(phead.count(x)!=1 for x in fields) or any(ghead.count(x)!=1 for x in HEADERS):
        raise ValueError("Official generator/plant schema incomplete")
    pi={k:phead.index(k) for k in fields}
    gi={k:ghead.index(k) for k in HEADERS}
    plants=[]
    for row in prows:
        if row[pi["Plant Code"]] is None:continue
        plants.append((str(row[pi["Plant Code"]]).strip(),
                       str(row[pi["Balancing Authority Code"]]).strip() if row[pi["Balancing Authority Code"]] is not None else ""))
    plant=pd.DataFrame(plants,columns=["plant_id","ba"])
    if plant.plant_id.duplicated().any():
        raise ValueError("Duplicated official Plant code")
    records=[]
    for row in grows:
        if row[gi["Plant Code"]] is None:continue
        record={v:(str(row[gi[k]]).strip() if row[gi[k]] is not None else "")
                for k,v in HEADERS.items()}
        records.append(record)
    gen=pd.DataFrame(records)
    if gen.empty or gen.duplicated(["plant_id","generator_id"]).any():
        raise ValueError("Duplicated/empty Operable generator roster")
    j=gen.merge(plant,on="plant_id",how="left",validate="many_to_one",indicator=True)
    selected=j.loc[j.ba.isin(BAS)].copy()
    if set(selected.ba)!=BAS:
        raise ValueError("Missing a four-BA roster in this source year")
    primary=selected.energy_source_1.fillna("").str.strip().str.upper()
    second=selected.energy_source_2.fillna("").str.strip().str.upper()
    multifuel=selected.multiple_fuels.fillna("").str.strip().str.upper().isin(["Y","YES","1","TRUE"]) | second.ne("")
    storage=selected.reported_technology.fillna("").str.contains("Storage|Battery|Pumped",case=False,regex=True)
    mw=pd.to_numeric(selected.nameplate_capacity_mw,errors="coerce")
    admitted=~multifuel & ~storage & primary.isin(FUEL_TO_TECH) & mw.gt(0) & mw.notna()
    accepted=selected.loc[admitted].copy()
    accepted["technology"]=primary.loc[admitted].map(FUEL_TO_TECH)
    accepted["nameplate_capacity_mw"]=mw.loc[admitted]
    report=accepted.groupby(["ba","technology"],as_index=False).agg(
        nameplate_capacity_mw=("nameplate_capacity_mw","sum"),
        generator_rows=("generator_id","size"))
    report["source_year"]=year
    manifest={"source_year":year,"all_us_operable_generators":len(gen),
              "four_ba_operable_rows":len(selected),
              "four_ba_selected_single_fuel_rows":len(accepted),
              "excluded_four_ba_rows":len(selected)-len(accepted),
              "nameplate_not_hourly_available_mw":True,
              "complete_physical_fleet_admitted":False,
              "actual_dispatch_or_EENS_calibrated":False,
              "plant_ba_source":"EIA-860 annual reported Plant BA; not electrical connectivity"}
    return report,manifest


def compare(a,b):
    if set(a.source_year)!={2023} or set(b.source_year)!={2024}:
        raise ValueError("Capacity comparison requires actual 2023 and 2024 annual source labels")
    x=a.merge(b,on=["ba","technology"],how="outer",suffixes=("_2023","_2024"),indicator=True)
    x["yearly_coverage"]=x["_merge"].astype(str)
    x["nameplate_difference_mw"]=x.nameplate_capacity_mw_2024.fillna(0)-x.nameplate_capacity_mw_2023.fillna(0)
    x["estimated_hourly_firm_capacity"]=False
    x["previous_frozen_2024_partial_fleet_valid_for_2023"]=False
    return x.drop(columns=["_merge"])


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive2023",required=True)
    p.add_argument("--archive2024",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    ra,ma=extract_year(a.archive2023,2023)
    rb,mb=extract_year(a.archive2024,2024)
    ra.to_csv(out/"eia860_2023_fourba_nameplate_candidates.csv",index=False)
    rb.to_csv(out/"eia860_2024_fourba_nameplate_candidates.csv",index=False)
    compare(ra,rb).to_csv(out/"eia860_2023_vs_2024_fourba_nameplate_comparison.csv",index=False)
    (out/"year_specific_capacity_scope.json").write_text(json.dumps({
        "source_manifests":[ma,mb],
        "2023_nameplate_fleet_only_not_replayed_in_pypsa":True,
        "cross_year_model_results_still_use_frozen_2024_partial_fleet":True,
        "actual_intertie_ratings_calibrated":False,
        "historical_energy_not_served_identified":False
    },indent=2)+chr(10))
    print(json.dumps([ma,mb],indent=2))
    print(compare(ra,rb).to_string(index=False))


if __name__=="__main__":
    main()
