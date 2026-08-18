# 01 — Data sources
*CRISP-DM Phase 2: Data Understanding. Cap: 500w.*

> **STATUS:** WRITTEN (rebuilt for Robyn after D8)
> **Blocked by:** nothing
> **Done when:** ✅ every source has owner, grain, coverage, licence, and a reproducible access path

## Why not a real advertiser's data

Commercial media spend is not public. Meta's Ad Library exposes spend and
impression ranges **only for political and issue ads** — commercial ads carry no
spend field in either the API or the web UI. Third-party tools sell *estimates*,
not actuals. A credible open MMM therefore has to use a recognised simulated
dataset. That is a constraint of the domain, stated here rather than glossed over.

## Primary source

|  |  |
| --- | --- |
| **Dataset** | `dt_simulated_weekly` |
| **Owner** | Meta Marketing Science, shipped with the open-source [Robyn](https://github.com/facebookexperimental/Robyn) MMM package |
| **Obtained** | `raw.githubusercontent.com/facebookexperimental/Robyn/main/R/data/dt_simulated_weekly.RData`, converted once to CSV **in Python via `pyreadr`**. The `.RData` artefact is deleted after conversion — **no R is involved anywhere in this project** |
| **Licence** | MIT |
| **Grain** | One row per week, Monday-dated, national |
| **Coverage** | 2015-11-23 → 2019-11-11 — **208 consecutive weeks, no gaps** |
| **Refresh** | Static. A fixed demo asset, not updated |
| **Contents** | 5 paid channels (TV, out-of-home, print, Facebook, paid search), 1 organic (`newsletter`), 1 control (`competitor_sales_B`), an unusable `events` flag, outcome `revenue` |
| **Scale** | 14,529,099 paid spend against 379,005,697 revenue — 3.8% |
| **Provenance caveat** | **Simulated by Meta.** True parameters are not published, so estimated ROIs cannot be scored against an answer key |

## Supporting source

`dt_prophet_holidays`, same repository and licence. **87,651 rows, 123 countries,
1995–2044.** Requires choosing a market.

**Market: Germany (DE) — inferred, never formally stated.** The dataset's own
roxygen documentation says only "Simulated MMM data" and names no region. Three
converging signals in Robyn's source point to DE:
1. `R/R/data.R:29` — the commented provenance line reads
   `dt_input <- read.csv('data/de_simulated_data.csv')`
2. `R/R/inputs.R:136` — the documented example for the main input function uses
   `prophet_country = "DE"`
3. `demo/demo.R:67` — the official demo sets `prophet_country = "DE"`

DE yields **37 holiday dates** inside the modelling window (10 distinct); US
would yield 44 (13 distinct). Recorded here as evidence; the choice is confirmed
in `05-analysis-plan.md`.

**Documentation defect noted:** `data.R` describes `revenue` as *"Daily total
revenue"* although the dataset is weekly. The field is weekly.

## Data readiness assessment — why this dataset and not the alternatives

Every candidate was downloaded and profiled, not judged from documentation.
A first pass selected Meridian's national sample; it was **rejected after audit**
and the evidence is kept in `data/audit/`.

| Axis | Meridian national | **Robyn (chosen)** |
| --- | --- | --- |
| Weeks | 156 | **208** |
| Seasonality peak/trough | 1.07× | **3.31×** |
| Channels dark >20% of weeks | **0/5** | **4/5** |
| CV per channel | 0.31–0.87 | **0.79–1.94** |
| Max abs corr(spend, outcome) | 0.18 | **0.44** |
| Quintile Q5 > Q1 | **2/5** | **5/5** |
| Unit-cost variation | ~1e-8, constant | **CV 0.12–0.25** |
| Channel identity | anonymous `Channel0-4` | **named media types** |

**Meridian's geo panel was also tested and also fails.** Meridian is designed
geo-first, so this mattered. Within-geo correlations are 0.02–0.13 and
**channel mix is near-identical across all 40 markets** — Channel3's share spans
only 0.380–0.414, sd 0.009. Geo-level MMM works because markets receive
*different* mixes; here every market gets the same plan scaled by population, so
there is no cross-sectional variation to exploit.

Also evaluated and rejected: `pymc-marketing/mmm_example.csv` (2 channels in
unitless 0–1 values — no currency to reallocate) and Meridian's
`hypothetical_geo_all_channels.csv` (**no outcome column**, despite the docs
describing one).

**Robyn's known weakness is a modelling problem, not an identification failure:**
`competitor_sales_B` correlates 0.92 with revenue. That is confronted in `03` and
resolved in `05`.

## Access reproducibility

`src/01_load.py` reads `data/raw/`, exposes `weekly()` and `holidays(country)`,
and asserts row count, Monday dating, weekly regularity, absence of missing
values, column presence, and value sanity. It additionally asserts **the two
properties that justified the switch** — at least 4 of 5 channels dark >20% of
weeks, and seasonality above 3.0× — so the audit's conclusion cannot silently
break. It runs at the top of `notebooks/01_eda.ipynb`; no analysis executes on
unvalidated data. Raw CSVs total ~3.4MB and are committed.
