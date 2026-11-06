import pytest
from grid_resilience.grand_coulee_pumping_scope_gate import pumping_scope_diagnostic


def test_2024_official_project_daily_peak_exceeds_hypothetical_ps_envelope():
    # Source-audited peak from July 2024; NOT a complete daily dataset.
    x = pumping_scope_diagnostic([10735.0], 314)
    assert x["hypothetical_ps_only_max_daily_charge_mwh"] == 7536.0
    assert x["project_daily_peak_minus_ps_envelope_mwh"] == 3199.0
    assert x["project_daily_energy_above_hypothetical_ps_envelope_days"] == 1
    assert not x["ps_charge_energy_disaggregated"]
    assert not x["water_balance_or_efficiency_calibrated"]


def test_within_envelope_does_not_certify_ps_identity():
    x = pumping_scope_diagnostic([1000, 2000], 314)
    assert x["project_daily_energy_above_hypothetical_ps_envelope_days"] == 0
    assert x["project_wide_pumping_is_ps_unit_charging"] is False


@pytest.mark.parametrize("values,power", [([],314),([-1],314),([float("nan")],314),([10],0),([10],float("inf"))])
def test_invalid_scope_inputs_rejected(values,power):
    with pytest.raises(ValueError):
        pumping_scope_diagnostic(values,power)
