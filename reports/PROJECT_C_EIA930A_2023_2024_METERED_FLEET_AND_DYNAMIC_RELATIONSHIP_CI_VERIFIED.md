# Paper C — Original EIA-930A 2023–2024 reporting-fleet and declared dynamic relationship admission

## Source-provenance result

**Official source:** [EIA-930 data definitions and annual EIA-930A XLS files](https://www.eia.gov/electricity/930-content/about.html). EIA states that EIA-930A inventories generators in EIA-860 identifiers appearing in the population reported on the Hourly Electric Grid Monitor, and expressly warns that not all EIA-860 generators are metered by balancing authorities. This is a valuable **reporting-population reconciliation**, not hourly generator availability, dispatch, or physical transfer rating.

**Verified GitHub Actions:**
- [Official original XLS schema and SHA256 CI 42450880563](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42450880563).
- [Year-specific four-BA Schedule 2 / Schedule 4 extraction and source-scope CI 42451161661](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42451161661), passing four regression tests and archival row-count/type checks.
- [Download source checksums, full selected four-BA Schedule 2 candidates, Schedule 4 relationship rows, technology grouping, and source-status manifests (artifact 13605567656)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42451161661/artifacts/13605567656).

### Schedule 2 original declared reporting inventory

| BA | 2023 annual Schedule 2 generator records | 2024 annual Schedule 2 generator records |
|---|---:|---:|
| AZPS | 131 | 133 |
| BPAT | 300 | 298 |
| CISO | 1,619 | 1,434 |
| SRP | 94 | 95 |
| **Total** | **2,144** | **1,960** |

Counts are **EIA-930A annual Schedule 2 reporting-population rows**, not observed dispatch, July-2024 online units, the sum of firm generation resources, or the complete physical fleet. They must not be compared as a physical capacity fraction to the earlier EIA-860 single-fuel nameplate screening sample without a generator-identity and technology denominator crosswalk. In the public EIA-930A workbook, some rows use original EIA-860 identities while others have EIA-930A fallbacks. The code preserves the source identifiers and their recognition status, and does not silently treat unmatched units as absent capacity.

### Schedule 4 has an important year-specific semantic change

The official **2023** Schedule 4 uses many **named BA codes** in the column `BAs having a Pseudo-Tie or Dynamic Relationship`. In the selected four-BA-related cohort, there are 455 **expanded row–relationship entries**, across 61 reporter/label groups. The 2023 records include **CISO–GRID** and **AZPS–CISO** as declared name-bearing relationships.

The official **2024** Schedule 4 contains 143 selected expanded row–relationship entries, across 19 groups. Crucially, **56 CISO records use relationship mechanism category labels rather than BA identifiers**:

| 2024 reporter BA | Original Schedule 4 label | Declared generator/relationship rows | Meaning the data establishes |
|---|---|---:|---|
| CISO | **PSEUDO TIE** | **21** | Annual resource-level pseudo-tie **category reported**, counterpart not identified by this cell |
| CISO | **DYNAMIC IMPORT** | **35** | Annual resource-level dynamic-import **category reported**, counterpart not identified by this cell |
| AZPS | GRID | 1 | Annual declared named BA relationship, not July interchange discrepancy attribution |
| BPAT | IPCO | 2 | Annual declared named relationship |
| BPAT | PGE | 9 | Annual declared named relationship |
| BPAT | PSEI | 6 | Annual declared named relationship |
| BPAT | TWPR | 11 | Annual declared named relationship (original source label retained, no unverified normalization) |

Additional named source relationships are retained in the archive, including some entered by an external BA and naming a target BA. **Never parse the literal strings `PSEUDO TIE` or `DYNAMIC IMPORT` as BA codes or pairwise transmission links.** The revised extractor has explicit `relationship_label_kind`, `relationship_original_label`, `declared_partner_ba` (blank for category labels), and `source_declares_mechanism_category` fields. Its tests fail if an unrecognized mechanism is silently turned into an arbitrary pairing.

### Specific significance for the earlier July EIA-930 reciprocal-reporting findings

Official 2024 Schedule 4 provides **positive, source-specific evidence of annual resource-level dynamic or pseudo-tie reporting for CISO**. This materially advances the previous generic discussion, but **it does not identify which direction of any particular July tie-line report was wrong** or attribute the `AZPS–CISO` or `CISO–SRP` hourly reciprocal discrepancy to a specific plant, transaction, time interval, or reporting mechanism.

The explicit 2024 AZPS–GRID relationship and the 2023 CISO–GRID named relationship also **do not prove a BPAT–GRID relationship or explain the BPAT–GRID 129,398 MWh absolute reciprocal reporting difference**. Absence of a BPAT–GRID or BPAT–SCL label in this extracted annual Schedule 4 cohort **must not be used as proof no such relationship existed**: BA-specific reporting could omit counterpart identity, use mechanism labels, or reflect a different source scope.

Current historical anomalies remain independently identified:
- BPAT: 168/168 complete original BA demand-generation-interchange triplets, −741,860 MWh week-signed residual; own bilateral sums approximately match the BA total.
- CISO: 144/168 original BA total interchange cells missing; bilateral partner report sums are observed but source-only **shadow** balance closes only 17/144 of those hours.
- Reciprocal reported pairwise differences: BPAT–GRID 129,398 MWh, BPAT–SCL 90,046 MWh, AZPS–CISO 49,080 MWh and AZPS–SRP 37,195 MWh absolute over the 168-hour source window.

These remain **reporting discrepancies**, not physical grid losses, unserved load, EENS, deliverable import MW, or certified thermal constraints.

## Implications for the Paper C calibration pathway

1. Use **EIA-930A Schedule 2 source-identifiable plant/generator units** as the **reporting-population denominator** for each year, with a transparent EIA-860 identity match. The earlier nameplate-driven PyPSA partial-fleet model and this annual reporting population are distinct source constructions.
2. Document Schedule 4 **type labels separately from counterpart codes**, including resource name, reported EIA plant/generator IDs, and year; they can inform accounting-boundary uncertainty but not hour-specific restoration.
3. For physical adequacy or climate-resilience modeling, obtain actual plant available MW, hourly supply and storage treatment, and independently certified electrical topology and transfer limits. EIA-930A annual names cannot reconstruct those inputs by itself.
4. Avoid comparing annual generator records as fully equivalent across source years: the 2023/2024 SCH 4 label semantics and EIA-930A annual roster-vintage conventions differ.

## Publication-ready wording

> Official EIA-930A annual generator inventories provide an independent source for defining the BA-visible reporting population. Schedule 4 additionally documents reported dynamic or pseudo-tie resource relationships, although the identifying information differs by year: named BA counterparties are present in many 2023 entries, while 2024 CISO entries include explicit pseudo-tie and dynamic-import category labels. Such annual relationships do not establish causation for any specific July 2024 directional interchange discrepancy. We therefore retain physical availability, transfer capability and observed system shortage as uncalibrated quantities.
