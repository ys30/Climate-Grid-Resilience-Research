import pandas as pd
import pytest
from grid_resilience.paperc_2024_baseline_admission import evaluate

BAS=("AZPS","BPAT","CISO","SRP")
FUEL=("Natural Gas","Coal","Nuclear","Solar without Integrated Battery Storage",
      "Wind without Integrated Battery Storage","Hydropower Excluding Pumped Storage",
      "Battery Storage","Pumped Storage")

def sample():
    hours=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    b=[];f=[]
    for ba in BAS:
        for i,t in enumerate(hours):
            part="Jan_Jun" if i<7 else "Jul_Dec"
            ti=None if ba=="CISO" and i>=24 else 0.
            b.append({"ba":ba,"utc_hour_start":t.isoformat(),
                "demand_mw":100.,"net_generation_mw":100.,
                "net_interchange_mw":ti,"source_partition":"2024_"+part,
                "raw_triplet_present":ti is not None,
                "raw_arithmetic_closes":ti is not None})
            names=FUEL[:3] if i<7 else FUEL
            for name in names:
                missing=name=="Battery Storage" or name=="Pumped Storage"
                f.append({"year":2024,"ba":ba,"utc_hour_start":t.isoformat(),
                    "original_fuel_category":name,"original_partition":part,
                    "reported_fuel_mwh":None if missing else 0.,
                    "fuel_value_reported":not missing})
    scopes=(
        {"source_ba_hours_complete":True,"raw_reported_values_never_imputed":True},
        {"2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent":True},
        {"no_storage_energy_mwh_initial_soc_or_efficiency_inferred":True})
    return pd.DataFrame(b),pd.DataFrame(f),*scopes

def test_original_source_admission_keeps_all_four_bas_but_no_physical_calibration():
    m,d,s=evaluate(*sample())
    assert len(m)==4 and len(d)==32
    assert m.set_index("ba").loc["CISO","raw_total_interchange_missing_hours"]==144
    assert m.modern_original_battery_reported_hours.eq(0).all()
    assert not m.historical_EENS_or_shortage_inference_admissible.any()
    assert not m.historical_pypsa_four_ba_calibration_admissible.any()
    assert s["full_source_hour_coverage_does_not_prove_physical_adequacy"]

def test_missing_ti_cannot_be_filled_as_zero():
    b,f,*other=sample()
    ix=b[(b.ba=="CISO")&(b.net_interchange_mw.isna())].index[0]
    b.loc[ix,"net_interchange_mw"]=0.
    with pytest.raises(ValueError,match="triplet"):
        evaluate(b,f,*other)

def test_original_partition_disagreement_rejected():
    b,f,*other=sample()
    f.loc[0,"original_partition"]="Jul_Dec"
    with pytest.raises(ValueError,match="partition"):
        evaluate(b,f,*other)

def test_source_fuel_missing_values_not_imputed():
    b,f,*other=sample()
    ix=f[(f.original_fuel_category=="Battery Storage")].index[0]
    f.loc[ix,"reported_fuel_mwh"]=0.
    with pytest.raises(ValueError,match="silently filled"):
        evaluate(b,f,*other)
