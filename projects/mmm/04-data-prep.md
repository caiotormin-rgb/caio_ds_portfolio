# 04 — Transformation log / feature spec
*CRISP-DM Phase 3: Data Preparation. Cap: 600w.*

> **STATUS: EXECUTED.** The plan below was committed before the pipeline ran
> (`a77803c`), so nothing here was reverse-engineered from the output. Results
> are recorded against it.
>
> **Blocked by:** nothing
> **Done when:** ✅ every transformation reversible from this document · ✅ totals reconcile

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
| Spend basis | Spend for all five paid channels spend, not exposure. Exposure retained for diagnostics only |
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

## Detection outcome — 16 planted, 16 detected, 1 nearly missed

Full log in `data/simulated/ingest_report.json`. 18 detection entries across the
six sources.

**The near-miss is the one worth reading.** Meta's string-serialisation defect
initially reported *zero* string fields. The check was
`DataFrame.dtype == object`, and **`pandas.read_json` silently coerces quoted
numerics on read** — so by the time the frame exists, the evidence is gone.
Detection was moved to the raw JSON text, which finds 7 quoted numeric fields.

That class of defect — one a library quietly repairs — is invisible to *any*
check performed after the read. It is the kind that survives a careful analyst,
and it was caught only because the detection count was asserted rather than
assumed.

## Judgment calls, recorded rather than silently applied

| Call | Decision | Why |
|---|---|---|
| Impression share `0.0999` | treated as **left-censored**, then dropped | regressing on 0.0999 models a number the platform never measured |
| Meta daily reach | summed as a **diagnostic only** | reach is set cardinality; the sum is not weekly reach |
| Unsettled tails | **flagged, not truncated** | a `settled` column carries the decision to Phase 4 rather than discarding rows here |
| TV invoice vs airings | **airings** used as the spend series | +2.5% invoice residual reported, not absorbed |
| Missing spend cells | **explicit 0** | a dark week is zero spend, not missing data. 275 cells, logged |

## Reconciliation

Total spend per channel against the generating truth:

| Channel | Ingested | Truth | Diff |
|---|---:|---:|---:|
| linear_tv | 12,600,000 | 12,600,000 | −0.000% |
| meta_social | 8,100,000 | 8,100,000 | −0.000% |
| youtube | 7,200,000 | 7,200,000 | +0.000% |
| ctv | 6,300,000 | 6,300,000 | −0.000% |
| search_brand | 5,400,000 | 5,400,000 | +0.000% |
| amazon_retail | 5,400,000 | 5,400,000 | −0.000% |

## Feature construction

`src/13_features.py` → `model_frame.csv`, 208 × 17, no missing values.

**What was built** — only what is genuinely exogenous and fixed:

| Group | Features | Note |
|---|---|---|
| Calendar | `sin1 cos1 sin2 cos2 trend` | 2 harmonics, pre-committed on a degrees-of-freedom argument |
| Holidays | `holiday_count`, `holiday_retail_count` | **count, not flags** — some weeks carry two, which a binary flag discards |
| Control | `category_demand` | the reported span fits with and without |
| Media | 6 raw spend columns | **raw. See below** |
| Outcome | `revenue`, `settled` | 6 unsettled weeks flagged, rows retained |

**What was deliberately NOT built, and this is the point:**

> **Adstock and saturation are not features — they are model parameters.**

In a typical pipeline you would engineer `tv_spend_adstocked` and move on. In MMM
that is a mistake: θ, α and κ are estimated jointly with the coefficients. Baking
them in pre-commits to a decay rate the model is supposed to learn — and
`03-data-quality.md` established that this data cannot reveal carryover on its
own. Fixing it here would disguise an assumption as a feature.

Also excluded: exposure and CPM columns (diagnostics only per the spend-not-exposure decision, and undefined
in dark weeks by nature), and impression share (13 censored weeks in a variable
that is not a model input).

## Rows dropped

**None.** Every one of the 208 weeks is retained. Unsettled weeks are flagged
rather than removed, so the decision to include or exclude them belongs to
`05-analysis-plan.md` where it can be stated and tested — not buried here.
