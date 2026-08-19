# 06 — Model card
*CRISP-DM Phase 4: Modeling. Cap: 600w.*

> **STATUS:** WRITTEN · **Blocked by:** nothing
> **Done when:** ✅ a stranger could rebuild this and knows what not to use it for

## Specification

`log(revenue) ~ baseline + Σ βᶜ · Hill(Adstock(spendᶜ))`, fit on **202 settled
weeks** (D17).

**Two-stage**, as Robyn and most production MMMs are built: an outer optimiser
searches the 18 nonlinear transform parameters; given those, coefficients are
solved in closed form with media constrained non-negative. This keeps the
nonlinear search to 18 parameters rather than 33 on 202 rows.

| Component | Form |
|---|---|
| Carryover | Geometric adstock, θ ∈ [0, 0.95], truncated at 12 weeks |
| Saturation | Hill, α ∈ [0.5, 3.0], κ anchored to median adstocked spend |
| Baseline | 2 Fourier harmonics + linear trend + holiday count + retail-holiday count |
| Control | `category_demand`; **fit with and without** (D10/D23) |
| Estimation | Nonlinear least squares (L-BFGS-B, 3 restarts), non-negative media |
| Intervals | **Residual** block bootstrap, 120 replicates, 13-week blocks |

**Fit:** R² 0.8248 with the control, 0.8202 without.

## Assumptions

1. Media effects are **additive across channels** and multiplicative on the baseline.
2. Carryover is **geometric** — a fixed proportional decay each week.
3. Response **saturates** and never turns negative (media coefficients ≥ 0).
4. Transform parameters are **constant over four years** — no evolving efficiency.
5. `category_demand` is **exogenous**. True here by construction; unverifiable on real data.

## Specification is deliberately correct

Geometric adstock + Hill + log outcome is **exactly how the data was generated**
(D1). It is also what every open-source MMM tool defaults to, so this is standard
practice rather than a shortcut — but it means **recovery here is an upper bound,
not a realistic expectation.** A real advertiser's response is not literally Hill.

## Validation — recovery against known truth

The check no real engagement can run.

| Channel | True mROI | Est. mROI | True θ | Est. θ |
|---|---:|---:|---:|---:|
| CTV | 3.63 | **7.54** | 0.55 | **0.59** ✅ |
| Meta social | 2.39 | 5.34 | 0.40 | 0.69 ✗ |
| YouTube | 2.16 | 3.02 | 0.45 | **0.00** ✗ |
| Amazon retail | 1.67 | 0.35 | 0.25 | 0.63 ✗ |
| Linear TV | 1.20 | **1.51** | 0.70 | **0.63** ✅ |
| Branded search | **0.00** | 5.14 | 0.10 | 0.72 ✗ |

**What recovers well: the ranking at the ends.** CTV is correctly identified as
the highest marginal return and linear TV among the lowest — which is the entire
reallocation decision.

**What does not recover: levels and carryover.** Marginal ROIs are inflated
roughly 2–3×. Carryover lands close on only 2 of 6 channels; YouTube's θ collapses
to zero and branded search's inflates to 0.72 against a true 0.10.

**This was predicted.** `03-data-quality.md` established from raw data alone that
carryover could not be corroborated and that the specification would have to carry
it. That is now confirmed against truth rather than asserted — and it is why the
response curves cannot be presented as measurements.

## Intended use

- **Ranking channels by marginal return**, to direct a constrained reallocation.
- **Identifying the saturated channel** — the one with high average and low
  marginal return.
- Demonstrating that seasonality must be controlled before any media claim.

## Prohibited use

- **Do not quote absolute ROI levels.** They are inflated 2–3× and every interval
  is wide.
- **Do not present response curves as measured.** No saturation curvature was
  visible in the data; the Hill shape comes from the functional form.
- **Do not report carryover length as a finding.** Two of six recovered. A θ from
  this model is a modelling artefact, not evidence.
- **Do not treat the fit statistic as validation.** R² 0.82 is mostly seasonality
  — the model predicts revenue well while getting four of six carryover
  parameters wrong. That gap *is* MMM's characteristic failure mode.
- **Do not transfer these parameters to another advertiser.**
