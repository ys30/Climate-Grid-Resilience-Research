import pandas as pd
import pytest
from grid_resilience.srp_epa_2024_identity_evidence_gate import review_queue

UNITS = {"141": ["1", "2", "3", "7", "8"],
         "55129": ["DBG1", "DBG2", "DBG4", "DBG5"],
         "147": ["K-7"]}
MISSING = {("141", "7"), ("141", "8"), ("55129", "DBG4"), ("55129", "DBG5")}


def fixture():
    rows = []
    for p, units in UNITS.items():
        for u in units:
            found = (p, u) not in MISSING
            rows.append({
                "oris": p, "epa_unit_id": u,
                "source_calendar_hour_rows": 8784,
                "direct_static_crosswalk_relationship_count": 1 if found else 0,
                "linked_eia_generator_ids": "X" if found else "",
                "linked_eia_prime_mover_classes": "CT" if found else "",
                "static_crosswalk_unit_found": found,
                "eia860_gt_generator_directly_linked": False,
                "2024_ecmps_monitoring_plan_verified": False,
                "actual_eia_generator_net_mw_validated": False,
            })
    return pd.DataFrame(rows)


def test_only_static_evidence_and_explicit_no_calibration():
    queue, report = review_queue(fixture())
    assert len(queue) == 10
    assert report["epa_units_with_static_crosswalk"] == 6
    assert report["epa_units_without_static_crosswalk"] == 4
    assert report["eligible_generator_level_net_mw_calibrations"] == 0
    assert queue.loc[queue.priority.eq("P0_missing_static_link")].shape[0] == 4
    assert not queue.temperature_derating_calibration_allowed.any()


def test_reject_missing_epa_unit():
    with pytest.raises(ValueError, match="10 EPA"):
        review_queue(fixture().iloc[:-1])


def test_reject_fabricated_2024_plan_verification():
    x = fixture()
    x.loc[0, "2024_ecmps_monitoring_plan_verified"] = True
    with pytest.raises(ValueError, match="cannot certify 2024"):
        review_queue(x)


def test_reject_unsubstantiated_gt_identity():
    x = fixture()
    x.loc[0, "eia860_gt_generator_directly_linked"] = True
    with pytest.raises(ValueError, match="GT identity"):
        review_queue(x)


def test_reject_fabricated_net_mw():
    x = fixture()
    x.loc[0, "actual_eia_generator_net_mw_validated"] = True
    with pytest.raises(ValueError, match="net electrical MW"):
        review_queue(x)


def test_reject_conflicting_static_counts():
    x = fixture()
    x.loc[0, "direct_static_crosswalk_relationship_count"] = 0
    with pytest.raises(ValueError, match="counts inconsistent"):
        review_queue(x)


def test_reject_missing_year_coverage():
    x = fixture()
    x.loc[0, "source_calendar_hour_rows"] = 744
    with pytest.raises(ValueError, match="annual source calendar"):
        review_queue(x)
