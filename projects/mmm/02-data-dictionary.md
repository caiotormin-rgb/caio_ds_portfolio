# 02 — Data dictionary
*CRISP-DM Phase 2: Data Understanding. Cap: table only — no prose.*

> **STATUS:** WRITTEN
> **Blocked by:** nothing
> **Done when:** ✅ every column in the modelling table has a definition and a unit

`data/raw/robyn_simulated_weekly.csv` — **208 rows × 12 columns**, one row per week.
Loaded via `src/01_load.py :: weekly()`. `r_y` = Pearson correlation with `revenue`.

Robyn's suffix convention: `_S` = spend, `_I` = impressions, `_P` = clicks,
`_B` = baseline/context variable.

| Field | Type | Required | Definition | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `DATE` | date | yes | Week start, always a Monday | `2015-11-23` | 208 consecutive weeks to 2019-11-11. No gaps, no duplicates. **2015 contributes only 6 weeks and 2019 only 45** — raw year-over-year comparison is invalid |
| `revenue` | float | yes | Weekly revenue. **The dependent variable** | `1,822,143` | Range 672,250–3,827,520. Never zero. No trend (−66/wk, p=0.94). **Seasonality 3.31× month peak/trough** — June 0.87m to November 2.87m |
| `tv_S` | float | yes | TV spend | `14,843.69` | 21.3% of paid spend. **56% of weeks dark.** CV 1.92. `r_y` +0.420 |
| `ooh_S` | float | yes | Out-of-home spend | `43,217.94` | **Largest at 61.9% of paid spend.** 59% of weeks dark. CV 1.94. `r_y` **+0.095 — the weakest of any channel** |
| `print_S` | float | yes | Print spend | `3,728.63` | 5.3% of paid spend. 58% of weeks dark. CV 1.74. `r_y` +0.230 |
| `facebook_S` | float | yes | Facebook spend | `2,145.66` | **Smallest at 3.1% of paid spend.** 51% of weeks dark. CV 1.47. `r_y` +0.318 |
| `facebook_I` | float | yes | Facebook impressions | `8,153,415` | Exposure twin of `facebook_S`, r = 0.991. **Cost per impression varies, CV 0.252** — so the two are *not* interchangeable. Model one, never both |
| `search_S` | float | yes | Paid search spend | `5,915.51` | 8.5% of paid spend. **Only 15% of weeks dark — effectively always-on**, unlike every other channel. CV 0.79. `r_y` **+0.443, the strongest channel** |
| `search_clicks_P` | float | yes | Paid search clicks | `16,945.21` | Exposure twin of `search_S`, r = 0.983. Cost per click varies, CV 0.124. Model one, never both |
| `newsletter` | float | yes | Newsletter volume. **Organic** — no media cost | `22,386.52` | Range 301–96,236, never zero. `r_y` +0.406. Excluded from paid-spend totals and from any reallocation. Correlates 0.60 with `search_S` |
| `competitor_sales_B` | int | yes | Competitor sales. Context/control variable | `5,538,025` | **`r_y` +0.916 — far above any media channel.** The central modelling problem; see `03-data-quality.md` |
| `events` | str | yes | Event flag | `na` | **206 of 208 weeks are `"na"`**; `event1` and `event2` occur once each. **Unusable at n=1 — drop it** |

## Supporting file

`data/raw/robyn_prophet_holidays.csv` — **87,651 rows × 4 columns**, one row per
holiday per country per year.

| Field | Type | Required | Definition | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `ds` | date | yes | Holiday date | `2016-12-25` | Covers 1995–2044 |
| `holiday` | str | yes | Holiday name | `Christmas Day` | |
| `country` | str | yes | ISO country code | `DE` | 123 countries |
| `year` | int | yes | Calendar year | `2016` | |

**Market: DE.** Never formally stated, but inferred from three converging signals
in Robyn's source — the commented provenance path `data/de_simulated_data.csv`,
and `prophet_country = "DE"` in both the documented example and the official
demo. DE gives 37 holiday dates inside the window (10 distinct); US would give 44.
Evidence in `01-data-sources.md`; confirmed in `05-analysis-plan.md`.

## Derived fields (not in the raw file)

| Field | Source | Definition |
| --- | --- | --- |
| `total_spend` | sum of the five `_S` columns | Weekly paid media total. Excludes `newsletter`, which has no cost |
| unit cost | `spend / exposure` | Facebook cost-per-impression, search cost-per-click. Only these two channels have exposure columns |

## Paid spend by channel, full 208 weeks

| Channel | Field | Total | Share |
| --- | --- | ---: | ---: |
| Out-of-home | `ooh_S` | 8,989,332 | 61.9% |
| TV | `tv_S` | 3,087,488 | 21.3% |
| Paid search | `search_S` | 1,230,427 | 8.5% |
| Print | `print_S` | 775,556 | 5.3% |
| Facebook | `facebook_S` | 446,297 | 3.1% |
| **Total paid** | | **14,529,099** | **3.8% of revenue** |

Total revenue over the period: 379,005,697.

## Channels with no exposure data

TV, out-of-home and print are **spend-only** — no impression or reach column
exists. Any modelling decision to use exposure rather than spend can therefore
apply to at most two of the five channels, or must be abandoned for consistency.
