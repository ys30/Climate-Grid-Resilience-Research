import csv
import pandas as pd
import pytest

from grid_resilience.paperc_2024_bilateral_exchange_gate import audit

BAS = ("AZPS", "BPAT", "CISO", "SRP")
TIME = "UTC Time at End of Hour"


def inputs(tmp_path, missing_total=False, missing_bilateral=False, duplicate=False):
    times = pd.date_range("2024-07-01T00:00:00Z", periods=168, freq="h")
    balance, bilateral = {}, {}
    for label, timeslice in (("Jan_Jun", times[:7]), ("Jul_Dec", times[7:])):
        b = tmp_path / ("balance_" + label + ".csv")
        i = tmp_path / ("interchange_" + label + ".csv")
        with b.open("w", newline="") as fb, i.open("w", newline="") as fi:
            wb=csv.DictWriter(fb,fieldnames=["Balancing Authority",TIME,"Total Interchange (MW)"])
            wi=csv.DictWriter(fi,fieldnames=["Balancing Authority",TIME,
                    "Directly Interconnected Balancing Authority","Interchange (MW)"])
            wb.writeheader()
            wi.writeheader()
            for idx,t in enumerate(timeslice):
                for ba in BAS:
                    hour=(t+pd.Timedelta(hours=1)).strftime("%m/%d/%Y %I:%M:%S %p")
                    absent=missing_total and ba=="CISO" and idx==0
                    wb.writerow({"Balancing Authority":ba,TIME:hour,
                                 "Total Interchange (MW)":"" if absent else "15"})
                    if not (missing_bilateral and ba=="BPAT" and idx==0):
                        item={"Balancing Authority":ba,TIME:hour,
                              "Directly Interconnected Balancing Authority":"SAMPLE",
                              "Interchange (MW)":"15"}
                        wi.writerow(item)
                        if duplicate and ba=="AZPS" and idx==0:
                            wi.writerow(item)
        balance[label]=b
        bilateral[label]=i
    return balance,bilateral


def test_full_hourly_reporting_agreement(tmp_path):
    rows, s, scope = audit(*inputs(tmp_path))
    assert len(rows)==672 and len(s)==4
    assert s.matched_reported_hours.eq(168).all()
    assert s.matched_absolute_difference_mwh.eq(0).all()
    assert not scope["historical_grid_adequacy_or_eens_validated"]


def test_reported_total_missing_bilateral_not_substituted(tmp_path):
    rows,s,_=audit(*inputs(tmp_path,missing_total=True))
    c=s.loc[s.ba.eq("CISO")].iloc[0]
    assert c.missing_total_interchange_hours==2
    assert c.missing_total_but_bilateral_observed_hours==2
    assert c.matched_reported_hours==166
    assert rows.loc[(rows.ba=="CISO")&(~rows.balance_total_interchange_reported),
                    "bilateral_minus_reported_total_mw"].isna().all()


def test_bilateral_absence_not_zero(tmp_path):
    rows,s,_=audit(*inputs(tmp_path,missing_bilateral=True))
    bp=s.loc[s.ba.eq("BPAT")].iloc[0]
    assert bp.bilateral_any_counterparty_hours==166
    assert bp.matched_reported_hours==166
    assert rows.loc[(rows.ba=="BPAT")&(~rows.bilateral_ba_hour_present),
                    "sum_reported_bilateral_mw"].isna().all()


def test_duplicate_counterparty_rejected(tmp_path):
    with pytest.raises(ValueError,match="Duplicate BA/hour/counterparty"):
        audit(*inputs(tmp_path,duplicate=True))


def test_missing_balance_hour_rejected(tmp_path):
    b,i=inputs(tmp_path)
    path=b["Jul_Dec"]
    with path.open() as f:
        lines=f.readlines()
    path.write_text("".join(lines[:-1]))
    with pytest.raises(ValueError,match="Incomplete original"):
        audit(b,i)
