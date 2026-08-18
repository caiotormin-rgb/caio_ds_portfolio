# Platform data specs — what real exports actually contain

Research input for simulating additional media variables. Everything here is
from official platform documentation; value ranges are marked where the only
sourcing was blog-level. Purpose: any simulated column we add must be
structurally indistinguishable from a real export to someone who works with
these tools daily.

**Supporting material, not a CRISP-DM artifact.** Referenced from
`01-data-sources.md` if and when simulated sources are added.

---

## The constraints that matter most

### Reach is not additive — the single biggest trap
Reach is the cardinality of a set of people, and set cardinality is
**subadditive**. For daily reach sets `R_d`:

```
max|R_d|  ≤  |⋃ R_d|  ≤  Σ|R_d|
```

Summing daily reach overcounts weekly reach by typically **30–70%**. Both
platforms say so explicitly — Google Ads on `metrics.unique_users` and
`metrics.average_impression_frequency_per_user`: *"This metric cannot be
aggregated, and can only be requested for date ranges of 92 days or less."*

Frequency inherits it and inverts: naive `Σimpressions / Σreach` **understates**
true weekly frequency. Daily frequency runs 1.1–1.5 while weekly runs 2–3.
**Never average frequency.**

A real weekly reach series was assembled by **156 separate API calls per
platform**, not by a `groupby`. Simulating it any other way produces an
impossible reach-to-impression ratio.

> **Implication for MMM:** use impressions or spend as the additive media
> variable, with adstock + a saturating transform. Keep reach/frequency as
> **diagnostics or covariates, not drivers.**

### Everything else that breaks on rollup

| Field | Wrong | Correct |
|---|---|---|
| `ctr`, view rate, quartile rates | mean of daily rates | `Σnumerator / Σdenominator` |
| `cpm`, `cpc`, `cpp`, `cpv` | mean of daily | `Σcost / Σvolume` |
| `frequency` | mean, or `Σimp/Σreach` | `Σimp / weekly_reach` from a fresh query |
| impression share | any rollup | denominator is **never returned** — impression-weighted mean is an approximation, document it as one |
| GSC `position` | mean | impression-weighted mean, still approximate |
| Trends index | sum or mean | re-pull at weekly grain; not recoverable from daily |

### Cross-source unit mismatches
- **`ctr`: Meta is percent 0–100. Google Ads and GSC are ratio 0–1.** A dataset with all three on one scale is wrong.
- **Money: Google Ads is micros (÷1e6).** Meta is decimal in account currency.
- **Week start: Google Ads `segments.week` is Monday. Trends is Sunday. Meta has no weekly increment at all. GSC has no weekly dimension.**
- Timezones differ per source (GSC is Pacific). Real weekly boundaries don't align perfectly.

---

## Source-by-source, condensed to what we'd use

### YouTube — the #1 tell of synthetic data
**Organic and paid come from two unrelated APIs.** Organic = YouTube Analytics
API. **All paid reach/frequency/CPV/impressions come from the Google Ads API**,
not YouTube.

- **`impressions`, `impressionsClickThroughRate`, and unique-viewer metrics do NOT exist in the YouTube Analytics API.** They exist only in the Studio UI. `adImpressions` is *ad* impressions — a different thing, and content-owner reports only.

Paid video fields (Google Ads API, `advertising_channel_type = 'VIDEO'`):

| Field | Type | Notes |
|---|---|---|
| `metrics.impressions` | INT64 | additive |
| `metrics.video_views` | INT64 | ≤ impressions |
| `metrics.video_view_rate` | DOUBLE 0–1 | native *and* derivable |
| `metrics.video_quartile_p25_rate` … `p100_rate` | DOUBLE 0–1 | rates only — absolute counts are derived. **Monotone: p25 ≥ p50 ≥ p75 ≥ p100** |
| `metrics.average_cpv`, `average_cpm` | DOUBLE | recompute on rollup |
| `metrics.cost_micros` | INT64 | **micros** |
| `metrics.unique_users` | INT64 | **native reach. Not aggregatable. ≤ 92-day windows** |
| `metrics.average_impression_frequency_per_user` | DOUBLE ≥1 | **native** — equals `impressions/unique_users` exactly |

Ranges *(blog-level)*: CPV ~$0.05 (range $0.01–0.19); CPM $5–10; view rate ~31.9%; CTR ~0.65%. Weekly frequency 1.5–4.0 for a national buy *(practitioner heuristic)*.

### Instagram — not a separate endpoint
Instagram is `breakdowns=publisher_platform` on Meta's `/<object>/insights`
edge (`facebook` | `instagram` | `audience_network` | `messenger`). **A simulated
"Instagram export" with its own account_id and no `publisher_platform` column
is a tell.**

| Field | Notes |
|---|---|
| `reach` | **native**, cannot be reconstructed. Flagged *Estimated* |
| `impressions` | native, additive |
| `frequency` | native; `= impressions/reach` exactly, ≥1 |
| `spend`, `cpm`, `cpp`, `cpc` | `cpp = cpm × frequency` always |
| `ctr` | **percent 0–100** |
| `video_p25_watched_actions` … | nested `list<AdsActionStats>`, analysts flatten |

- **All numeric fields serialize as JSON strings** (`"reach": "48213"`). CSV is fine either way.
- `time_increment` accepts `all_days`, `monthly`, or an integer 1–90 — **there is no `weekly`**.
- Insights stabilize only **after 28 days**; recent weeks in a real export are still moving.

Ranges *(blog-level)*: CPM median ~$13.48 all-industry, US ~$20, Q4 ≈ +26% vs Q1. CTR 0.8–4.1% depending on objective. Weekly frequency 1.2–3.0; fatigue flagged above 3–4.

### Google Ads search — where fake data usually fails

| Field | Notes |
|---|---|
| `segments.week` | **native Monday-start weekly rollup** |
| `metrics.impressions`, `clicks` | additive |
| `metrics.ctr` | **ratio 0–1** (contrast Meta) |
| `metrics.cost_micros`, `average_cpc` | **micros** |
| `metrics.conversions` | **DOUBLE and routinely fractional** (0.34, 2.71). Integer conversions are a tell |
| `metrics.search_impression_share` | **clipped: reported in [0.1, 1.0]; anything below 0.1 is reported as exactly `0.0999`** |
| `search_budget_lost_impression_share`, `search_rank_lost_impression_share` | **clipped to [0, 0.9]; above 0.9 reported as `0.9001`** |
| `segments.search_term_match_type` | includes variants like **Near Exact / Near Phrase**, unlike `match_type` |

**Not native, and this matters:**
- **Branded vs non-branded does not exist anywhere in the API.** No field, no enum, no label. Analysts regex the keyword/search-term text against a brand-token list. A simulated file may carry a `brand_flag` **only if presented as an analyst's derived output.**
- **Search volume is not in performance reporting at all.** It comes from `KeywordPlanIdeaService` → `avg_monthly_searches`, which is **monthly, rounded into buckets (10/50/100/500/1K/5K/10K), and not joinable to daily performance.**
- Search-terms report is privacy-thresholded since Sept 2020, so `Σ search_term impressions < Σ keyword impressions` — a credible sim leaves **10–40% unattributed**.

Constraints worth simulating: `absolute_top_IS ≤ top_IS ≤ IS`. The three IS components sum to ≈1.0 but **only approximately** — clipping breaks the identity, so don't enforce it.

### Google Trends — genuinely low-friction

| Property | Detail |
|---|---|
| Values | **integer index 0–100**, not a count or rate |
| Grain | **a 3-year window natively returns weekly data** — exactly our 156 weeks |
| Normalization | each point ÷ total searches for that geo/window, then rescaled 0–100 |
| Hard rule | **exactly one period equals 100** in a single-term pull |
| Zeros | real, meaning "below threshold" — not "no searches" |
| Noise | statistical noise is **deliberately injected** for privacy, most visible at low interest |
| Never | sum, average, or combine two separate pulls without rescaling on an overlap |

Official FAQ: *"Google Trends is not a scientific poll… A spike in a particular
topic does not reflect that a topic is somehow 'popular' or 'winning'."*
Searches from AI Mode and AI Overviews are excluded.

### Google Search Console — the one to avoid here
- Metrics: `clicks`, `impressions` (**doubles in the schema despite being counts**), `ctr` (0–1), `position` (≥1).
- **16-month retention.** A 156-week GSC series is **not obtainable** via the standard API — only via BigQuery bulk export, or by an analyst having pulled monthly for three years.
- **Anonymized queries**: itemized query rows never sum to the site total, and there is no remainder row. Realistic itemized share is 60–90%.
- Branded/non-branded is again analyst-derived, not native.

---

## Sources

Official: [YouTube Analytics metrics](https://developers.google.com/youtube/analytics/metrics) ·
[Google Ads metrics](https://developers.google.com/google-ads/api/fields/v21/metrics) ·
[segments](https://developers.google.com/google-ads/api/fields/v21/segments) ·
[search_term_view](https://developers.google.com/google-ads/api/fields/v21/search_term_view) ·
[Video campaigns](https://developers.google.com/google-ads/api/docs/video/overview) ·
[Impression share](https://support.google.com/google-ads/answer/2497703) ·
[Unique Reach](https://support.google.com/google-ads/answer/9012727) ·
[Search terms privacy thresholds](https://support.google.com/google-ads/answer/11127882) ·
[Meta Ads Insights](https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/) ·
[Insights breakdowns](https://developers.facebook.com/docs/marketing-api/insights/breakdowns/) ·
[GSC searchanalytics.query](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) ·
[GSC data filtering deep dive](https://developers.google.com/search/blog/2022/10/performance-data-deep-dive) ·
[Trends FAQ](https://support.google.com/trends/answer/4365533) ·
[Trends API alpha](https://developers.google.com/search/blog/2025/07/trends-api)

Blog-level, **value ranges only, not authoritative**:
[WordStream Facebook](https://www.wordstream.com/blog/facebook-ads-benchmarks-2025) ·
[WordStream Google Ads](https://www.wordstream.com/blog/2026-google-ads-benchmarks) ·
[Store Growers YouTube](https://www.storegrowers.com/youtube-ads-benchmarks/) ·
[Sovran Meta CPM](https://sovran.ai/benchmarks/meta-ads-cpm-by-industry) ·
[Strike Social Q1 2025](https://strikesocial.com/blog/q1-2025-youtube-ads-benchmark-report/)

All URLs verified HTTP 200.
