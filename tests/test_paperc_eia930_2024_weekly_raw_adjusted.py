import csv
import pandas as pd
import pytest
from grid_resilience.paperc_eia930_2024_weekly_raw_adjusted import compare

BAS=("AZPS","BPAT","CISO","SRP")
FIELDS=("Demand (MW)","Net Generation (MW)","Total Interchange (MW)")


def create(path,times,blank_raw=False,blank_adjusted=False):
    headers=["Balancing Authority","UTC Time at End of Hour",*FIELDS,
             *(c+" (Adjusted)" for c in FIELDS)]
    with path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=headers);writer.writeheader()
        for i,t in enumerate(times):
            for ba in BAS:
                row={"Balancing Authority":ba,
                    "UTC Time at End of Hour":(t+pd.Timedelta(hours=1)).strftime("%m/%d/%Y %I:%M:%S %p")}
                raw=[100,120,20]
                adj=[100,120,20]
                if ba=="BPAT":raw[2]=50
                for c,value in zip(FIELDS,raw):row[c]=value
                for c,value in zip(FIELDS,adj):row[c+" (Adjusted)"]=value
                if blank_raw and ba=="CISO" and i==0:
                    row["Total Interchange (MW)"]=""
                if blank_adjusted and ba=="CISO" and i==0:
                    row["Total Interchange (MW) (Adjusted)"]=""
                writer.writerow(row)


def inputs(tmp_path,blank_raw=False,blank_adjusted=False):
    times=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    a,b=tmp_path/"jan.csv",tmp_path/"jul.csv"
    create(a,times[:7],blank_raw,blank_adjusted)
    create(b,times[7:],blank_raw,blank_adjusted)
    return a,b,times


def test_raw_adjusted_not_substituted_and_missingness_counted(tmp_path):
    a,b,_=inputs(tmp_path,blank_raw=True)
    detail,t,scope=compare(a,b)
    assert len(detail)==672
    c=t.loc[t.ba.eq("CISO")].iloc[0]
    assert c.raw_interchange_missing_hours==2
    assert c.adjusted_interchange_missing_hours==0
    assert c.raw_TI_missing_but_adjusted_present_hours==2
    assert c.raw_complete_triplet_hours==166
    assert c.adjusted_complete_triplet_hours==168
    bp=t.loc[t.ba.eq("BPAT")].iloc[0]
    assert bp.raw_nonclosing_evaluable_hours==168
    assert bp.adjusted_closing_hours==168
    assert not bp.original_generator_population_calibrated
    assert scope["never_substitute_adjusted_for_missing_raw"]


def test_missing_adjusted_is_not_imputed(tmp_path):
    a,b,_=inputs(tmp_path,blank_adjusted=True)
    _,t,_=compare(a,b)
    c=t.loc[t.ba.eq("CISO")].iloc[0]
    assert c.adjusted_complete_triplet_hours==166
    assert c.raw_complete_triplet_hours==168


def test_missing_source_hour_rejected(tmp_path):
    a,b,times=inputs(tmp_path)
    create(b,times[8:])
    with pytest.raises(ValueError,match="Missing official"):
        compare(a,b)


def test_source_overlap_rejected(tmp_path):
    a,b,times=inputs(tmp_path)
    create(b,times[6:])
    with pytest.raises(ValueError,match="Overlapping"):
        compare(a,b)
