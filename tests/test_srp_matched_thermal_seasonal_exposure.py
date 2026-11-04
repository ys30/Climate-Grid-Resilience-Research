import pandas as pd
import pytest
from grid_resilience.srp_matched_thermal_seasonal_exposure import compare


def example(month,extra=False):
    t=pd.date_range(f"2024-{month:02d}-01",periods=744,freq="h",tz="UTC")
    sites=[("gas","1",100.,10. if month==1 else 35.),
           ("coal","2",50.,2. if month==1 else 25.)]
    if extra:sites.append(("gas","3",200.,36.))
    return pd.concat([pd.DataFrame({
        "timestamp_utc":t,"technology":tech,"plant_id":plant,
        "temperature_2m_c":temp,"selected_nameplate_mw":mw})
        for tech,plant,mw,temp in sites],ignore_index=True)


def test_matched_only_same_sites_not_july_only_gas():
    table,h,plants,diff,m=compare(example(1),example(7,extra=True))
    assert m["matched_gas_plants"]==1 and m["july_only_gas_plants"]==1
    assert m["matched_gas_nameplate_mw"]==100.
    gas=table[(table.technology=="gas")&(table.month=="July")].iloc[0]
    assert gas.capacity_weighted_mean_temp_c==35.
    assert gas.weighted_fleet_hours_ge_35_c==744
    assert gas.weighted_fleet_hours_ge_40_c==0
    assert abs(diff.loc[diff.technology=="gas","july_minus_january_mean_temp_c"].iloc[0]-25)<1e-8
    assert len(h)==744*4 and len(plants)==4
    assert not m["thermal_derating_calibrated"]


def test_mismatched_capacities_fail():
    j=example(1);u=example(7)
    u.loc[u.plant_id.eq("1"),"selected_nameplate_mw"]=110.
    with pytest.raises(ValueError,match="nameplate differs"):
        compare(j,u)


def test_duplicate_monthly_hour_fails():
    j=example(1)
    with pytest.raises(ValueError,match="Duplicate"):
        compare(pd.concat([j,j.iloc[[0]]]),example(7))


def test_missing_source_hour_fails():
    with pytest.raises(ValueError,match="Incomplete UTC"):
        compare(example(1).iloc[1:],example(7))


def test_nonfinite_temperature_fails():
    j=example(1);j.loc[0,"temperature_2m_c"]=float("nan")
    with pytest.raises(ValueError,match="nonfinite"):
        compare(j,example(7))


def test_site_level_capacity_hours_not_fleet_mean_temperature_hours():
    # Two 50 MW gas sites: 30C and 40C. Fleet mean is 35C for all 744h,
    # but only half the installed site capacity actually exceeds 40C.
    t=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    u=pd.date_range("2024-07-01",periods=744,freq="h",tz="UTC")
    def raw(times,month):
        rows=[]
        for tech,plant,mw,temp in (("gas","1",50.,30. if month==1 else 30.),
                                   ("gas","3",50.,40. if month==1 else 42.),
                                   ("coal","2",30.,25. if month==1 else 36.)):
            rows.append(pd.DataFrame({"timestamp_utc":times,"technology":tech,
                "plant_id":plant,"selected_nameplate_mw":mw,"temperature_2m_c":temp}))
        return pd.concat(rows,ignore_index=True)
    result,_,plant,_,manifest=compare(raw(t,1),raw(u,7))
    gas=result[(result.month=="January")&(result.technology=="gas")].iloc[0]
    assert gas.weighted_fleet_hours_ge_35_c==744
    assert gas.site_exposed_nameplate_mwh_ge_35_c==50*744
    assert gas.site_exposed_nameplate_mwh_ge_40_c==50*744
    assert gas.site_capacity_hour_fraction_ge_35_c==.5
    assert gas.site_nameplate_weighted_degree_hours_above_35_c==2.5*744
    assert manifest["plant_level_exposure_not_unit_outage_or_energy_loss"]
