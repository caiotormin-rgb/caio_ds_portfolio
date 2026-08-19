# 01 — Data sources
*CRISP-DM Phase 2: Data Understanding. Cap: 500w.*

> **STATUS:** WRITTEN — rewritten for the simulated dataset
> **Blocked by:** nothing
> **Done when:** ✅ every source has owner, grain, coverage, licence and a reproducible access path

## Why the data is simulated

Three real or vendor-supplied candidates were audited and each failed on
**identification** — not on tidiness. The audit is the justification, and the
evidence is in `03-data-quality.md`.

| Candidate | Fatal finding |
|---|---|
| Google Meridian, 7 simulated CSVs | No flighting, 1.07× seasonality, near-zero spend-outcome correlation at national **and** geo grain. Root cause read from its DGP: impressions are iid draws with no seasonal or autoregressive term, `u_m`/`u_tm` are shared across all geos, and **the media equation never references the control variables** despite the notebook claiming confounding |
| Robyn `dt_simulated_weekly` | Usable, and used for the full EDA. But seasonality explains 80.7% of revenue while all five channels add **2.6 points**; `competitor_sales_B` correlates 0.92 with revenue and is undecidable between confounder, mediator and seasonality proxy — a question [open and unanswered](https://github.com/facebookexperimental/Robyn/issues/1073) in Robyn's own tracker |
| `pymc-marketing/mmm_example.csv` | Two channels in unitless 0–1 values. No currency to reallocate |

**Settled negative:** no advertiser has ever released real MMM data. Zenodo, OSF,
Harvard Dataverse and journal replication policies were all checked. IRI/Circana
requires an NDA and $1,000 and carries advertising for 2 of 30 categories;
Dominick's has zero media channels.

Simulation is therefore not a shortcut. It is the only route to a **known answer
key** — without which a reallocation recommendation cannot be validated at all.

## Primary source — our own DGP

| | |
| --- | --- |
| **Specification** | [`reference/dgp-spec.md`](reference/dgp-spec.md) — **pre-registered and committed before any data was generated** (`85ea4fa`, amended `ce906f1`). The git log is the proof |
| **Owner** | This project |
| **Seed** | 20260818 |
| **Grain** | One row per week, Monday-dated, national |
| **Coverage** | 2021-01-04 → 2024-12-23 — **208 weeks, four complete calendar years** (52/52/52/52). No partial-year tails |
| **Market** | US, USD |
| **Channels** | Linear TV, Meta social, YouTube, CTV/streaming, branded search, Amazon retail media |
| **Ground truth recorded** | Per channel: adstock θ, Hill α and κ, β, true weekly contribution, true ROI, true marginal ROI at observed spend, and **the true optimal reallocation**. This is what `07-evaluation.md` scores against |
| **Provenance caveat** | **Fully synthetic, and stated as such everywhere.** No claim of external validity. The value is that every estimate is checkable |

## Supporting source — real

**US federal holiday calendar** via the `holidays` Python package (v0.103). Real
public data, no invention. 51 dates across the window, 46 of 208 weeks affected
(22.1%), 11 distinct holidays each recurring 4–5 times — no n=1 problem.

## Source projection — six exports, each in its platform's real shape

Truth is generated once, then projected into six exports with different units,
grains, week definitions and defects. Reconciling them is the Phase 3 work and
the point of the exercise.

| Channel | Simulated source | Spec verified |
| --- | --- | --- |
| Branded search | Google Ads API `keyword_view` | ✅ official docs |
| YouTube | Google Ads API, video campaign | ✅ official docs |
| Meta social | Meta Ads Insights | ✅ official docs |
| CTV / streaming | **DV360** Bid Manager report | ✅ machine-readable API discovery document |
| Amazon retail media | Amazon Ads API v3 | ✅ doc mirror, corroborated twice |
| Linear TV | Agency spreadsheet — no API exists | n/a by construction |

Field specifications and the "tells" that mark synthetic data are in
[`reference/platform-data-specs.md`](reference/platform-data-specs.md). **DV360
was chosen over The Trade Desk and Xandr because their field names could not be
verified** — and inventing field names is precisely the failure mode being avoided.

## Access reproducibility

`src/10_simulate_truth.py` → `src/11_project_to_sources.py` → `src/12_ingest.py`,
each seeded and each asserting its own invariants. Raw exports, truth parameters
and the reconciled modelling table are all committed, so any figure in the
readout can be traced back to the line that produced it.
