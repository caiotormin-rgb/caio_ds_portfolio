# 04 - Transformation Log / Feature Spec
*Step 04 of 09 | CRISP-DM Phase 3: Data Preparation | Audience: technical reviewer.*

This file records how six platform-shaped exports became one weekly modeling
table, including the fixes applied and the features deliberately left out.

Status: work in progress. This transformation log documents the synthetic
case-study version of Caio's MMM project framework.

## Main Point

The data-prep problem was not formatting. It was making six incompatible source
systems agree on one weekly spend table. A budget recommendation is not worth
reading if the spend totals do not tie back to source systems.

## Engineering Design

The pipeline is intentionally layered:

1. Generate known truth.
2. Project truth into messy platform-shaped exports.
3. Ingest and reconcile those exports.
4. Build a narrow modeling table.
5. Fit and validate the model against the answer key.

That design tests whether the process can survive realistic data conditions
before it is pointed at real advertisers.

## Source Alignment

Everything is keyed to a Monday-starting week.

| Source | Native shape | Handling |
|---|---|---|
| Google Ads search | Weekly report available | Keep native Monday week |
| Google Ads YouTube | Weekly report available | Keep native Monday week |
| Meta Ads Insights | Daily rows only | Roll up to Monday weeks |
| Amazon Ads | Daily rows only; zero days omitted | Reindex to full week grid and fill true zeroes |
| DV360 CTV | Weekly report plus separate reach file | Join reports after validating week boundaries |
| Linear TV | Monthly invoice plus weekly airings | Allocate invoice to weekly airings and reconcile |

## Data Fixes

| Problem | Fix | Why it matters |
|---|---|---|
| Google cost in micros | Divide by 1,000,000 | Prevents million-fold spend errors |
| Meta click-through rate on percent scale | Convert to 0-1 ratio | Makes rates comparable across platforms |
| Meta numeric fields stored as strings | Detect in raw JSON and cast explicitly | Prevents silent parser behavior from hiding defects |
| Daily rates | Recompute from totals after rollup | Avoids averaging rates incorrectly |
| Reach | Keep as diagnostic, never sum daily reach | Reach is a count of unique people, not an additive metric |
| Amazon missing rows | Treat no-activity days as zero | Prevents confusing dark periods with missing data |
| DV360 footer and grand total | Truncate at the first blank line | Prevents report metadata from becoming data |
| Recent conversion restatement | Flag unsettled weeks | Keeps recency bias visible for modeling |

## Detection Result

The pipeline planted realistic source problems and checked that the ingest
process caught them. The final report logged 14 defect classes and 16 detected
instances, including one near-miss: Meta's quoted numeric fields disappeared
after `pandas.read_json` silently coerced them. The check was moved upstream to
the raw JSON text.

That near-miss is the useful lesson. Some data problems are invisible after a
library "helps" by repairing them.

## Reconciliation

Total spend reconciles to the generating truth:

| Channel | Reconciled spend | Truth | Difference |
|---|---:|---:|---:|
| Linear TV | 12,600,000 | 12,600,000 | 0.000% |
| Meta social | 8,100,000 | 8,100,000 | 0.000% |
| YouTube | 7,200,000 | 7,200,000 | 0.000% |
| CTV | 6,300,000 | 6,300,000 | 0.000% |
| Branded search | 5,400,000 | 5,400,000 | 0.000% |
| Amazon retail media | 5,400,000 | 5,400,000 | 0.000% |

## Modeling Table

`src/13_features.py` creates `data/simulated/model_frame.csv`: 208 weeks, 17
columns, no missing values.

| Group | Features | Reason |
|---|---|---|
| Calendar | `sin1`, `cos1`, `sin2`, `cos2`, `trend` | Controls annual seasonality without monthly dummy variables |
| Holidays | `holiday_count`, `holiday_retail_count` | Counts preserve weeks with multiple holidays |
| Demand control | `category_demand` | Tests sensitivity to an external driver of sales and media planning |
| Media | Six raw spend columns | Keeps the budget basis consistent across channels |
| Outcome | `revenue`, `settled` | Flags rows affected by late conversion reporting |

## Deliberately Excluded

Adstock and saturation are not engineered as fixed features. They are estimated
inside the model. Building them in advance would hide an assumption as if it
were observed data.

Exposure, reach, CPM, impression share, and GRPs are retained for audit checks
but not used as model drivers. Spend is the common budget unit across all six
channels.

## Current Stack

| Layer | Tools |
|---|---|
| Ingestion | Python, pandas, JSON, CSV |
| Validation | pandas assertions, source-total reconciliation, ingest report |
| Feature engineering | Python, pandas, numpy, `holidays` |
| Modeling handoff | `data/simulated/model_frame.csv` |

## Scale-Up Stack

For real advertisers, this layer should move from local files to a managed data
workflow:

| Layer | Candidate tools | Role in production |
|---|---|---|
| Warehouse | BigQuery, Snowflake, DuckDB, Postgres | Store raw exports, cleaned facts, model frames, and result history |
| Transformations | dbt or SQLMesh | Build tested source contracts and documented media tables |
| Orchestration | Dagster, Prefect, Airflow | Schedule refreshes, validations, model runs, and report delivery |
| Data-quality checks | Great Expectations, dbt tests, custom assertions | Catch spend mismatches, late data changes, missing controls, and schema drift |
| Source connectors | Platform APIs, agency file drops, MCP/tool integrations | Move from manual files to repeatable source ingestion and follow-up workflows |

## Rows Dropped

None during preparation. The final 6 unsettled weeks are flagged here and
excluded later in `05-analysis-plan.md`.

## Next

Continue to `05-analysis-plan.md`.
