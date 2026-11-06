"""Scope-safety diagnostics: project-wide pumping is not PS-only charging.

No disaggregation is inferred: a hypothetical 314 MW symmetric charger cannot
explain project-wide daily energy above 314*24 MWh, but this does not identify
which equipment consumed the remaining electricity.
"""
import math


def pumping_scope_diagnostic(daily_project_pump_mwh, assumed_ps_charge_mw=314.0):
    values = [float(v) for v in daily_project_pump_mwh]
    power = float(assumed_ps_charge_mw)
    if not values or not math.isfinite(power) or power <= 0:
        raise ValueError("Require observed daily MWh and positive assumed MW")
    if any(not math.isfinite(v) or v < 0 for v in values):
        raise ValueError("Observed daily pumping MWh must be finite and nonnegative")
    daily_envelope = power * 24.0
    exceeding = [i for i, v in enumerate(values) if v > daily_envelope + 1e-9]
    return {
        "project_pumping_observation_days": len(values),
        "project_pumping_reported_total_mwh": sum(values),
        "project_pumping_reported_daily_max_mwh": max(values),
        "ps_charging_mw_is_assumed_not_measured": power,
        "hypothetical_ps_only_max_daily_charge_mwh": daily_envelope,
        "project_daily_energy_above_hypothetical_ps_envelope_days": len(exceeding),
        "project_daily_peak_minus_ps_envelope_mwh": max(values) - daily_envelope,
        "project_daily_peak_to_ps_envelope_ratio": max(values) / daily_envelope,
        "project_wide_pumping_is_ps_unit_charging": False,
        "ps_charge_energy_disaggregated": False,
        "water_balance_or_efficiency_calibrated": False,
        "note": "Envelope comparison is a model-scope inconsistency check only; it cannot assign electricity to individual pump types or establish PS usable stored energy.",
    }
