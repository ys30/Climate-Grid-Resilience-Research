import pandas as pd
import pytest
from grid_resilience.srp_ecmps_2024_plan_evidence_gate import audit


def examples():
    return pd.DataFrame({
        "facility_id": ["141", "141", "55129", "147"],
        "epa_unit_id": ["7", "7", "DBG4", "K-7"],
        "stack_pipe_id": ["CS1", "CS2", "CP1", "MS1"],
        "begin_date": ["2023-01-01", "2024-09-01", "2024-07-15", "2022-01-01"],
        "end_date": ["2024-07-10", None, None, None],
        "source_plan_id": ["plan1", "plan2", "plan3", "plan4"],
        "source_url": ["https://example.org/plan"] * 4,
        "source_sha256": ["a" * 64] * 4,
    })


def test_admit_only_historically_effective_monitoring_relationships():
    detail, summary, meta = audit(examples())
    assert len(detail) == 3
    assert detail.loc[detail.epa_unit_id.eq("7"), "stack_pipe_id"].tolist() == ["CS1"]
    assert len(summary) == 10
    assert summary.dated_ecmps_relationship_rows.sum() == 3
    assert not summary.unique_eia_generator_identity_confirmed.any()
    assert not meta["temperature_derating_or_outage_identified"]


def test_prior_monitoring_plan_not_active():
    x = examples()
    x.loc[0, "end_date"] = "2024-06-30"
    _, summary, _ = audit(x)
    assert not summary.loc[summary.epa_unit_id.eq("7"),
                           "monitoring_plan_location_evidence_admitted"].iloc[0]


def test_reject_missing_primary_source_hash():
    x = examples()
    x.loc[0, "source_sha256"] = "not-sha256"
    with pytest.raises(ValueError, match="SHA256"):
        audit(x)


def test_reject_spurious_generator_name_as_unit():
    x = examples()
    x.loc[0, "epa_unit_id"] = "AF7"
    with pytest.raises(ValueError, match="Unexpected EPA unit"):
        audit(x)


def test_reject_end_prior_to_begin():
    x = examples()
    x.loc[0, "end_date"] = "2022-01-01"
    with pytest.raises(ValueError, match="Invalid plan effective"):
        audit(x)


def test_reject_duplicate_source_relationship():
    x = examples()
    with pytest.raises(ValueError, match="Duplicated monitoring-plan"):
        audit(pd.concat([x, x.iloc[[0]]], ignore_index=True))
