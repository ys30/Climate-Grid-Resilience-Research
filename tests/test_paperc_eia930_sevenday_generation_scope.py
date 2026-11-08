import csv
from datetime import timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from grid_resilience.eia930_fuel_decomposition import FUELS
from grid_resilience.paperc_eia930_sevenday_generation_scope import extract,model_comparison,BAS


def official_fixture(tmp_path,blank=False,missing=False):
    target=tmp_path/"source.csv"
    header=["Balancing Authority","UTC Time at End of Hour","Net Generation (MW)"]+[
        "Net Generation (MW) from "+f for f in FUELS]
    times=pd.date_range("2023-07-10T00:00:00Z",periods=168,freq="h")
    with target.open("w",newline="") as f:
        writer=csv.writer(f);writer.writerow(header)
        for t in times:
            for ba in BAS:
                if missing and t==times[-1] and ba=="SRP":continue
                vals=["10"]*len(FUELS)
                if blank and t==times[0] and ba=="AZPS":
                    vals[FUELS.index("Natural Gas")]=""
                writer.writerow([ba,(t+pd.Timedelta(hours=1)).strftime("%m/%d/%Y %I:%M:%S %p"),"90"]+vals)
    return target


def modeled_fixture():
    times=pd.date_range("2023-07-10T00:00:00Z",periods=168,freq="h")
    return pd.DataFrame([{"timestamp":t.isoformat(),"ba":ba,"scenario":"baseline",
        "technology":tech,"generation_mwh":2.0}
        for t in times for ba in BAS for tech in ("wind","generic_thermal_proxy")])


def test_exact_hour_ending_alignment_and_full_fuel(tmp_path):
    x=extract(official_fixture(tmp_path),"2023-07-10T00:00:00Z")
    assert len(x)==4*len(FUELS)
    assert x.reported_hours.eq(168).all()
    assert x.observed_full_period_mwh.eq(1680).all()
    assert x.official_ba_net_generation_mwh.eq(15120).all()


def test_missing_fuel_remains_missing_not_zero(tmp_path):
    x=extract(official_fixture(tmp_path,blank=True),"2023-07-10T00:00:00Z")
    z=x.loc[x.ba.eq("AZPS") & x.fuel.eq("Natural Gas")].iloc[0]
    assert z.reported_hours==167 and z.blank_hours==1
    assert np.isnan(z.observed_full_period_mwh)
    assert z.signed_observed_mwh_reported_hours_only==1670


def test_missing_ba_hour_fails_closed(tmp_path):
    with pytest.raises(ValueError,match="Incomplete official"):
        extract(official_fixture(tmp_path,missing=True),"2023-07-10T00:00:00Z")


def test_model_output_separate_from_observed_scope(tmp_path):
    obs=extract(official_fixture(tmp_path),"2023-07-10T00:00:00Z")
    out=model_comparison(obs,modeled_fixture(),2023,"isolated")
    assert len(out)==36
    assert not out.actual_generation_coverage_fraction_certified.any()
    assert out.loc[out.fuel.eq("Natural Gas"),"modeled_baseline_mwh"].eq(336).all()
    assert out.loc[out.fuel.eq("Solar"),"modeled_baseline_mwh"].isna().all()


def test_missing_modeled_hour_rejected(tmp_path):
    obs=extract(official_fixture(tmp_path),"2023-07-10T00:00:00Z")
    with pytest.raises(ValueError,match="complete"):
        model_comparison(obs,modeled_fixture().iloc[:-1],2023,"isolated")

def test_2024_split_wind_hydro_storage_schema_preserved(tmp_path):
    source=official_fixture(tmp_path)
    old=["Net Generation (MW) from "+f for f in FUELS]
    new=[
        "Net Generation (MW) from Coal","Net Generation (MW) from Natural Gas",
        "Net Generation (MW) from Nuclear","Net Generation (MW) from All Petroleum Products",
        "Net Generation (MW) from Hydropower Excluding Pumped Storage",
        "Net Generation (MW) from Pumped Storage",
        "Net Generation (MW) from Solar without Integrated Battery Storage",
        "Net Generation (MW) from Solar with Integrated Battery Storage",
        "Net Generation (MW) from Wind without Integrated Battery Storage",
        "Net Generation (MW) from Wind with Integrated Battery Storage",
        "Net Generation (MW) from Battery Storage",
        "Net Generation (MW) from Other Energy Storage",
        "Net Generation (MW) from Unknown Energy Storage",
        "Net Generation (MW) from Geothermal",
        "Net Generation (MW) from Other Fuel Sources",
        "Net Generation (MW) from Unknown Fuel Sources"]
    import csv as csvmod
    with source.open(newline="") as f:
        original=list(csvmod.DictReader(f))
    newpath=tmp_path/"split.csv"
    with newpath.open("w",newline="") as f:
        w=csvmod.DictWriter(f,fieldnames=[
            "Balancing Authority","UTC Time at End of Hour","Net Generation (MW)"]+new)
        w.writeheader()
        for row in original:
            out={k:row[k] for k in (
                "Balancing Authority","UTC Time at End of Hour","Net Generation (MW)")}
            out.update({key:"1" for key in new})
            w.writerow(out)
    x=extract(newpath,"2023-07-10T00:00:00Z")
    assert len(x)==4*len(new)
    assert "Pumped Storage" in set(x.fuel)
    assert "Wind with Integrated Battery Storage" in set(x.fuel)
    assert "Wind" not in set(x.fuel)
    y=model_comparison(x,modeled_fixture(),2023,"isolated")
    assert y.loc[y.fuel.eq("Wind with Integrated Battery Storage"),"modeled_baseline_mwh"].isna().all()
    assert y.loc[y.fuel.eq("Wind without Integrated Battery Storage"),"modeled_baseline_mwh"].notna().all()
