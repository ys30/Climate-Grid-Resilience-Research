import pandas as pd
import pytest
from grid_resilience.paperc_eia930_fuel_taxonomy_transition import audit,LABELS,BAS

def cohort():
    rows=[]
    for year,start,partitions in [
        (2023,"2023-07-10T00:00:00Z",[(168,"Jul_Dec","legacy")]),
        (2024,"2024-07-01T00:00:00Z",[(7,"Jan_Jun","legacy"),(161,"Jul_Dec","modern")])]:
        h=0
        for length,part,style in partitions:
            for t in pd.date_range(start,periods=168,freq="h")[h:h+length]:
                for ba in BAS:
                    for kind,v in LABELS.items():
                        for name in v[style]:
                            blank=name=="Wind with Integrated Battery Storage" and ba=="CISO"
                            val=None if blank else 0. if kind=="storage" else 5.
                            rows.append({"year":year,"ba":ba,
                                "utc_hour_start":t.isoformat(),"original_partition":part,
                                "original_fuel_category":name,
                                "reported_fuel_mwh":val,
                                "fuel_value_reported":not blank,
                                "reported_zero":val==0 if val is not None else False})
            h+=length
    return pd.DataFrame(rows),{
        "2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent":True,
        "blank_never_assumed_zero":True}

def test_legacy_seven_plus_modern_161_source_groups():
    detail,summary,scope=audit(*cohort())
    assert len(summary)==52
    assert set(summary.source_hours)=={7,161,168}
    assert summary.loc[summary.year.eq(2024)&
        summary.original_category_label.eq("Wind with Integrated Battery Storage")&
        summary.ba.eq("CISO"),"blank_hours"].iloc[0]==161
    assert scope["legacy_and_modern_schema_mwh_not_automatically_additive"]
    assert not summary.cross_2024_schema_full_168h_fuel_total_certified.any()

def test_blank_not_transmuted_to_zero():
    d,m=cohort()
    row=d[(d.ba=="CISO")&(d.original_fuel_category=="Wind with Integrated Battery Storage")].index[0]
    d.loc[row,"reported_fuel_mwh"]=0.
    with pytest.raises(ValueError,match="invented"):
        audit(d,m)

def test_original_zero_distinguished():
    d,s,_=audit(*cohort())
    x=s[s.original_category_label.eq("Battery Storage")]
    assert x.reported_zeros.sum()==4*161
    assert x.blank_hours.sum()==0

def test_missing_source_hour_rejected():
    d,m=cohort()
    with pytest.raises(ValueError,match="category or hour"):
        audit(d.iloc[:-1],m)

def test_no_unsupported_schema_admission():
    d,m=cohort()
    m["2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent"]=False
    with pytest.raises(ValueError,match="taxonomy"):
        audit(d,m)
