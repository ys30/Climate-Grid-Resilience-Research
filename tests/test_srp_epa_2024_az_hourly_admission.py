import pandas as pd
import pytest
from grid_resilience.srp_epa_2024_az_hourly_admission import audit_csv


def csv_data(tmp_path):
    p=tmp_path/"2024_az_hourly.csv"
    pd.DataFrame([
        {"facilityId":"141","unitId":"A","year":2024,"grossLoad":10,"heatInput":12},
        {"facilityId":"141","unitId":"B","year":2024,"grossLoad":11,"heatInput":13},
        {"facilityId":"141","unitId":"A","year":2024,"grossLoad":15,"heatInput":14},
        {"facilityId":"55129","unitId":"C","year":2024,"grossLoad":20,"heatInput":24},
        {"facilityId":"888","unitId":"X","year":2024,"grossLoad":21,"heatInput":29}
    ]).to_csv(p,index=False)
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
    d.loc[0,"year"]=2025
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
