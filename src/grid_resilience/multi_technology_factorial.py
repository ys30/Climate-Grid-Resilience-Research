"""Run matched four-way multi-technology scenarios and compute interaction.

Inputs are externally prepared. This experiment does not certify calibration.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .multi_technology_scenarios import prepare_scenarios, SCENARIOS
from .multi_technology_dispatch import solve

def run(demand, weather, capacity, availability, output, links=None, event_id="event", storage=None):
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    inputs = out / "scenario_inputs"
    settings = prepare_scenarios(demand, weather, availability, inputs)
    frames = []
    for scenario in SCENARIOS:
        folder = out / "solved" / scenario
        result = solve(inputs / scenario / "demand.csv", capacity,
                       inputs / scenario / "availability.csv", folder,
                       links_csv=links, storage_csv=storage)
        result = result.copy()
        result["scenario"] = scenario
        result["event_id"] = event_id
        frames.append(result)
    combined = pd.concat(frames, ignore_index=True)
    if combined.duplicated(["scenario", "ba"]).any():
        raise ValueError("Duplicate scenario/BA")
    names = set(combined.scenario)
    if names != set(SCENARIOS):
        raise ValueError("Missing factorial scenarios")
    piv = combined.pivot(index="ba", columns="scenario", values="unserved_energy_mwh")
    if piv.isna().any().any() or len(combined) != len(piv) * 4:
        raise ValueError("Incomplete factorial output")
    interaction = (piv["heat_wind"] - piv["heat_only"] -
                   piv["wind_only"] + piv["baseline"])
    summary = interaction.rename("nonadditive_interaction_mwh").reset_index()
    summary.insert(0, "event_id", event_id)
    combined.to_csv(out / "multi_technology_factorial_dispatch.csv", index=False)
    summary.to_csv(out / "multi_technology_interactions.csv", index=False)
    manifest = {
        "event_id": event_id, "scenario_assumptions": settings,
        "network_classification": "hypothetical_transfer_link" if links is not None else "isolated_bas",
        "storage_classification": "assumed_fixed_initial_soc" if storage is not None else "absent",
        "status": "four_matched_synthetic_or_supplied_scenario_solves_not_historically_calibrated",
        "generation_calibration_certified": False,
        "n_bas": len(piv),
        "total_nonadditive_interaction_mwh": float(interaction.sum()),
    }
    (out / "multi_technology_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest

def main():
    p = argparse.ArgumentParser()
    for name in ("demand", "weather", "capacity", "availability", "output"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--links")
    p.add_argument("--storage")
    p.add_argument("--event-id", default="event")
    a = p.parse_args()
    print(json.dumps(run(a.demand, a.weather, a.capacity, a.availability,
                         a.output, a.links, a.event_id, a.storage), indent=2))

if __name__ == "__main__":
    main()
