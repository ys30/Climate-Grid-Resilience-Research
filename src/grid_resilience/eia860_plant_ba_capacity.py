"""Use EIA-860 2024 Plant official BA codes to attribute Operable generators."""
import argparse,io,json,zipfile
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
BAS={"CISO","AZPS","BPAT","SRP"}
def build(archive,generators_csv,output):
    with zipfile.ZipFile(archive) as z:
        names=[s for s in z.namelist() if s.endswith("2___Plant_Y2024.xlsx")]
        if len(names)!=1:raise ValueError("Missing/ambiguous EIA-860 2024 Plant workbook")
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        try:
            ws=wb["Plant"];it=ws.iter_rows(values_only=True);next(it)
            header=list(next(it))
            fields=["Plant Code","Balancing Authority Code"]
            ix={k:header.index(k) for k in fields}
            records=[{"plant_id":str(row[ix["Plant Code"]]).strip(),
                      "ba":str(row[ix["Balancing Authority Code"]]).strip()}
                     for row in it if row[ix["Plant Code"]] is not None]
        finally:wb.close()
    plant=pd.DataFrame(records)
    if plant.plant_id.duplicated().any():raise ValueError("Duplicate plant ID")
    gen=pd.read_csv(generators_csv,dtype={"plant_id":str,"generator_id":str},keep_default_na=False)
    if not {"nameplate_capacity_mw","energy_source_1","plant_id","generator_id"}.issubset(gen):
        raise ValueError("Missing generator fields")
    merged=gen.merge(plant,on="plant_id",how="left",validate="many_to_one",indicator=True)
    unmatched=int((merged["_merge"]!="both").sum())
    selected=merged.loc[merged.ba.isin(BAS)].copy()
    from .eia860_generator_join import FUEL_TO_TECH
    primary=selected.energy_source_1.fillna("").str.strip()
    second=selected.energy_source_2.fillna("").str.strip()
    multiple=selected.multiple_fuels.fillna("").str.strip().str.upper().eq("Y")|second.ne("")
    storage=selected.reported_technology.fillna("").str.contains("Storage|Battery|Pumped",case=False,regex=True)
    capacity=pd.to_numeric(selected.nameplate_capacity_mw,errors="coerce")
    good=~multiple&~storage&primary.isin(FUEL_TO_TECH)&capacity.notna()&(capacity>0)
    # Disjoint attrition reasons on the four-BA operable generator roster.
    # This audits selection into the single-fuel capacity subset, not the full fleet.
    reasons=pd.Series("included",index=selected.index,dtype=str)
    reasons.loc[~(capacity.notna()&(capacity>0))]="invalid_or_missing_nameplate"
    reasons.loc[reasons.eq("included")&multiple]="multifuel_or_secondary_fuel"
    reasons.loc[reasons.eq("included")&storage]="storage_excluded"
    reasons.loc[reasons.eq("included")&~primary.isin(FUEL_TO_TECH)]="unmapped_primary_energy_source"
    attrition=reasons.value_counts().to_dict()
    assert sum(attrition.values())==len(selected)
    assert int(attrition.get("included",0))==int(good.sum())
    selected=selected.loc[good].copy();selected["technology"]=primary.loc[good].map(FUEL_TO_TECH)
    selected["capacity_mw"]=capacity.loc[good]
    summary=selected.groupby(["ba","technology"],as_index=False).agg(
        nameplate_capacity_mw=("capacity_mw","sum"),generator_count=("generator_id","size"))
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    summary.to_csv(out/"eia860_plant_ba_capacity_candidates.csv",index=False)
    manifest={"plants_with_reported_ba":len(plant),"unmatched_generator_plant_ids":unmatched,
              "four_ba_operable_generator_rows":int(merged.ba.isin(BAS).sum()),
              "eligible_single_fuel_generator_rows":len(selected),
              "four_ba_roster_attrition_counts":{str(k):int(v) for k,v in sorted(attrition.items())},
              "fraction_of_four_ba_rows_selected":(len(selected)/int(merged.ba.isin(BAS).sum())
                  if int(merged.ba.isin(BAS).sum()) else None),
              "eligible_nameplate_capacity_mw":float(selected.capacity_mw.sum()),
              "plant_ba_mapping_source":"EIA-860 2024 Plant balancing authority code",
              "full_ba_fleet_certified":False,"historical_calibration_certified":False,
              "caution":"Single-fuel nameplate capacity only; BA association is reported for 2024, not verified hourly status or net output."}
    (out/"eia860_plant_ba_capacity_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest
def main():
    p=argparse.ArgumentParser();p.add_argument("--archive",required=True)
    p.add_argument("--generators",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(build(a.archive,a.generators,a.output),indent=2))
if __name__=="__main__":main()
