import csv
import pandas as pd
import pytest

from grid_resilience.paperc_eia930_2024_weekly_balance_gate import audit

BAS=("AZPS","BPAT","CISO","SRP")


def write_source(path,dates,missing_ti=False,bpat_offset=False):
    header=["Balancing Authority","UTC Time at End of Hour","Demand (MW)",
            "Net Generation (MW)","Total Interchange (MW)"]
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=header)
        w.writeheader()
        for i,t in enumerate(dates):
            for ba in BAS:
                d=100.0
                ng=120.0
                ti=20.0
                if bpat_offset and ba=="BPAT":ti=60.0
                if missing_ti and ba=="CISO" and i==0:ti=""
                w.writerow({"Balancing Authority":ba,
                    "UTC Time at End of Hour":(t+pd.Timedelta(hours=1)).strftime("%m/%d/%Y %I:%M:%S %p"),
                    "Demand (MW)":d,"Net Generation (MW)":ng,"Total Interchange (MW)":ti})


def sample(tmp_path,missing_ti=False,bpat_offset=False):
    ts=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    a,b=tmp_path/"jan.csv",tmp_path/"jul.csv"
    write_source(a,ts[:7],missing_ti,bpat_offset)
    write_source(b,ts[7:],missing_ti,bpat_offset)
    return a,b,ts


def test_correctly_sourced_complete_balance(tmp_path):
    a,b,_=sample(tmp_path)
    hourly,summary,meta=audit(a,b)
    assert len(hourly)==672
    assert len(summary)==4
    assert summary.source_hours.eq(168).all()
    assert summary.jan_jun_hours.eq(7).all()
    assert summary.jul_dec_hours.eq(161).all()
    assert summary.hourly_arithmetic_closing_hours.eq(168).all()
    assert summary.signed_raw_residual_valid_hours_mwh.eq(0).all()
    assert not summary.historical_supply_adequacy_calibrated.any()
    assert meta["historical_energy_not_served_estimated"] is False


def test_sign_convention_nonclosing_is_diagnostic(tmp_path):
    a,b,_=sample(tmp_path,bpat_offset=True)
    _,summary,_=audit(a,b)
    bp=summary.loc[summary.ba.eq("BPAT")].iloc[0]
    assert bp.hourly_arithmetic_nonclosing_hours==168
    assert bp.signed_raw_residual_valid_hours_mwh==-6720
    assert not bp.all_raw_hours_close


def test_missing_ti_not_silently_zeroed(tmp_path):
    a,b,_=sample(tmp_path,missing_ti=True)
    hourly,summary,_=audit(a,b)
    c=summary.loc[summary.ba.eq("CISO")].iloc[0]
    assert c.missing_raw_total_interchange_hours==2
    assert c.triplet_complete_hours==166
    assert c.hourly_arithmetic_closing_hours==166
    assert not c.all_raw_triplets_complete
    assert hourly.loc[~hourly.raw_triplet_present,"raw_generation_minus_demand_minus_interchange_mw"].isna().all()


def test_missing_official_source_hour_rejected(tmp_path):
    a,b,ts=sample(tmp_path)
    write_source(b,ts[8:])
    with pytest.raises(ValueError,match="incomplete"):
        audit(a,b)


def test_duplicate_source_hour_rejected(tmp_path):
    a,b,ts=sample(tmp_path)
    write_source(b,ts[6:])
    with pytest.raises(ValueError,match="Overlapping"):
        audit(a,b)
