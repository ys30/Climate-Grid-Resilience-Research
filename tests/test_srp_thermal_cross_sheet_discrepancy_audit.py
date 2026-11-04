import pandas as pd
import pytest
from grid_resilience.srp_thermal_cross_sheet_discrepancy_audit import analyze


def records():
    rows=[]
    for month in ("2024-01","2024-07"):
        for plant,tech,cap,p1,p4 in (
            ("101","gas",100.,True,True),
            ("102","gas",50.,True,False),
            ("103","coal",80.,True,True)):
            rows.append({"period":month,"plant_id":plant,"technology":tech,
                "nameplate_mw":cap,"page1_technology_reported":p1,
                "page4_plant_reported":p4,
                "page1_eligible_signed_net_mwh":(120. if plant=="101" else
                    30. if plant=="102" else 40.),
                "page4_signed_net_mwh":(100. if plant=="101" else
                    float("nan") if plant=="102" else 45.)})
    return pd.DataFrame(rows)


def test_signed_and_absolute_source_discrepancy_preserved():
    detail,stats,missing,m=analyze(records())
    j=stats.loc[stats.period.eq("2024-01")&stats.technology.eq("gas")].iloc[0]
    assert j.eligible_source_plant_count==2
    assert j.page1_reported_count==2 and j.page4_reported_count==1
    assert j.net_source_difference_mwh==20
    assert j.absolute_source_difference_mwh==20
    assert j.flagged_plant_count==1
    assert len(missing)==2
    assert missing.page4_reported.eq(False).all()
    assert not m["monthly_difference_proves_thermal_derating"]


def test_small_difference_below_tolerance():
    x=records()
    mask=x.plant_id.eq("101")
    x.loc[mask,"page1_eligible_signed_net_mwh"]=100.1
    d,stats,_,_=analyze(x,absolute_tolerance_mwh=1.)
    assert not d.loc[d.plant_id.eq("101"),"flag_material_absolute_difference"].any()


def test_unreported_value_must_be_missing():
    x=records()
    x.loc[x.plant_id.eq("102"),"page4_signed_net_mwh"]=0.
    with pytest.raises(ValueError,match="remain missing"):
        analyze(x)


def test_duplicate_source_identity_rejected():
    x=records()
    with pytest.raises(ValueError,match="Duplicate"):
        analyze(pd.concat([x,x.iloc[[0]]],ignore_index=True))


def test_nonfinite_reported_source_rejected():
    x=records()
    x.loc[0,"page1_eligible_signed_net_mwh"]=float("nan")
    with pytest.raises(ValueError,match="Reported source"):
        analyze(x)


def test_bad_scope_rejected():
    x=records()
    x.loc[0,"period"]="2024-03"
    with pytest.raises(ValueError,match="scope"):
        analyze(x)
