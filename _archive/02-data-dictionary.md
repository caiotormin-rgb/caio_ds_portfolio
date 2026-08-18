# 02 — Data dictionary
*Phase 2: Data Understanding. Table only.*

`data/cached/mmm_weekly.csv` — 208 rows × 12 columns, one row per week.

Suffix convention is Robyn's demo naming: `_S` = spend, `_I` = impressions,
`_P` = clicks, `_B` = baseline/context variable.

| Field | Type | Required | Definition | Example | Notes |
|---|---|---|---|---|---|
| `DATE` | Date | yes | Week start, always a Monday | `2015-11-23` | 208 consecutive weeks, no gaps, no duplicates |
| `revenue` | num | yes | Weekly total revenue. **The dependent variable.** | `2754372` | Range 672K–3.83M. No trend (−65/wk, p=0.94). Strong seasonality: Jun trough ~868K, Nov peak ~2.87M |
| `tv_S` | num | yes | TV spend | `22358.35` | **55.8% zero weeks** — flighted |
| `ooh_S` | num | yes | Out-of-home spend | `132278.4` | **59.1% zero** — flighted. Largest channel at 61.9% of total spend |
| `print_S` | num | yes | Print spend | `453.87` | **58.2% zero** — flighted. Smallest offline channel |
| `facebook_S` | num | yes | Facebook spend | `7607.13` | **51.4% zero.** Only 3.1% of total spend |
| `facebook_I` | num | yes | Facebook impressions | `24301284` | Exposure twin of `facebook_S`; **r = 0.991**. Model one or the other, never both |
| `search_S` | num | yes | Paid search spend | `4133.33` | **15.4% zero — effectively always-on**, unlike every other channel |
| `search_clicks_P` | num | yes | Paid search clicks | `9837.24` | Exposure twin of `search_S`; **r = 0.983**. Model one or the other, never both |
| `newsletter` | num | yes | Newsletter sends. **Organic**, not paid | `19401.65` | Never zero (min 301). Excluded from spend totals and from the reallocation, since it has no media cost |
| `competitor_sales_B` | int | yes | Competitor sales. Context/control variable | `8125009` | **r = 0.916 with revenue.** See `03-data-quality.md` — this is the central modeling problem |
| `events` | chr | yes | Event flag | `na` | **206 of 208 weeks are `"na"`.** `event1` and `event2` occur once each. Unusable as a control at n=1 |

## Derived / not in the raw file

| Field | Source | Definition |
|---|---|---|
| `holiday_*` | `data/cached/holidays_all.csv` | Holiday indicators. Requires choosing a market; Robyn's demo convention is DE → 37 dates in window |

## Total spend by channel, full window

| Channel | Total | Share of paid spend |
|---|---:|---:|
| `ooh_S` | 8,989,332 | 61.9% |
| `tv_S` | 3,087,488 | 21.3% |
| `search_S` | 1,230,427 | 8.5% |
| `print_S` | 775,556 | 5.3% |
| `facebook_S` | 446,297 | 3.1% |
| **Total paid** | **14,529,100** | 3.83% of total revenue |
