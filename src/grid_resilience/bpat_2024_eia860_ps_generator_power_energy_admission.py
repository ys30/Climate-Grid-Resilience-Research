"""2024 BPAT PS identity/power-energy admission from original EIA-860 ZIP.

Do not treat generic energy storage (often batteries) as pumped storage.
Use 2024 Plant BA + Operable generator prime mover/technology + separate
Energy Storage operable worksheet, linked by plant/generator identity.
Only report PS as physically parameterized when the SAME PS generator has
positive charge MW, discharge MW and usable energy MWh from storage sheet.
Even then historical SOC/efficiency/available MW remain unobserved.
"""
import argparse
import io
import json
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from openpyxl import load_workbook

def _key(x):
    return x.astype("string").str.strip().str.replace(r"\.0$","",regex=True)

def plant_ba(archive):
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if n.endswith("2___Plant_Y2024.xlsx")]
        if len(names)!=1: raise ValueError("Official EIA860 2024 Plant workbook not unique")
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        try:
            rows=wb["Plant"].iter_rows(values_only=True)
            next(rows)
            hdr=list(next(rows))
            if hdr.count("Plant Code")!=1 or hdr.count("Balancing Authority Code")!=1:
                raise ValueError("Missing/ambiguous official Plant BA headers")
            pid=hdr.index("Plant Code");ba=hdr.index("Balancing Authority Code")
            data=[{"plant_id":str(r[pid]).strip(),"ba":str(r[ba]).strip()}
                  for r in rows if r[pid] is not None]
        finally: wb.close()
    p=pd.DataFrame(data)
    p["plant_id"]=_key(p.plant_id)
    if p.empty or p.plant_id.duplicated().any():raise ValueError("Invalid Plant BA source mapping")
    return p

def audit(archive,operable,storage):
    required={"plant_id","generator_id","prime_mover","reported_technology",
              "nameplate_capacity_mw","status","energy_source_1"}
    st_required={"plant_id","generator_id","energy_mwh","charge_mw","discharge_mw",
                 "storage_technology","operating_year","operating_month"}
    if not required.issubset(operable) or not st_required.issubset(storage):
        raise ValueError("Official generator/storage fields missing")
    g=operable.copy();s=storage.copy()
    for frame in (g,s):
        for k in ("plant_id","generator_id"):
            frame[k]=_key(frame[k])
        if frame.duplicated(["plant_id","generator_id"]).any():
            raise ValueError("Duplicate official source plant-generator identity")
    g["nameplate_capacity_mw"]=pd.to_numeric(g.nameplate_capacity_mw,errors="coerce")
    for k in ("energy_mwh","charge_mw","discharge_mw","operating_year","operating_month"):
        s[k]=pd.to_numeric(s[k],errors="coerce")
    p=plant_ba(archive)
    g=g.merge(p,on="plant_id",how="left",validate="many_to_one",indicator="plant_join")
    bpat=g.loc[g.ba.eq("BPAT")].copy()
    if bpat.empty:raise ValueError("No original BPAT EIA860 operable generators")
    # Prime mover PS is the clear physical pumped hydro identification code.
    # Also show potential pumped technology text but do not silently conflate.
    pm=bpat.prime_mover.astype("string").str.strip().str.upper()
    tech=bpat.reported_technology.astype("string").str.contains("pumped",case=False,na=False)
    suspected=bpat.loc[pm.eq("PS")|tech].copy()
    suspected["prime_mover_ps_confirmed"]=suspected.prime_mover.astype("string").str.strip().str.upper().eq("PS")
    suspected["pumped_technology_label"]=suspected.reported_technology.astype("string").str.contains("pumped",case=False,na=False)
    suspected=suspected.merge(s[["plant_id","generator_id","energy_mwh","charge_mw","discharge_mw",
        "storage_technology","operating_year","operating_month"]],
        on=["plant_id","generator_id"],how="left",validate="one_to_one",indicator="storage_sheet_join")
    suspected["capacity_nameplate_positive"]=suspected.nameplate_capacity_mw.gt(0)&suspected.nameplate_capacity_mw.notna()
    suspected["three_storage_parameters_source_complete"]=(suspected[["energy_mwh","charge_mw","discharge_mw"]].gt(0).all(axis=1))
    suspected["storage_operating_by_july_2024"]=(
        suspected.operating_year.lt(2024)|
        (suspected.operating_year.eq(2024)&suspected.operating_month.le(7)))
    suspected["all_ps_source_parameters_verified"]=(
        suspected.prime_mover_ps_confirmed&
        suspected.capacity_nameplate_positive&
        suspected.three_storage_parameters_source_complete&
        suspected.storage_operating_by_july_2024&
        suspected.storage_sheet_join.eq("both"))
    # For all other storage rows, filter by BA using original plant roster.
    s_ba=s.merge(p,on="plant_id",how="left",validate="many_to_one",indicator="storage_plant_join")
    bp_storage=s_ba.loc[s_ba.ba.eq("BPAT")].copy()
    complete=bp_storage[["energy_mwh","charge_mw","discharge_mw"]].gt(0).all(axis=1)
    ps=suspected.loc[suspected.prime_mover_ps_confirmed].copy()
    if ps.empty:
        raise ValueError("No BPAT conventional pumped hydro candidate in original EIA860 Operable roster")
    summary={
        "source":"EIA860 2024 original Plant + Operable Generator + Operable Energy Storage",
        "target_ba":"BPAT",
        "bpat_operable_gen_records":int(len(bpat)),
        "bpat_ps_prime_mover_records":int(len(ps)),
        "bpat_pumped_technology_label_records":int(suspected.pumped_technology_label.sum()),
        "bpat_ps_positive_nameplate_records":int(ps.capacity_nameplate_positive.sum()),
        "bpat_ps_positive_nameplate_mw":float(ps.loc[ps.capacity_nameplate_positive,"nameplate_capacity_mw"].sum()),
        "bpat_ps_exact_generator_storage_sheet_matches":int(ps.storage_sheet_join.eq("both").sum()),
        "bpat_ps_source_complete_mw_mwh_records":int(ps.all_ps_source_parameters_verified.sum()),
        "bpat_ps_source_complete_reported_charge_mw":float(ps.loc[ps.all_ps_source_parameters_verified,"charge_mw"].sum()),
        "bpat_ps_source_complete_reported_discharge_mw":float(ps.loc[ps.all_ps_source_parameters_verified,"discharge_mw"].sum()),
        "bpat_ps_source_complete_reported_energy_mwh":float(ps.loc[ps.all_ps_source_parameters_verified,"energy_mwh"].sum()),
        "bpat_eia860_storage_sheet_all_technologies_rows":int(len(bp_storage)),
        "bpat_storage_sheet_complete_power_energy_rows":int(complete.sum()),
        "bpat_storage_sheet_not_pumped_storage_by_default":True,
        "bpat_ps_power_energy_storage_sheet_full_roster_verified":bool(len(ps)>0 and ps.all_ps_source_parameters_verified.all()),
        "physical_ps_672h_dispatch_parameters_admitted":bool(len(ps)>0 and ps.all_ps_source_parameters_verified.all()),
        "efficiency_verified_from_historical_measurements":False,
        "initial_soc_verified":False,
        "actual_historical_pumping_verified":False,
        "plant_ba_attribution_only_2024_not_hourly":True,
        "full_system_reliability_calibrated":False}
    return suspected,bp_storage,summary

def main():
    parser=argparse.ArgumentParser()
    for key in ("archive","operable","storage","output"):parser.add_argument("--"+key,required=True)
    args=parser.parse_args()
    ps,storage,m=audit(args.archive,pd.read_csv(args.operable,dtype="string"),
          pd.read_csv(args.storage,dtype="string"))
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    ps.to_csv(out/"bpat_2024_pumped_hydro_generator_source_identity.csv",index=False)
    storage.to_csv(out/"bpat_2024_2024_eia860_storage_sheet_other_technologies.csv",index=False)
    (out/"bpat_2024_ps_power_energy_admission_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print(ps.to_string(index=False));print(json.dumps(m,indent=2))

if __name__=="__main__":main()
