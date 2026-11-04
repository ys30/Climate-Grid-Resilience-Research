import pandas as pd
import pytest
from grid_resilience.srp_epa_2024_az_hourly_admission import audit_csv


def csv_data(tmp_path):
    p=tmp_path/"2024_az_hourly.csv"
    pd.DataFrame([
        {"facilityId":"141","unitId":"A","Date":"2024-07-01","Gross Load (MW)":10,"Heat Input (mmBtu)":12},
        {"facilityId":"141","unitId":"B","Date":"2024-07-01","grossLoad":11,"heatInput":13},
        {"facilityId":"141","unitId":"A","Date":"2024-07-01","grossLoad":15,"heatInput":14},
        {"facilityId":"55129","unitId":"C","Date":"2024-07-01","grossLoad":20,"heatInput":24},
        {"facilityId":"888","unitId":"X","Date":"2024-07-01","grossLoad":21,"heatInput":29}
    ]).assign(Hour=[0,1,2,3,4]).to_csv(p,index=False)
    return p


def test_source_unit_identity_is_not_gen_electric_output(tmp_path):
    u,s,m=audit_csv(csv_data(tmp_path))
    assert len(u)==3
    assert s.loc[s.oris=="141","source_hourly_rows"].iloc[0]==3
    assert s.loc[s.oris=="141","distinct_epa_unit_ids"].iloc[0]==2
    assert s.loc[s.oris=="147","source_hourly_rows"].iloc[0]==0
    assert not m["unit_level_hourly_net_mw_verified"]
    assert not m["target_eia860_gt_generators_automatically_matched"]
    assert m["rows_at_target_facilities"]==4


def test_invalid_csv_facility_key_rejected(tmp_path):
    p=csv_data(tmp_path)
    d=pd.read_csv(p).rename(columns={"facilityId":"ambiguousID"})
    d.to_csv(p,index=False)
    with pytest.raises(ValueError,match="facility identifier"):
        audit_csv(p)


def test_missing_unit_id_rejected(tmp_path):
    p=csv_data(tmp_path)
    d=pd.read_csv(p)
    d.loc[0,"unitId"]=None
    d.to_csv(p,index=False)
    with pytest.raises(ValueError,match="unit ID"):
        audit_csv(p)


def test_non_2024_target_record_rejected(tmp_path):
    p=csv_data(tmp_path)
    d=pd.read_csv(p)
    d.loc[0,"Date"]="2025-07-01"
    d.to_csv(p,index=False)
    with pytest.raises(ValueError,match="non-2024"):
        audit_csv(p)


def test_no_target_records_is_evidence_gap_not_zero_operations(tmp_path):
    p=csv_data(tmp_path)
    d=pd.read_csv(p)
    d["facilityId"]="888"
    d.to_csv(p,index=False)
    _,s,m=audit_csv(p)
    assert s.source_hourly_rows.eq(0).all()
    assert m["missing_facility_emissions_is_not_outage"]


def test_duplicate_unit_calendar_hour_rejected(tmp_path):
    p=csv_data(tmp_path)
    d=pd.read_csv(p)
    d.loc[2,"Hour"]=0
    d.to_csv(p,index=False)
    with pytest.raises(ValueError,match="Duplicate EPA unit"):
        audit_csv(p)


def test_invalid_operating_hour_rejected(tmp_path):
    p=csv_data(tmp_path)
    d=pd.read_csv(p)
    d.loc[0,"Hour"]=24
    d.to_csv(p,index=False)
    with pytest.raises(ValueError,match="Invalid EPA hourly"):
        audit_csv(p)
