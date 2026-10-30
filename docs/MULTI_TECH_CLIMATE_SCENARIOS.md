# Matched multi-technology climate scenarios (V2)

This module creates four matched input datasets: baseline, heat only, low wind only, and combined heat + low wind. It does **not** replace the validated legacy partial-fleet factorial experiment.

```bash
python -m grid_resilience.multi_technology_scenarios \
  --demand INPUT_DEMAND.csv --weather INPUT_WEATHER.csv \
  --availability INPUT_TECH_HOURLY_AVAILABILITY.csv \
  --output outputs/multi_technology_scenarios
```

Each scenario gets `demand.csv` and `availability.csv` compatible with the isolated `multi_technology_dispatch.solve` interface. A synthetic/default 4°C heat increase changes demand only above 30°C, with a 1.2% increment for each degree of newly added excess heat. Low wind multiplies supplied wind availability by 0.7, leaving other technologies unchanged. These are **stipulated screening assumptions**, not observed impacts. To compare scenario dispatch runs, use exactly the same capacity input and link input for all four cases.

**Remaining research tasks:** establish robust external BA/technology classification and hourly availability, complete generator fleet, storage energy/SOC, physically justified transmission limits, a four-solve orchestration with linked results, EIA-923 validation over matching full periods, and holdout event analysis. The existing one-week event is not comparable to a full monthly EIA-923 total.
