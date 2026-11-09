import csv
import json
import pandas as pd
import pytest
from grid_resilience.paperc_caiso_telemetry_vs_rtd import telemetry,comparison

def fixture(tmp_path):
    files={}
    rows=[]
    for year,start in ((2023,"2023-07-10T00:00:00Z"),(2024,"2024-07-01T00:00:00Z")):
        utc=pd.date_range(start,periods=2016,freq="5min")
        dates=sorted(set(x.tz_convert("America/Los_Angeles").strftime("%Y-%m-%d") for x in utc))
        files[year]={}
        for day in dates:
            ts=[x.tz_convert("America/Los_Angeles") for x in utc if x.tz_convert("America/Los_Angeles").strftime("%Y-%m-%d")==day]
            bat=tmp_path/f"bat_{year}_{day}.csv"
            fuel=tmp_path/f"fuel_{year}_{day}.csv"
            with bat.open("w",newline="") as f, fuel.open("w",newline="") as g:
                bw=csv.writer(f);fw=csv.writer(g)
                bw.writerow(["Time","Total batteries","Stand-alone batteries","Hybrid batteries"])
                fw.writerow(["Time","Batteries"])
                for local in ts:
                    t=local.strftime("%H:%M")
                    bw.writerow([t,50,40,10]);fw.writerow([t,50])
            files[year][day]={"storage":str(bat),"fuelsource":str(fuel)}
        for k,u in enumerate(utc):
            if year==2023 and k==500:continue
            hour=u.floor("h")
            rows.append({"eia930_study_year":year,"market":"RTD",
                "resource_type":"LESR","output_type":"EN",
                "utc_hour_start_from_local_trade_date":hour.isoformat(),
                "interval_index":int((u-hour).total_seconds()//300)+1,
                "original_market_value":30})
    return files,pd.DataFrame(rows)

def test_full_utc_coverage_and_scope_safe_market_comparison(tmp_path):
    files,market=fixture(tmp_path)
    telemetry_df,day=telemetry(files)
    assert len(telemetry_df)==4032
    assert len(day)==16
    assert telemetry_df.fuel_storage_same_source_reading.all()
    d,summary,scope=comparison(telemetry_df,market)
    assert summary.set_index("year").rtd_market_missing_intervals.to_dict()=={2023:1,2024:0}
    assert summary.rtd_market_exact_utc_matched_intervals.sum()==4031
    assert not summary.instrument_and_resource_population_identical.any()
    assert scope["no_imputed_2023_missing_rtd_market_intervals"]

def test_source_csv_unavailable_is_not_silently_imputed(tmp_path):
    files,market=fixture(tmp_path)
    a=files[2024][sorted(files[2024])[0]]["storage"]
    with open(a,"w") as f:f.write("Time,Missing\n00:00,3\n")
    with pytest.raises(ValueError,match="columns"):
        telemetry(files)

def test_duplicate_utc_market_source_intervals_rejected(tmp_path):
    files,market=fixture(tmp_path)
    t,_=telemetry(files)
    market=pd.concat([market,market.iloc[[0]]],ignore_index=True)
    with pytest.raises(ValueError,match="duplicate"):
        comparison(t,market)
