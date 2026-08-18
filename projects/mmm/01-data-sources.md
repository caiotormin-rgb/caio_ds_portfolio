# 01 — Data sources
*CRISP-DM Phase 2: Data Understanding. Cap: 500w.*

> **STATUS:** WRITTEN
> **Blocked by:** nothing
> **Done when:** ✅ every source has owner, grain, coverage, licence, and a reproducible access path

## Why this data and not a real advertiser's

Commercial media spend is not public. Meta's Ad Library exposes spend and
impression ranges **only for political and issue ads** — commercial ads carry no
spend field in either the API or the web UI. Third-party tools sell *estimates*,
not actuals. A credible open MMM therefore has to use a recognised simulated
dataset or generate its own. That is a real constraint of the domain, stated here
rather than glossed over in the readout.

## Primary source

| | |
|---|---|
| **Dataset** | `national_all_channels.csv` |
| **Owner** | Google, shipped with the open-source [Meridian](https://github.com/google/meridian) MMM framework |
| **Obtained** | `raw.githubusercontent.com/google/meridian/main/meridian/data/simulated_data/csv/national_all_channels.csv` |
| **Licence** | Apache-2.0 |
| **Grain** | One row per week, national |
| **Coverage** | 2021-01-25 → 2024-01-15 — **156 consecutive weeks, no gaps** |
| **Refresh** | Static. A fixed demo asset, not updated |
| **Contents** | 5 paid channels (spend *and* impressions each), 1 organic channel, controls `competitor_sales_control` / `sentiment_score_control` / `Promo`, outcome `conversions` with `revenue_per_conversion` |
| **Scale** | 219,492,402 paid spend against 1,318,718,006 implied revenue — 16.6% |
| **Provenance caveat** | **Simulated by Google.** True parameters are not published, so estimated ROIs cannot be scored against an answer key |

## Secondary source — retained for Phase 5 only

`geo_all_channels.csv`, same repository and licence: **40 geos × 156 weeks =
6,240 rows**, identical fields plus `population`.

Verified numerically, not assumed: **summing the geo panel over its 40 geos
reproduces the national file to floating-point precision** (max relative
difference 2.2e-16). The two are the same simulation at different grain, not
competing datasets. `src/01_load.py` asserts this on every run, so the property
cannot silently break. It underwrites the D2 decision to model nationally first
and add geo as a bounded robustness check.

## Candidates evaluated and rejected

Each was downloaded and profiled, not judged from documentation.

| Candidate | Why rejected |
|---|---|
| Robyn `dt_simulated_weekly` | R-based toolchain, ruled out at D1. Data itself was viable — 208 weeks, named channels |
| `pymc-marketing/mmm_example.csv` | Only 2 channels, in unitless 0–1 values. **Cannot support a budget reallocation** — no currency to reallocate |
| Meridian `hypothetical_geo_all_channels.csv` | **No outcome column**, despite documentation describing one. 38 weeks |
| Meridian `national_media` / `geo_media` (± `_rf`) | 4 paid channels, no organic, no Promo. The `_rf` pair adds Channel3 reach/frequency — parked, not rejected on quality |

## Access reproducibility

`src/01_load.py` reads `data/raw/`, exposes `national()` and `geo()`, and asserts
row counts, weekly regularity, panel balance, absence of missing values, column
presence, value sanity, and the aggregation identity above. It runs at the top of
`notebooks/01_eda.ipynb`, so no analysis executes on unvalidated data. Both raw
files total ~1MB and are committed.

## Known gap

Channels are named `Channel0`–`Channel4` — **anonymous, with no media type**.
Any mapping to TV / search / social would be an invention and must be disclosed
as one if made. Carried forward to `03-data-quality.md`.
