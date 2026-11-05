"""Grand Coulee EIA-860 6163 PS to USBR reversible pumping-plant concordance.

The six generator keys and 314MW nameplate MUST come from original EIA860.
USBR independently describes John W. Keys III plant and its irrigation
mission. No water volume-to-electricity conversion or guessed reservoir SOC.
"""
import argparse,json
from pathlib import Path
import pandas as pd
EXPECTED={"PG7":50.0,"PG8":50.0,"PG9":53.5,"PG10":53.5,"PG11":53.5,"PG12":53.5}
USBR=[
    "https://www.usbr.gov/projects/index.php?id=438",
    "https://www.usbr.gov/projects/index.php?id=526",
    "https://www.usbr.gov/pn/grandcoulee/cbp/johnkeys/index.html",
    "https://www.usbr.gov/projects/index.php?id=228"
]

def audit(source):
    need={"plant_id","generator_id","prime_mover","reported_technology","nameplate_capacity_mw","ba","storage_sheet_join"}
    if not need.issubset(source):raise ValueError(f"Original EIA860 PS audit missing {need-set(source.columns)}")
    q=source.copy()
    q["plant_id"]=q.plant_id.astype("string").str.strip().str.replace(r"\\.0$","",regex=True)
    q["generator_id"]=q.generator_id.astype("string").str.strip()
    q["nameplate_capacity_mw"]=pd.to_numeric(q.nameplate_capacity_mw,errors="raise")
    if (len(q)!=6 or q.generator_id.duplicated().any() or
        set(q.generator_id)!=set(EXPECTED) or not q.plant_id.eq("6163").all() or
        not q.ba.eq("BPAT").all() or
        not q.prime_mover.eq("PS").all() or
        not q.storage_sheet_join.eq("left_only").all()):
        raise ValueError("Original 2024 EIA860 Grand Coulee six BPAT PS generator identities do not match")
    for key,capacity in EXPECTED.items():
        v=float(q.loc[q.generator_id.eq(key),"nameplate_capacity_mw"].iloc[0])
        if abs(v-capacity)>.01:raise ValueError(f"Source-nameplate inconsistency {key}")
    if abs(q.nameplate_capacity_mw.sum()-314.)>.01:raise ValueError("PS nameplate aggregate inconsistent")
    q["usbr_facility"]="John W. Keys III Pump-Generating Plant, Grand Coulee"
    q["uses_irrigation_water_supply"]=True
    q["usbr_generator_operation"]="six reversible pump-generating units (distinct from six dedicated pumps)"
    q["source_verified_water_to_electrical_usable_storage_mwh"]=pd.NA
    q["source_verified_2024_hourly_irrigation_delivery_m3"]=pd.NA
    q["source_verified_2024_pumping_power_mw"]=pd.NA
    q["source_verified_roundtrip_efficiency"]=pd.NA
    q["source_verified_2024_hourly_dispatch"]=pd.NA
    summary={"eia860_2024_plant_id":"6163","eia860_2024_ba":"BPAT",
      "usbr_official_facility":"Grand Coulee - John W. Keys III Pump-Generating Plant",
      "physical_reversible_PS_generating_units":6,
      "dedicated_irrigation_only_pumps_usbr_describes":6,
      "EIA860_PS_nameplate_MW":314.0,
      "Banks_Lake_upper_reservoir_and_irrigation_water_storage":True,
      "Banks_Lake_active_storage_acre_feet_usbr_described":715000,
      "active_storage_acre_feet_is_not_usable_PS_energy_MWh":True,
      "water_allocation_to_2024_PS_electricity_verified":False,
      "PS_pumping_electrical_MW_verified_from_source":False,
      "PS_usable_MWh_verified":False,
      "PS_roundtrip_efficiency_verified":False,
      "PS_hourly_2024_water_duty_or_dispatch_verified":False,
      "earlier_assumed_2h_4h_80pct_90pct_are_physical_facts":False,
      "earlier_model_zero_initial_final_SOC_is_historical_fact":False,
      "original_nameplate_not_firm_available_power":True,
      "usbr_original_sources":USBR,
      "research_classification":"source-confirmed identity and generator nameplate, uncalibrated PS operations"}
    return q,summary

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--eia860-ps",required=True)
    a.add_argument("--output",required=True)
    x=a.parse_args();g,m=audit(pd.read_csv(x.eia860_ps,dtype={"plant_id":str,"generator_id":str}))
    o=Path(x.output);o.mkdir(parents=True,exist_ok=True)
    g.to_csv(o/"bpat_grand_coulee_eia860_ps_six_generator_usbr_concordance.csv",index=False)
    (o/"grand_coulee_usbr_2024_ps_operational_admission.json").write_text(json.dumps(m,indent=2)+"\n")
    print("VERIFIED GRAN COULEE EIA860 6163 6 PS UNITS AND IRRIGATION WATER DUTY")
    print(g[["plant_id","generator_id","nameplate_capacity_mw","usbr_facility"]].to_string(index=False))
    print(json.dumps(m,indent=2))

if __name__=="__main__":main()
