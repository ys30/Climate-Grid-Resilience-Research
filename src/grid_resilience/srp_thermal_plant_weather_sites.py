"""Select SRP EIA-860 thermal-plant coordinates for weather sampling.

Plant BA reflects annual reporting assignment, not actual dispatch rights.
Nameplate is deduplicated by plant-generator, and each generator is assigned
exactly once by its primary fuel/prime mover. Unknown coordinates are counted
in the denominator rather than silently disappearing from source coverage.
"""
import argparse
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import load_workbook

FUEL_MOVER={"NG":{"CT","GT","CA","CS","ST"},"SUB":{"ST"}}
CATEGORY={"NG":"gas","SUB":"coal"}


def plant_coordinates(archive):
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if n.endswith("2___Plant_Y2024.xlsx")]
        if len(names)!=1:raise ValueError("Expected one official 2024 Plant workbook")
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        try:
            sheet=wb["Plant"]
            it=sheet.iter_rows(values_only=True)
            next(it)
            header=[str(v).strip() if v is not None else "" for v in next(it)]
            fields=["Plant Code","Balancing Authority Code","Latitude","Longitude"]
            if any(header.count(k)!=1 for k in fields):
                raise ValueError("Missing/ambiguous official Plant coordinates")
            idx={k:header.index(k) for k in fields}
            records=[]
            for row in it:
                if row[idx["Plant Code"]] is None:continue
                records.append({
                    "plant_id":str(row[idx["Plant Code"]]).strip(),
                    "plant_reported_ba":str(row[idx["Balancing Authority Code"]]).strip() if row[idx["Balancing Authority Code"]] is not None else "",
                    "latitude":row[idx["Latitude"]],
                    "longitude":row[idx["Longitude"]]
                })
        finally:
            wb.close()
    p=pd.DataFrame(records)
    p["plant_id"]=p.plant_id.astype("string").str.replace(r"^0+(?=[0-9])","",regex=True)
    if p.plant_id.duplicated().any():raise ValueError("Duplicate official plant key")
    return p


def select(generators,plants,*,ba="SRP",max_plants=8):
    if max_plants<1:raise ValueError("Invalid point limit")
    required={"plant_id","generator_id","energy_source_1","prime_mover",
              "nameplate_capacity_mw"}
    if not required.issubset(generators):raise ValueError("Missing operable generator fields")
    if not {"plant_id","plant_reported_ba","latitude","longitude"}.issubset(plants):
        raise ValueError("Missing Plant BA or locations")
    g=generators.copy()
    p=plants.copy()
    for df,keys in ((g,("plant_id","generator_id")),(p,("plant_id",))):
        for key in keys:
            df[key]=df[key].astype("string").str.strip()
            if df[key].isna().any() or df[key].eq("").any():
                raise ValueError("Invalid plant/generator ID")
        df["plant_id"]=df.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
    if g.duplicated(["plant_id","generator_id"]).any() or p.plant_id.duplicated().any():
        raise ValueError("Duplicate generator or plant IDs")
    g["nameplate_capacity_mw"]=pd.to_numeric(g.nameplate_capacity_mw,errors="coerce")
    g["primary_fuel"]=g.energy_source_1.astype("string").str.strip()
    g["prime_mover"]=g.prime_mover.astype("string").str.strip()
    g=g.merge(p,on="plant_id",how="left",validate="many_to_one")
    g=g.loc[g.plant_reported_ba.astype("string").str.strip().eq(ba)].copy()
    g=g.loc[g.apply(lambda row:row.primary_fuel in FUEL_MOVER and
                    row.prime_mover in FUEL_MOVER[row.primary_fuel],axis=1)].copy()
    if g.empty:raise ValueError("No target thermal generators")
    if not np.isfinite(g.nameplate_capacity_mw.to_numpy(float)).all() or (
            g.nameplate_capacity_mw<=0).any():
        raise ValueError("Invalid source thermal nameplate")
    g["technology"]=g.primary_fuel.map(CATEGORY)
    p=g.groupby(["technology","plant_id"],as_index=False,dropna=False).agg(
        nameplate_mw=("nameplate_capacity_mw","sum"),
        generator_count=("generator_id","size"),
        latitude=("latitude","first"),longitude=("longitude","first"))
    for key in ("latitude","longitude"):
        p[key]=pd.to_numeric(p[key],errors="coerce")
    p["valid_coordinate"]=p.latitude.between(20,55)&p.longitude.between(-130,-95)
    # Keep all source nameplate in coverage denominator; invalid sites remain visible.
    selected=[]
    by_tech={}
    for technology,d in p.groupby("technology"):
        good=d.loc[d.valid_coordinate].sort_values(
            ["nameplate_mw","plant_id"],ascending=[False,True]).head(max_plants).copy()
        if not good.empty:
            good["selection_capacity_weight"]=good.nameplate_mw/good.nameplate_mw.sum()
            selected.append(good)
        total=float(d.nameplate_mw.sum())
        source_with_coords=float(d.loc[d.valid_coordinate,"nameplate_mw"].sum())
        sampled=float(good.nameplate_mw.sum())
        by_tech[technology]={
            "source_generator_count":int(d.generator_count.sum()),
            "source_plant_count":int(len(d)),
            "source_nameplate_mw":total,
            "plants_with_valid_coordinate":int(d.valid_coordinate.sum()),
            "coordinate_covered_mw":source_with_coords,
            "coordinate_coverage_fraction":source_with_coords/total,
            "selected_plant_count":int(len(good)),
            "selected_nameplate_mw":sampled,
            "sampled_share_of_source_capacity":sampled/total
        }
    if not selected:raise ValueError("No geolocated thermal plants")
    sites=pd.concat(selected,ignore_index=True)
    result={"ba":ba,"source_year":2024,"source":"Official EIA860 Plant and Operable Generator",
            "source_primary_fuel_and_prime_mover_only":True,
            "annual_plant_ba_is_dispatch_right":False,
            "eia_plant_location_is_stack_or_cooling_entrance":False,
            "temperature_exposure_is_not_plant_derating":True,
            "max_points_per_technology":max_plants,
            "coverage_by_technology":by_tech}
    return sites,p,result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--archive",required=True)
    parser.add_argument("--generators",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--max-plants",type=int,default=8)
    args=parser.parse_args()
    sites,population,manifest=select(
        pd.read_csv(args.generators,dtype={"plant_id":"string","generator_id":"string"}),
        plant_coordinates(args.archive),max_plants=args.max_plants)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    sites.to_csv(out/"srp_thermal_era5_site_selection.csv",index=False)
    population.to_csv(out/"srp_thermal_coordinate_population.csv",index=False)
    (out/"srp_thermal_site_coverage_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
