import csv
import pandas as pd
import pytest
from grid_resilience.paperc_eia930_2024_reciprocity import audit

HEADER=["Balancing Authority","Directly Interconnected Balancing Authority",
        "UTC Time at End of Hour","Interchange (MW)"]


def fixture(tmp_path,missing_reverse=False,blank_reverse=False,mismatch=False):
    dates=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    a,b=tmp_path/"jan.csv",tmp_path/"jul.csv"
    for f,subset in ((a,dates[:7]),(b,dates[7:])):
        with f.open("w",newline="") as out:
            w=csv.DictWriter(out,fieldnames=HEADER);w.writeheader()
            for i,t in enumerate(subset):
                dt=(t+pd.Timedelta(hours=1)).strftime("%m/%d/%Y %I:%M:%S %p")
                w.writerow(dict(zip(HEADER,["CISO","AZPS",dt,"50"])))
                if not (missing_reverse and i==0):
                    w.writerow(dict(zip(HEADER,["AZPS","CISO",dt,
                        "" if blank_reverse and i==0 else "-48" if mismatch else "-50"])))
                w.writerow(dict(zip(HEADER,["BPAT","EXTERNAL",dt,"10"])))
    return a,b


def test_reciprocal_pair_and_non_reporting_external_partner(tmp_path):
    d,s,m=audit(*fixture(tmp_path))
    x=s[(s.ba_a=="AZPS")&(s.ba_b=="CISO")].iloc[0]
    assert x.observed_pair_hour_keys==168
    assert x.both_directions_reported_hours==168
    assert x.absolute_reciprocity_deviation_valid_hours_mwh==0
    external=s[(s.ba_a=="BPAT")&(s.ba_b=="EXTERNAL")].iloc[0]
    assert external.only_one_direction_or_blank_hours==168
    assert external.absolute_reciprocity_deviation_valid_hours_mwh==0
    assert m["historical_eens_validated"] is False


def test_unreported_counterdirection_not_zero(tmp_path):
    d,s,_=audit(*fixture(tmp_path,missing_reverse=True))
    k=s[(s.ba_a=="AZPS")&(s.ba_b=="CISO")].iloc[0]
    assert k.only_one_direction_or_blank_hours==2
    assert k.both_directions_reported_hours==166
    assert d.loc[~d.both_direction_values_present,"signed_reciprocity_sum_mw"].isna().all()


def test_blank_opposite_value_not_zero(tmp_path):
    _,s,_=audit(*fixture(tmp_path,blank_reverse=True))
    k=s[(s.ba_a=="AZPS")&(s.ba_b=="CISO")].iloc[0]
    assert k.only_one_direction_or_blank_hours==2


def test_nonreciprocal_measured_pair_is_reported_not_rejected(tmp_path):
    _,s,_=audit(*fixture(tmp_path,mismatch=True))
    k=s[(s.ba_a=="AZPS")&(s.ba_b=="CISO")].iloc[0]
    assert k.absolute_reciprocity_deviation_valid_hours_mwh==336
    assert k.reciprocity_within_1mw_hours==0


def test_duplicate_directional_record_rejected(tmp_path):
    a,b=fixture(tmp_path)
    with a.open() as f:lines=f.readlines()
    with a.open("a") as f:f.write(lines[1])
    with pytest.raises(ValueError,match="Duplicate"):
        audit(a,b)
