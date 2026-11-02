"""Attach energy-constrained hydro and pumped storage to an existing PyPSA bus.

This module is for explicit counterfactuals, not calibrated historical dispatch.
"""
from math import sqrt

def add_hy_ps(n, bus, settings, *, prefix="SRP"):
    required={"hydro_nameplate_mw","hydro_monthly_dispatch_budget_mwh",
              "ps_discharge_nameplate_mw","ps_charge_nameplate_mw_assumed",
              "ps_energy_capacity_mwh_assumed","ps_roundtrip_efficiency_assumed"}
    if not required.issubset(settings):raise ValueError("Missing resource assumptions")
    for key in required:
        value=settings[key]
        if not isinstance(value,(int,float)) or value<0:raise ValueError(f"Bad setting {key}")
    efficiency=settings["ps_roundtrip_efficiency_assumed"]
    if not 0<efficiency<=1:raise ValueError("Bad roundtrip efficiency")
    if settings["historical_calibration_certified"] is not False:
        raise ValueError("Scenario must not assert historical calibration")
    if bus not in n.buses.index:raise ValueError("Target BA bus absent")
    hydro_bus=f"{prefix}_hydro_resource";storage_bus=f"{prefix}_ps_resource"
    if hydro_bus in n.buses.index or storage_bus in n.buses.index:
        raise ValueError("Duplicate resource buses")
    n.add("Bus",hydro_bus);n.add("Bus",storage_bus)
    # Reservoir starts with an explicitly assumed energy budget. The Store
    # cannot replenish (no link into hydro bus), and has nonnegative e_t.
    n.add("Store",f"{prefix}_hydro_budget",bus=hydro_bus,
          e_nom=float(settings["hydro_monthly_dispatch_budget_mwh"]),
          e_initial=float(settings["hydro_monthly_dispatch_budget_mwh"]),
          e_cyclic=False)
    n.add("Link",f"{prefix}_hydro_out",bus0=hydro_bus,bus1=bus,
          p_nom=float(settings["hydro_nameplate_mw"]),efficiency=1.0)
    n.add("Store",f"{prefix}_ps_energy",bus=storage_bus,
          e_nom=float(settings["ps_energy_capacity_mwh_assumed"]),
          e_initial=0.0,e_cyclic=True)
    eta=sqrt(efficiency)
    n.add("Link",f"{prefix}_ps_charge",bus0=bus,bus1=storage_bus,
          p_nom=float(settings["ps_charge_nameplate_mw_assumed"]),
          efficiency=eta)
    n.add("Link",f"{prefix}_ps_discharge",bus0=storage_bus,bus1=bus,
          p_nom=float(settings["ps_discharge_nameplate_mw"]),efficiency=eta)
    return {"hydro_link":f"{prefix}_hydro_out","storage_charge_link":f"{prefix}_ps_charge",
            "storage_discharge_link":f"{prefix}_ps_discharge",
            "energy_budget_mwh":float(settings["hydro_monthly_dispatch_budget_mwh"]),
            "storage_e_nom_mwh":float(settings["ps_energy_capacity_mwh_assumed"]),
            "roundtrip_efficiency":float(efficiency),
            "historical_calibration_certified":False}
