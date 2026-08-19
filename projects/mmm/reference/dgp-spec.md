# Data-generating process — specification

> **PRE-REGISTRATION.** Committed **before** any data is generated. The git log
> is the proof. No parameter here may be changed after seeing model output; if
> one must change, it is a new dated entry in `DECISIONS.md` explaining why.

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
