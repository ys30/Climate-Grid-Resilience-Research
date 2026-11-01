"""Regression tests for split EIA-930 wind columns and missing-category disclosure."""
import csv
import json
from datetime import datetime,timedelta,timezone
import pandas as pd
import pytest
from grid_resilience.bpat_wind_observation_audit import audit

BASE="Net Generation (MW) from Wind "
A=BASE+"without Integrated Battery Storage"
B=BASE+"with Integrated Battery Storage"

def make_inputs(tmp_path,category=None):
    balance=tmp_path/"balance.csv";capacity=tmp_path/"capacity.csv"
    pd.DataFrame([{"ba":"BPAT","technology":"wind","nameplate_capacity_mw":100}]).to_csv(capacity,index=False)
    fields=["Balancing Authority","UTC Time at End of Hour",A,A+" (Imputed)",A+" (Adjusted)",B,B+" (Imputed)",B+" (Adjusted)"]
    with balance.open("w",newline="") as fp:
        writer=csv.DictWriter(fp,fieldnames=fields);writer.writeheader()
        for i in range(744):
            t=datetime(2024,7,1,tzinfo=timezone.utc)+timedelta(hours=i+1)
            row={"Balancing Authority":"BPAT","UTC Time at End of Hour":t.strftime("%m/%d/%Y %H:%M:%S"),A:"10",A+" (Adjusted)":"20",B:"",B+" (Adjusted)":""}
            if category=="reported":row[B+" (Adjusted)"]="3"
            writer.writerow(row)
    return balance,capacity

def test_blank_integrated_category_is_audited_not_certified(tmp_path):
    balance,capacity=make_inputs(tmp_path)
    result=audit(balance,capacity,tmp_path/"out",2024,7)
    assert result["hours"]==744
    assert result["reported_eia930_wind_energy_mwh"]==744*20
    assert result["blank_category_hours_assumed_zero"][B]==744
    assert result["blank_category_zero_is_provisional_not_observed"] is True

def test_reported_categories_are_added_once(tmp_path):
    balance,capacity=make_inputs(tmp_path,category="reported")
    result=audit(balance,capacity,tmp_path/"out",2024,7)
    assert result["reported_eia930_wind_energy_mwh"]==744*23
    assert result["blank_category_hours_assumed_zero"][B]==0

def test_omitted_hours_are_not_interpolated(tmp_path):
    balance,capacity=make_inputs(tmp_path)
    frame=pd.read_csv(balance);frame=frame.iloc[7:];frame.to_csv(balance,index=False)
    result=audit(balance,capacity,tmp_path/"out",2024,7)
    assert result["hours"]==737
    assert len(result["missing_timestamp_utc"])==7
    assert result["observed_coverage_fraction"]==pytest.approx(737/744)
