# Data-generating process — specification

> **PRE-REGISTRATION.** Committed **before** any data is generated. The git log
> is the proof. No parameter here may be changed after seeing model output; if
> one must change, it is a new dated entry in `05-analysis-plan.md` explaining why.

**Written:** 2026-08-18 · **Seed:** 20260818 · **Market:** US · **Currency:** USD

## Window

208 weeks, **2021-01-04 → 2024-12-23**, Monday-dated. Four complete calendar
years (52/52/52/52) — no partial-year tails.

## Structure

```
revenue_t = baseline_t × (1 + Σ_c contribution_{c,t}) × noise_t
```

Multiplicative, because seasonality in retail scales the whole business rather
than adding to it — and because the EDA showed a 3.3x swing, which an additive
baseline forces into the wrong shape.

### Baseline
| Component | Specification |
|---|---|
| Level | 1,800,000 USD/week |
| Seasonality | 2 Fourier harmonics, period 52.18, peak/trough ≈ **3.0x**, peak in late November |
| Trend | +0.4%/year — small but non-zero, so trend/media separation is tested |
| Holidays | US federal calendar, per-holiday multipliers. Thanksgiving week ×1.35, Christmas week ×1.25, Independence Day ×0.92, others ×1.0 |
| `category_demand` | AR(1), φ=0.6, exogenous. **Drives baseline AND media planning** — a genuine confounder, correctly signed |

### Channels

`adstock` is geometric with decay θ. `saturation` is Hill:
`h(x) = x^α / (x^α + κ^α)`. Contribution = `β · h(adstock(spend, θ))`.

**Operating point** = median adstocked spend ÷ κ. Above 1 means past the knee.

| Channel | Budget share | θ (decay) | α (shape) | Operating point | β | Role |
|---|---:|---:|---:|---:|---:|---|
| **TV** | 45% | **0.70** | 1.6 | **2.5 — well past knee** | 0.075 | Over-invested. *Cut.* |
| **Print** | 20% | 0.30 | 1.4 | 1.2 — at the knee | 0.030 | **Seasonal decoy** — spend 60% concentrated in Q4 |
| **Display** | 15% | 0.20 | 1.5 | 1.0 | **0.000** | **The dud.** True effect zero |
| **Search** | 12% | **0.10** | 1.8 | 0.8 | 0.055 | Always-on, short carryover. Hard to identify |
| **Social** | 8% | 0.40 | 1.7 | **0.35 — steep part** | 0.050 | Under-invested. *Fund.* |

**Media plans** (calibrated to what we measured on real and demo data):

| Channel | Dark weeks | Planning note |
|---|---:|---|
| TV | ~45% | Flighted bursts. **Planning correlated with print (ρ≈0.45)** so VIF exceeds 1 |
| Print | ~50% | Q4-loaded, the decoy mechanism |
| Display | ~20% | Mostly on |
| Search | **~2%** | Always-on, smooth. AC(1) target ≈ +0.7 |
| Social | ~35% | Flighted |

### Noise
Multiplicative lognormal, σ **tuned to land media's incremental R² in 8–10%**
after seasonality is controlled. Robyn gave 2.6pp (too little to learn from), the
real retailer 4.4pp. **Achieved value is recorded post-generation and never
re-tuned.**

## Ground truth recorded

Per channel: θ, α, κ, β, true weekly contribution, **true ROI**, **true marginal
ROI at observed spend**, and the **true optimal reallocation** at fixed total
budget. These are the answer key `07-evaluation.md` scores against.

## Source projection — 5 exports, each in its platform's real shape

Truth is generated once, then projected into five exports with different units,
grains and defects. See `reference/platform-data-specs.md` for the verified
field specifications.

| Channel | Simulated source | Shape |
|---|---|---|
| Search | Google Ads API `keyword_view` | `cost_micros`, `ctr` ratio 0–1, fractional `conversions`, `search_impression_share` clipped, native Monday `segments.week` |
| Social | Meta Ads Insights | **All numerics as JSON strings**, `ctr` **percent 0–100**, `frequency = impressions/reach`, **daily rows** |
| Display | Google Ads, Display network | Micros, different report shape from search |
| TV | **Agency spreadsheet** | Spend + GRPs, monthly invoice vs weekly airings |
| Print | **Agency spreadsheet** | Insertion dates, rate-card cost, not week-aligned |

## Planted defects — 12, for the detection-rate report

The dataset is synthetic and stated as such. The EDA notebook demonstrates the
**detection method**, not a discovery. Detection rate is reported honestly.

| # | Defect | Source | Class |
|---|---|---|---|
| 1 | `ctr` on 0–100 while Google is 0–1 | Meta | unit mismatch |
| 2 | Cost in micros, unconverted | Google ×2 | unit |
| 3 | All numerics serialised as strings | Meta | type |
| 4 | Daily rows requiring rollup | Meta | grain |
| 5 | **Reach non-additive** — summing daily overstates weekly by 30–70% | Meta | grain trap |
| 6 | Impression share clipped, `0.0999` sentinel | Search | encoding |
| 7 | Fractional conversions | Search | type expectation |
| 8 | Monthly invoice ≠ sum of weekly airings | TV | reconciliation |
| 9 | Insertion dates not week-aligned | Print | grain |
| 10 | One duplicated row | Display | integrity |
| 11 | Final 2 weeks understated (28-day settling) | Meta | recency |
| 12 | A block of rows in a different currency unit | TV | unit |

## Explicitly out of scope

Geo panel · reach/frequency modelling · competitive response dynamics ·
population-state simulation (that is AMSS, parked) · multiple products.

---

# AMENDMENT 1 — 2026-08-18, before any data generated

Recorded as a dated amendment rather than a silent edit. The original above is
committed at `85ea4fa`; nothing has been generated, so pre-registration integrity
is intact. **Reason for amendment:** Caio asked for a modern digital channel mix.

## What changed and why

**1. Channel mix modernised — 5 channels become 6.** Print and generic display
are dropped; CTV, YouTube and Amazon retail media are added. The original mix was
a 2015-era plan, which dates the project wrongly for a 2021-2024 window.

**2. The dud becomes branded search.** Previously a generic zero-effect channel.
Branded search tests the same thing — does the model invent an effect — but poses
a question marketing teams genuinely argue about: when someone searches your brand
and clicks your ad, would they have converted anyway? It is always-on, smooth, and
correlates beautifully with revenue, so it is *supposed* to look like a top
performer. A model that correctly returns near-zero incremental effect is a real
result, not a synthetic curiosity.

**3. The seasonal decoy becomes Amazon retail media.** Retail media genuinely
spikes in Q4 (Prime Day, Black Friday, holiday), so a Q4-loaded decoy is realistic
rather than contrived — and it is a channel that barely existed in 2019.

**4. The under-invested channel is CTV, not social.** This makes the
recommendation coherent instead of arbitrary: *linear TV is over-invested while
the audience moved to streaming.* That is the defining media shift of the chosen
window. "Cut TV, fund Meta" would be two unrelated observations sharing a budget.

**5. Deliberate collinearity moves from TV-print to linear TV <-> CTV, rho ~ 0.4.**
The original placement was realistic but analytically pointless — nobody cares
whether TV and print can be separated. **Separating linear from CTV *is* the
recommendation**, so the model's hardest task now coincides with the decision's
hardest question. If it succeeds, that is a genuine result; if it fails, that is
an honest and reportable failure of the kind a real engagement hits.
**Risk to monitor:** too much correlation makes them unidentifiable rather than
merely hard. Achieved adstock-pair separability is recorded post-generation using
the same diagnostic that corrected the search-adstock error.

## Revised channels

| Channel | Budget | θ | α | Operating pt | β | Role |
|---|---:|---:|---:|---:|---:|---|
| **Linear TV** | 28% | **0.70** | 1.6 | **2.5 past knee** | 0.075 | over-invested → *cut* |
| **Meta social** | 18% | 0.40 | 1.6 | 0.8 | 0.055 | solid performer |
| **YouTube** | 16% | 0.45 | 1.5 | 1.1 | 0.045 | mid; carries reach & frequency |
| **CTV / streaming** | 14% | 0.55 | 1.7 | **0.35 steep** | 0.050 | under-invested → *fund* |
| **Search — brand** | 12% | **0.10** | 1.8 | 0.9 | **0.000** | **the incrementality test** |
| **Amazon retail media** | 12% | 0.25 | 1.4 | 1.2 | 0.030 | **seasonal decoy**, 60% Q4 |

Six channels, ~18 media parameters against 208 weeks. Seven would breach the
observations-to-parameter guideline.

## Revised media plans

| Channel | Dark weeks | Planning note |
|---|---:|---|
| Linear TV | ~45% | Flighted bursts. **Correlated with CTV, rho ~ 0.4** |
| CTV | ~30% | Flighted, correlated with linear TV |
| YouTube | ~25% | Mostly on |
| Meta social | ~35% | Flighted |
| Search — brand | **~2%** | Always-on, smooth. AC(1) target ~ +0.7 |
| Amazon retail | ~20% | **60% of annual spend in Q4** — the decoy mechanism |

## Revised source projection

| Channel | Simulated source | Verified? |
|---|---|---|
| Search — brand | Google Ads API `keyword_view` | ✅ `platform-data-specs.md` |
| YouTube | Google Ads API, video campaign | ✅ `platform-data-specs.md` |
| Meta social | Meta Ads Insights | ✅ `platform-data-specs.md` |
| CTV / streaming | Programmatic DSP export | ⏳ research pending |
| Amazon retail media | Amazon Ads API | ⏳ research pending |
| Linear TV | Agency spreadsheet — no API exists | n/a, by construction |

The two pending specs must be verified before their exports are written. **Field
names will not be invented** — that is the exact tell the platform research
warned about.

## Defects — REVISED after the Amazon/DV360 research

The research surfaced better defects than the ones originally invented: these are
documented platform behaviours rather than plausible-sounding faults. **14 planted.**

| # | Defect | Source | Class |
|---|---|---|---|
| 1 | `ctr` on 0-100 while Google is 0-1 | Meta | unit mismatch |
| 2 | Cost in micros, unconverted | Google Ads ×2 | unit |
| 3 | All numerics serialised as strings | Meta | type |
| 4 | Daily rows requiring rollup | Meta, Amazon | grain |
| 5 | **Reach non-additive** — summing daily overstates weekly 30-70% | Meta, DV360 | grain trap |
| 6 | Impression share clipped, `0.0999` sentinel | Search | encoding |
| 7 | Fractional conversions | Search | type expectation |
| 8 | Monthly invoice ≠ sum of weekly airings | TV sheet | reconciliation |
| 9 | A block of rows in a different currency unit | TV sheet | unit |
| 10 | **Zero-activity rows omitted entirely** — daily row counts fluctuate, and a naive join cannot distinguish "no spend" from "missing" | Amazon | absence vs zero |
| 11 | **Last ~6 weeks of conversions understated** — 42-day restatement horizon (traffic settles d+3, conversions at d+1/7/28 on the interaction date) | Amazon | vintage |
| 12 | **`Grand Total` row after a blank line, misaligned to the header** — naive `read_csv` ingests it as data | DV360 | file structure |
| 13 | **Reach delivered in a separate file** from impressions, because DV360 cannot return both in one report type | DV360 | structural |
| 14 | **Week-boundary misalignment** — `pandas.resample("W")` defaults to Sunday-ending while Google Ads `segments.week` is Monday-start, so one source lands a day off | pipeline | silent corruption |

Defects 10-14 replace weaker invented ones. Each is a documented behaviour with a
citation in `platform-data-specs.md`, so the EDA notebook is demonstrating
detection of **real** failure modes rather than ones we made up to be findable.

---

# AMENDMENT 2 — 2026-08-18, during calibration

Two parameters changed while calibrating. Recorded rather than quietly applied,
because the original values are committed at `85ea4fa`/`ce906f1`.

**1. Signal target lowered from 8-10% to 4-6% incremental R².**
The original band was aspirational. Measured against a 3x seasonal swing, hitting
9% requires media to drive roughly half of all revenue — implausible, and it would
have made the modelling task artificially easy. **Reference points from the audit:
the real retailer achieved 4.4pp, Robyn 2.6pp.** The revised band is realistic and
still ~1.6x Robyn. **Achieved: 0.0406.**

**2. CTV beta raised 0.145 → 0.320.**
At the pre-registered value CTV's marginal ROI came out at 1.65, below Meta's
2.39 — so the designed "fund CTV" recommendation did not hold. The operating
point (0.28, deep on the steep part) was right; the coefficient was too small for
that to translate into the highest marginal return. **This is a scenario-design
correction, not a fit to model output — no model has been run.**

## Calibration record

| Parameter | Value | How chosen |
|---|---|---|
| `beta_scale` | 1.25 | searched to hit the target band |
| `noise_sigma` | 0.18 | searched jointly with beta_scale |
| achieved incremental R² | **0.0406** | measured against the **true** transforms, not `log1p(spend)` — a naive spec understates genuinely present signal, and calibrating to it would have inflated the true effect |
| media / revenue | 9.1% | emergent, not targeted |
| seasonality peak/trough | 3.00x | as specified |

## Ground truth as generated

| Channel | Share | Avg ROI | **Marginal ROI** | Designed role | Holds? |
|---|---:|---:|---:|---|---|
| CTV | 14% | 2.62 | **3.63** | under-invested → fund | ✅ highest marginal |
| Meta social | 18% | 3.18 | 2.39 | solid performer | ✅ |
| YouTube | 16% | 3.64 | 2.16 | mid | ✅ |
| Amazon retail | 12% | 3.42 | 1.67 | seasonal decoy | ✅ |
| **Linear TV** | **28%** | **5.03** | **1.20** | over-invested → cut | ✅ **the trap** |
| Branded search | 12% | **0.00** | **0.00** | the dud | ✅ exactly zero |

**Linear TV is the result worth having:** it has the *highest average ROI of any
channel* and the *lowest non-zero marginal ROI*. An analyst reading average ROI
concludes TV is the best performer and funds it further. The correct answer is to
cut it. That single inversion is the case for marginal analysis, and the model
either finds it or does not.
