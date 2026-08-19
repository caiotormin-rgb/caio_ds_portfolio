# 01 - Data Sources
*Step 01 of 09 | CRISP-DM Phase 2: Data Understanding | Audience: analytics lead.*

This file explains why the project uses simulated data and how that data was
made realistic enough to test the business process.

Status: work in progress. This is the source plan for the synthetic case-study
version of Caio's MMM project framework.

## Short Answer

The final dataset is synthetic by design. Public real-world MMM data with named
media channels, spend, revenue, timing, and a known answer key was not available.
Using synthetic data lets the model be graded against truth instead of only
judged by whether it sounds plausible.

That distinction matters here: the model eventually produces a plausible but
wrong answer for branded search. Without a known answer key, that failure would
not be visible.

## Candidate Data Audited

| Candidate | Why it was not enough |
|---|---|
| Google Meridian sample | Too little identifying variation: no meaningful media flighting and near-zero spend-outcome signal at national and geo levels |
| Robyn `dt_simulated_weekly` | Useful for exploratory work, but media adds only 2.6 percentage points beyond seasonality and an important competitor variable is not interpretable |
| PyMC-Marketing `mmm_example.csv` | Two anonymous channels on a 0-1 scale, with no currency basis for budget reallocation |

The issue was not whether the files were clean. The issue was whether they could
support a defensible budget recommendation.

## Final Source

| Item | Value |
|---|---|
| Source | Project-generated data-generating process |
| Specification | `reference/dgp-spec.md` |
| Seed | `20260818` |
| Grain | One national row per Monday-starting week |
| Coverage | `2021-01-04` through `2024-12-23` |
| Market | United States |
| Currency | USD |
| Channels | Linear TV, Meta social, YouTube, CTV, branded search, Amazon retail media |
| Ground truth | True contribution, ROI, marginal ROI, carryover, saturation, and optimal reallocation |

## Platform-Shaped Exports

The truth is generated once, then projected into six source files that mimic
real platform exports. The goal is to test the data assembly work, not just the
model fit.

| Channel | Simulated source shape | Why it matters |
|---|---|---|
| Branded search | Google Ads keyword report | Costs arrive in micros; branded status is analyst-derived |
| YouTube | Google Ads video campaign report | Paid YouTube metrics do not come from YouTube Analytics |
| Meta social | Meta Ads Insights | Daily rows, string-encoded numbers, and different rate units |
| CTV | DV360 report | Reach comes from a separate report and the CSV has a non-rectangular footer |
| Amazon retail media | Amazon Ads v3 | Zero-activity days are absent, not reported as zero |
| Linear TV | Agency spreadsheet | No API; invoices and weekly airings need reconciliation |

## Reproducibility

The source pipeline runs in order:

1. `src/10_simulate_truth.py` creates the answer key.
2. `src/11_project_to_sources.py` creates platform-shaped exports.
3. `src/12_ingest.py` reconciles those exports.
4. `src/13_features.py` creates the modeling table.

Raw exports, truth parameters, and reconciled tables are committed so the
readout figures can be traced back to source data.

## Next

Continue to `02-data-dictionary.md`.
