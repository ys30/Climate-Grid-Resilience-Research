import pandas as pd
import pytest
from grid_resilience.srp_thermal_heat_episode_audit import events


def weather():
    t=pd.date_range("2024-07-01",periods=744,freq="h",tz="UTC")
    rows=[]
    for tech in ("gas","coal"):
        temp=[20.]*744
        if tech=="gas":
            temp[0:3]=[36.,37.,38.]
            temp[10:18]=[40.]*8
            temp[500]=45.
        rows.extend({"month":"July","technology":tech,
                     "timestamp_utc":ts,"capacity_weighted_temperature_c":temp[i]}
                    for i,ts in enumerate(t))
    return pd.DataFrame(rows)


def test_disjoint_heat_episodes_and_hour_conservation():
    e,m=events(weather())
    a=m[(m.technology=="gas")&(m.threshold_c==35.)].iloc[0]
    b=m[(m.technology=="gas")&(m.threshold_c==40.)].iloc[0]
    assert a.episode_count==3
    assert a.hot_hours==12
    assert a.longest_episode_hours==8
    assert a.episodes_at_least_6h==1
    assert b.hot_hours==9 and b.episode_count==2
    assert len(e[(e.technology=="gas")&(e.threshold_c==35.)])==3


def test_missing_utc_hour_is_rejected():
    with pytest.raises(ValueError,match="UTC"):
        events(weather().iloc[:-1])


def test_duplicate_source_hour_is_rejected():
    x=weather()
    with pytest.raises(ValueError,match="Duplicate"):
        events(pd.concat([x,x.iloc[[0]]],ignore_index=True))


def test_no_episode_does_not_fail():
    e,m=events(weather().query("technology=='coal'"))
    assert e.empty
    assert m.hot_hours.eq(0).all()
    assert m.longest_episode_hours.eq(0).all()
