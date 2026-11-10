# Paper C — Source-solver archive inventory and clean manuscript release check (2026-11-10)

**Status:** Exact GitHub Actions original-solver ZIP artifacts retrieved and independently inventoried, *not* rerun; clean private manuscript generated. **No DOI deposited, no exact software environment lock, no source redistribution license review completed.**

## Archived original model provenance

| Model family | Exact successful historical run | Original artifact ID | Historical code commit | Contents inventoried |
|---|---|---:|---|---:|
| July 2024 four × 168h original solver | [42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361) | 13451375705 | `6831206284ffa86f176974972314038f49e7794f` | 17 original ZIP members |
| Distinct-year July 2023 vs July 2024 model | [42419234209](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42419234209) | 13592962046 | `35ba7bf2edb46659895a9ff9b9fb860215c4dd20` | 26 original ZIP members |
| Grand Coulee continuous 672h HY + hypothetical PS model | [42130327635](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42130327635) | 13462104608 | `aca4b93ecd69790708bafdcf5ef3a9c5c6ab0a9c` | 7 original ZIP members |

Four original result figures contribute 8 separate PNG/PDF masters. **Total 58 file-level SHA256 member entries** archived in a private review bundle along with the exact original solver ZIP bytes. ZIP compilation SHA256: `d447a74e18662a381d1eac75acb1ff04b031ec2ca4c8af8bbf513a94ce201cde`.

**Important:** The publication/bundle file here has **not** been uploaded to this public GitHub repository or Zenodo; this README only records verification provenance. The model archives contain original-model input subsets and may carry upstream provider attribution or redistribution restrictions. Check source licenses before public data release.

## Scientific and reproducibility scope

- Original four-week files include verified 2024 source intake manifests, four weekly original weather/demand windows, frozen hypothetical links and original summary/model outputs. The distinct-year archive contains both original source and model run manifests, input provenance and factored output. Grand Coulee original archive contains four-assumed-access scenario results, model scope and 672h series.
- The 2023/2024 source comparison **reuses the same 2024 July 1–7 result** as the four-week study, and the 672h Grand Coulee resource configuration is not directly comparable to the independent 168h four-week model. The [original-anchor bridge](PROJECT_C_CROSSYEAR_FOURWEEK_SHARED_2024_ANCHOR_CI_VERIFIED.md) verified zero difference for the common model outcome.
- Original runs record code identities but do not include a complete pip-freeze/locked highspy/pypsa version set. Running current `pip freeze` would report the wrong environment. This archive is an **original results evidence inventory**, not verified executable bitwise reproduction.
- No complete historical BA fleet, source-calibrated interties, operator-authorized PG7–PG12 power/SOC, original complete fuel data or actual EENS/outage measurement is established. **Do not claim calibrated physical climate grid reliability.**

## Private manuscript separation

A new v9 paper-only draft retains the title, Abstract, Introduction, Methods, Results, Discussion, Conclusions, 5 actual embedded source figures, 3 scientific tables, Data/code availability, and six bibliography entries; the internal editorial appendices were excluded. The private manuscript remains a **pre-submission draft**: third-party software version lock and provider licensing must be closed before any reproducibility DOI, and source calibration remains a substantive scientific limitation.

See [original SHA and formula audit](PROJECT_C_PAPER_SOURCE_CODE_FORMULAS_EXECUTION_SHA_FREEZE_AUDIT_2026_11_10.md) for source code and claims.
