import csv
import pandas as pd
import pytest
from grid_resilience.paperc_eia930_2023_2024_hourly_fuel_panel import audit

BAS=("AZPS","BPAT","CISO","SRP")
OLD=("Coal","Natural Gas","Nuclear","All Petroleum Products",
     "Hydropower and Pumped Storage","Solar","Wind","Other Fuel Sources","Unknown Fuel Sources")
NEW=("Coal","Natural Gas","Nuclear","All Petroleum Products","Hydropower Excluding Pumped Storage",
     "Pumped Storage","Solar without Integrated Battery Storage",
     "Solar with Integrated Battery Storage","Wind without Integrated Battery Storage",
     "Wind with Integrated Battery Storage","Other Fuel Sources","Unknown Fuel Sources")


def make(path,times,fuels,blank=False,missing_hour=False):
    columns=["Balancing Authority","UTC Time at End of Hour","Net Generation (MW)"]+[
        "Net Generation (MW) from "+x for x in fuels]
    with path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=columns)
        writer.writeheader()
        for i,t in enumerate(times):
            for ba in BAS:
                if missing_hour and i==0 and ba=="AZPS":
                    continue
                raw={"Balancing Authority":ba,
                     "UTC Time at End of Hour":(t+pd.Timedelta(hours=1)).strftime(
                        "%m/%d/%Y %I:%M:%S %p"),"Net Generation (MW)":"80"}
                for fuel in fuels:
                    raw["Net Generation (MW) from "+fuel]=(
                        "" if blank and i==0 and ba=="CISO" and fuel=="Natural Gas" else
                        "0" if fuel!="Natural Gas" else "40")
                writer.writerow(raw)


def sample(tmp_path,blank=False,missing_hour=False):
    ts23=pd.date_range("2023-07-10T00:00:00Z",periods=168,freq="h")
    ts24=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    a,b,c=[tmp_path/x for x in ("23.csv","24a.csv","24b.csv")]
    make(a,ts23,OLD,blank,missing_hour)
    make(b,ts24[:7],OLD,blank)
    make(c,ts24[7:],NEW,blank)
    return {(2023,"Jul_Dec"):a,(2024,"Jan_Jun"):b,(2024,"Jul_Dec"):c}


def test_original_2024_seven_plus_161_and_source_categories(tmp_path):
    hourly,summary,scope=audit(sample(tmp_path))
    assert hourly.groupby(["year","ba"]).utc_hour_start.nunique().eq(168).all()
    p=scope["original_source_partitions"]
    assert {(x["year"],x["partition"],x["source_ba_hours"]) for x in p}=={
        (2023,"Jul_Dec",672),(2024,"Jan_Jun",28),(2024,"Jul_Dec",644)}
    assert hourly.loc[(hourly.year==2024)&hourly.original_fuel_category.eq("Pumped Storage"),
                      "original_partition"].eq("Jul_Dec").all()
    assert not hourly.loc[(hourly.year==2024)&hourly.original_fuel_category.eq("Wind"),
                      "original_partition"].eq("Jul_Dec").any()
    assert scope["2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent"]
    assert not scope["historical_hourly_available_mw_or_adequacy_calibrated"]


def test_blank_is_not_reported_zero(tmp_path):
    hourly,summary,_=audit(sample(tmp_path,blank=True))
    v=hourly[(hourly.year==2024)&(hourly.ba=="CISO")&
             (hourly.original_partition=="Jan_Jun")&
             (hourly.original_fuel_category=="Natural Gas")]
    assert len(v)==7
    assert v.reported_fuel_mwh.isna().sum()==1
    assert v.reported_zero.sum()==0
    s=summary[(summary.year==2024)&summary.ba.eq("CISO")&
              summary.original_partition.eq("Jan_Jun")&
              summary.original_fuel_category.eq("Natural Gas")].iloc[0]
    assert s.reported_hours==6 and s.blank_hours==1
    assert pd.isna(s.full_partition_mwh_only_if_no_blank)


def test_absent_original_ba_hour_rejected(tmp_path):
    with pytest.raises(ValueError,match="incomplete"):
        audit(sample(tmp_path,missing_hour=True))


def test_overlapping_two_source_partitions_rejected(tmp_path):
    src=sample(tmp_path)
    ts24=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    make(src[(2024,"Jul_Dec")],ts24[6:],NEW)
    with pytest.raises(ValueError,match="Overlapping"):
        audit(src)


def test_original_fuel_labels_do_not_claim_modern_equivalence(tmp_path):
    hourly,_,_=audit(sample(tmp_path))
    f=hourly[hourly.year.eq(2024)]
    assert f[f.original_fuel_category.eq("Hydropower and Pumped Storage")].utc_hour_start.nunique()==7
    assert f[f.original_fuel_category.eq("Hydropower Excluding Pumped Storage")].utc_hour_start.nunique()==161
    assert f[f.original_fuel_category.eq("Wind with Integrated Battery Storage")].utc_hour_start.nunique()==161
