"""Extract EIA-860 wind-plant coordinates for four BAs without inventing locations.

EIA-860 Plant coordinates represent power-plant locations; they are not
individual turbine coordinates or BA-wide wind-resource estimates.
"""
import argparse,io,json,zipfile
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook

BAS={"AZPS","BPAT","CISO","SRP"}
def extract(archive,generators,output):
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if n.endswith("2___Plant_Y2024.xlsx")]
        if len(names)!=1:raise ValueError("EIA-860 Plant workbook not uniquely found")
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        try:
            ws=wb["Plant"];it=ws.iter_rows(values_only=True);next(it)
            header=[str(x).strip() if x is not None else "" for x in next(it)]
            fields=["Plant Code","Balancing Authority Code","Latitude","Longitude"]
            if any(header.count(x)!=1 for x in fields):raise ValueError("Plant coordinate schema incompatible: "+repr([(x,header.count(x)) for x in fields]))
            ix={key:header.index(key) for key in fields}
            rows=[{"plant_id":str(row[ix["Plant Code"]]).strip(),
                    "ba":str(row[ix["Balancing Authority Code"]]).strip(),
                    "latitude":row[ix["Latitude"]],"longitude":row[ix["Longitude"]]}
                  for row in it if row[ix["Plant Code"]] is not None]
        finally:wb.close()
    plants=pd.DataFrame(rows)
    if plants.plant_id.duplicated().any():raise ValueError("Duplicate EIA plant code")
    gen=pd.read_csv(generators,dtype={"plant_id":str},keep_default_na=False)
    wind=gen.loc[(gen.energy_source_1=="WND") & (gen.energy_source_2.eq("")) &
                 (~gen.multiple_fuels.str.upper().eq("Y"))].copy()
    wind["capacity_mw"]=pd.to_numeric(wind.nameplate_capacity_mw,errors="coerce")
    wind=wind.loc[wind.capacity_mw.gt(0)].copy()
    linked=wind.merge(plants,on="plant_id",validate="many_to_one",indicator=True)
    wind_ba=linked.loc[linked.ba.isin(BAS)].copy()
    if wind_ba.empty:raise ValueError("No linked eligible wind generators")
    wind_ba["latitude"]=pd.to_numeric(wind_ba.latitude,errors="coerce")
    wind_ba["longitude"]=pd.to_numeric(wind_ba.longitude,errors="coerce")
    valid=(wind_ba.latitude.between(20,55) & wind_ba.longitude.between(-130,-95))
    good=wind_ba.loc[valid].copy()
    locations=good.groupby(["ba","plant_id","latitude","longitude"],as_index=False).agg(
        nameplate_mw=("capacity_mw","sum"),generator_count=("generator_id","size"))
    locations=locations.sort_values(["ba","nameplate_mw"],ascending=[True,False])
    total=wind_ba.groupby("ba").capacity_mw.sum()
    matched=good.groupby("ba").capacity_mw.sum()
    manifest={"source":"EIA-860 2024 Plant latitude/longitude and Operable Generator wind nameplate",
              "wind_generator_rows":len(wind_ba),"wind_plant_locations":len(locations),
              "covered_wind_nameplate_mw":float(good.capacity_mw.sum()),
              "total_eligible_wind_nameplate_mw":float(wind_ba.capacity_mw.sum()),
              "coordinate_coverage_by_ba":{ba:{"capacity_total_mw":float(total.get(ba,0)),
                "capacity_with_valid_coords_mw":float(matched.get(ba,0)),
                "capacity_coverage_fraction":float(matched.get(ba,0)/total.get(ba,1))}
                for ba in sorted(BAS)},
              "plant_location_not_turbine_coordinate":True,
              "wind_fleet_coverage_not_certified":True,
              "hourly_weather_download_completed":False}
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    locations.to_csv(out/"eia860_2024_wind_plant_locations.csv",index=False)
    (out/"eia860_wind_plant_location_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest
def main():
    p=argparse.ArgumentParser()
    for arg in ("archive","generators","output"):p.add_argument("--"+arg,required=True)
    a=p.parse_args();print(json.dumps(extract(a.archive,a.generators,a.output),indent=2))
if __name__=="__main__":main()
