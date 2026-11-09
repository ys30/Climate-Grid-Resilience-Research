import pandas as pd
import pytest
from grid_resilience.paperc_2024_full_fuel_schema_audit import analyze,BAS,START,N

LABELS=["Coal","Natural Gas","Nuclear","Petroleum","Other","Unknown","Wind","Solar",
        "Hydro","Pumped","Battery","Other storage"]
def sample():
    fuels=[];six=[]
    for ba in BAS:
        for k in range(N):
            t=(START+pd.Timedelta(hours=k)).isoformat()
            six.append({"ba":ba,"utc_hour_start":t,"net_generation_mw":100.,
                        "all_six_original_components_numeric":ba!="BPAT",
                        "sum_six_original_reported_components_mwh":
                            60. if ba!="BPAT" else None})
            for name in LABELS:
                null=(ba=="BPAT" and name=="Coal") or name=="Battery"
                fuels.append({"year":2024,"ba":ba,"utc_hour_start":t,
                    "original_partition":"Jul_Dec","original_fuel_category":name,
                    "fuel_value_reported":not null,
                    "reported_fuel_mwh":None if null else 0. if name=="Other" else 10.})
    return pd.DataFrame(fuels),pd.DataFrame(six),{
        "blank_never_assumed_zero":True,
        "2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent":True}

def test_original_all_label_source_blanks_are_explicit():
    category,hour,summary,scope=analyze(*sample())
    assert len(category)==48 and len(hour)==644
    assert summary.original_hours.eq(161).all()
    assert summary.hours_all_original_categories_numeric.eq(0).all()
    assert hour.all_category_reported_mwh_only_if_complete.isna().all()
    assert summary.loc[summary.ba=="BPAT","total_blank_category_cells"].iloc[0]==322
    assert scope["source_difference_not_physical_shortage_or_EENS"]

def test_missing_label_cannot_reclassify_as_zero():
    f,s,m=sample()
    f.loc[0,"fuel_value_reported"]=False
    with pytest.raises(ValueError,match="falsely imputed"):
        analyze(f,s,m)

def test_source_category_hour_missing_rejected():
    f,s,m=sample()
    with pytest.raises(ValueError,match="rectangular"):
        analyze(f.iloc[:-1],s,m)

def test_source_six_cohort_mismatch_rejected():
    f,s,m=sample()
    with pytest.raises(ValueError,match="Unmatched"):
        analyze(f,s.iloc[:-1],m)
