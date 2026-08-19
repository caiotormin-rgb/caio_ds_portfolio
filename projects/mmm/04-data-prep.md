# 04 — Transformation log / feature spec
*CRISP-DM Phase 3: Data Preparation. Cap: 600w.*

> **STATUS: PLAN, NOT LOG.** Nothing has been generated or transformed yet.
> This document states **what will be done and how it will be checked**, written
> before execution so the reconciliation cannot be reverse-engineered from
> whatever the data happens to look like. Every section is rewritten as a record
> of what actually happened once `12_ingest.py` runs.
>
> **Blocked by:** `03-data-quality.md` ✅ · generation of the six source exports
> **Done when:** every transformation is reversible from this document alone, and totals reconcile to source

## The problem this phase solves

Six exports, six shapes. Different units, different grains, different week
definitions, two with no API at all. Reconciling them into one weekly modelling
table **is** the phase — and per industry practice a good MMM project is roughly
60% data readiness, 40% modelling.

## Join keys

Everything keys on **week-starting Monday**, derived once in a single place from
a daily-grain intermediate. Never with `pandas.resample("W")`, which defaults to
Sunday-ending and would misalign against Google Ads by one day.

| Source | Native grain | Week handling |
|---|---|---|
| Google Ads (search, YouTube) | daily; native `segments.week` | Monday-start, use as-is |
| Meta Ads Insights | daily, **no weekly increment** | roll up — but **not** reach |
| Amazon Ads v3 | daily, **no weekly grain exists** | roll up; a week column here would be fake |
| DV360 | daily; `FILTER_WEEK` available | Monday-start (non-YouTube) |
| Linear TV spreadsheet | monthly invoice + weekly airings | allocate invoice across airings, reconcile |

## Planned transformations

| Step | Rule |
|---|---|
| Currency | Google Ads and DV360 `cost_micros` ÷ 1e6. DV360 report values are **decimal already** — micros appear only in its entity API |
| Rate units | Meta `ctr` is **percent 0–100**; Google and DV360 are **ratio 0–1**. Normalise to ratio |
| Types | Meta serialises all numerics as **JSON strings** — cast explicitly, never rely on inference |
| Rate recomputation | Every rate recomputed as `Σnumerator / Σdenominator` after rollup. Never the mean of daily rates |
| Reach | **Never summed.** Generated and carried at weekly grain only; retained as a diagnostic, not a model input |
| Zero vs missing | Amazon **omits** zero-activity rows. Reindex to the full week grid and fill with 0 — explicitly, with the count logged |
| Spend basis | Spend for all five paid channels (D11). Exposure retained for diagnostics only |
| Holidays | US federal calendar → per-week count plus flags for the retail-relevant subset. Count, not binary, because some weeks carry two |

## Defect handling — 14 planted, detection reported honestly

The dataset is synthetic and stated as such, so the EDA demonstrates the
**detection method**, not a discovery. `notebooks/02_eda.ipynb` finds them; this
document records the fix and the **detection rate** — including any that slipped.

| # | Defect | Planned handling |
|---|---|---|
| 1 | Meta `ctr` on 0–100 | unit normalisation; assert range post-fix |
| 2 | Unconverted micros | ÷1e6; assert plausible CPM |
| 3 | Meta numerics as strings | explicit cast; assert dtypes |
| 4 | Daily grain needing rollup | single rollup path |
| 5 | **Reach non-additive** | never summed; assert `reach ≤ impressions` and `freq ≥ 1` |
| 6 | Impression-share `0.0999` sentinel | treat as censored, not as a value |
| 7 | Fractional conversions | keep as float; integer-casting would be the bug |
| 8 | TV invoice ≠ Σ airings | allocate pro rata, log the residual |
| 9 | TV currency-unit block | detect by magnitude break, rescale, log rows touched |
| 10 | **Amazon omits zero-activity rows** | reindex to full grid; log fill count |
| 11 | **42-day conversion restatement** | truncate the unsettled tail, or flag it. Decision recorded here |
| 12 | **DV360 misaligned `Grand Total`** | truncate at the first blank line, as every real consumer does |
| 13 | **DV360 reach in a separate file** | second read, explicit join, no summation |
| 14 | **Week-boundary misalignment** | one derivation point; assert all sources share a week index |

## Reconciliation

Post-ingest, total spend per channel must tie back to the generating truth within
tolerance. Any residual is stated, not absorbed. The reconciliation table goes
here.

## Rows dropped

| Rule | Rows | Rationale |
|---|---:|---|
| _(filled after execution)_ | | |
