# Technology-resolved capacity preparation (V2)

The legacy factorial solver still uses a **generic thermal proxy + wind**. The new `technology_capacity` module is an **independent validation step**, not yet connected to dispatch. It accepts audited upstream BA/technology inventory totals with columns `ba,technology,capacity_mw,source_year,capacity_source`.

Supported labels: gas, coal, nuclear, hydro, solar, wind, geothermal, oil, biomass, storage, other. Broad `thermal` is explicitly rejected: splitting coal and gas requires actual plant-level fuel classifications rather than an invented allocation.

```bash
python -m grid_resilience.technology_capacity --source inputs/audited_technology_capacity.csv --output outputs/technology_capacity --expected-year 2024 --expected-bas CISO AZPS BPAT SRP
python -m pytest -q
```

Outputs: an unchanged audited-input projection, plus `technology_capacity_manifest.json` containing absent BA/technology combinations. **Missing categories are not automatically zero**. Reconcile them with upstream records before marking a technology inventory complete. The validator does not create capacity-factor profiles, operating costs, storage energy capacity/SOC, or calibrated transmission data, and does not change the historical screening results.

Next integration: audited EIA-860 plant-fuel crosswalk, BA-specific hourly renewable availability, plant-level thermal availability, and an independent PyPSA multi-technology solve behind separate tests.
