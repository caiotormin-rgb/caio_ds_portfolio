# 02 — Data dictionary
*CRISP-DM Phase 2: Data Understanding. Cap: table only — no prose.*

> **STATUS:** WRITTEN
> **Blocked by:** nothing
> **Done when:** ✅ every column in the modelling table has a definition and a unit

`data/raw/meridian_national_all_channels.csv` — **156 rows × 17 columns**, one row per week.
Loaded via `src/01_load.py :: national()`. `r_y` = Pearson correlation with `conversions`.

| Field | Type | Required | Definition | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `time` | date | yes | Week start, always a Monday | `2021-01-25` | 156 consecutive weeks to 2024-01-15. No gaps, no duplicates |
| `conversions` | float | yes | Weekly conversions. **The dependent variable** | `422,632,782` | Range 340.3m–491.3m, mean 422.6m. Never zero |
| `revenue_per_conversion` | float | yes | Revenue value of one conversion | `0.02000151` | **156 distinct values, not a constant** — but CV is 0.076% and full range spans 0.45% of the mean. `revenue = conversions × this` correlates 0.99994 with `conversions`, so the two are interchangeable as an outcome |
| `Channel0_spend` | float | yes | Paid media spend, channel 0 | `259,626.37` | 18.5% of paid spend. Never zero. `r_y` +0.051 |
| `Channel1_spend` | float | yes | Paid media spend, channel 1 | `200,771.14` | 14.3% of paid spend. Never zero. `r_y` +0.012 |
| `Channel2_spend` | float | yes | Paid media spend, channel 2 | `77,431.73` | 5.5% of paid spend. **Only channel with dark weeks — 2.6%.** `r_y` −0.110 |
| `Channel3_spend` | float | yes | Paid media spend, channel 3 | `563,207.42` | **Largest at 40.0% of paid spend.** Never zero. `r_y` −0.124 |
| `Channel4_spend` | float | yes | Paid media spend, channel 4 | `305,965.92` | 21.7% of paid spend. Never zero. `r_y` −0.179 |
| `Channel0_impression` | int | yes | Impressions delivered, channel 0 | `35,406,541` | **Fixed CPM 7.3327** — exact rescale of spend |
| `Channel1_impression` | int | yes | Impressions delivered, channel 1 | `20,824,222` | **Fixed CPM 9.6412** — exact rescale of spend |
| `Channel2_impression` | int | yes | Impressions delivered, channel 2 | `10,420,201` | **Fixed CPM 7.4309** — exact rescale of spend |
| `Channel3_impression` | int | yes | Impressions delivered, channel 3 | `72,272,418` | **Fixed CPM 7.7928** — exact rescale of spend |
| `Channel4_impression` | int | yes | Impressions delivered, channel 4 | `39,267,119` | **Fixed CPM 7.7919** — exact rescale of spend |
| `Organic_channel0_impression` | int | yes | Impressions from an **organic** channel — no media cost | `21,298,667` | Range 0.4m–60.9m. Never zero. Excluded from paid-spend totals and from any reallocation. `r_y` +0.017 |
| `competitor_sales_control` | float | yes | Competitor sales activity. Context/control, **pre-standardised** | `-0.0448` | Range −1.95 to +2.13, mean ≈ 0. `r_y` **−0.380** — the strongest non-media relationship in the table |
| `sentiment_score_control` | float | yes | Brand sentiment. Context/control, **pre-standardised** | `-0.0264` | Range −1.86 to +1.96, mean ≈ 0. `r_y` −0.056 |
| `Promo` | float | yes | Promotional intensity | `0.4957` | Range 0.012–1.473, **never zero — always-on continuous intensity, not an on/off flag.** `r_y` **+0.299** |

## Units and conventions

| Convention | Meaning |
| --- | --- |
| `_spend` | Currency, unspecified denomination. Simulated |
| `_impression` | Count of impressions delivered |
| `_control` | Pre-standardised context variable, mean ≈ 0 |
| `Channel0`–`Channel4` | **Anonymous.** No media type is given. Any mapping to TV / search / social would be an invention and must be disclosed as one |

## Derived fields (not in the raw file)

| Field | Source | Definition |
| --- | --- | --- |
| `revenue` | `conversions × revenue_per_conversion` | Monetary outcome. Built in the EDA notebook |
| `total_spend` | sum of the five `_spend` columns | Weekly paid media total |
| implied CPM | `spend / impression × 1000` | Per channel; constant by construction — see notes above |

## Paid spend by channel, full 156 weeks

| Channel | Total | Share |
| --- | ---: | ---: |
| `Channel3` | 87,860,358 | 40.0% |
| `Channel4` | 47,730,683 | 21.7% |
| `Channel0` | 40,501,713 | 18.5% |
| `Channel1` | 31,320,298 | 14.3% |
| `Channel2` | 12,079,349 | 5.5% |
| **Total paid** | **219,492,402** | **16.6% of revenue** |

Implied revenue over the period: 1,318,718,006.

## Additional fields in the geo file (Phase 5 only)

`data/raw/meridian_geo_all_channels.csv` — **6,240 rows × 19 columns**, one row per geo-week.
Same 17 fields plus:

| Field | Type | Required | Definition | Example | Notes |
| --- | --- | --- | --- | --- | --- |
| `geo` | str | yes | Market identifier | `Geo0` | 40 distinct, `Geo0`–`Geo39` |
| `population` | float | yes | Market population | `229,277.33` | 136,671–994,049. **Constant within each geo** — a static weight, not a time series |
