# 05 — Analysis / measurement plan
*CRISP-DM Phase 4: Modeling. Cap: 400w.*

> **PRE-REGISTRATION.** Written and committed **before any model is fit**.
> Date written: **2026-08-18**. The commit that adds this file is the proof —
> no modelling code exists in the repository at that point.
>
> **STATUS:** WRITTEN · **Blocked by:** nothing · **Done when:** ✅ committed before the first fit

## Primary metric

**Marginal ROI per channel**, at observed spend. Not average ROI — the ground
truth already shows why: linear TV has the **highest average ROI (5.03) and the
lowest non-zero marginal ROI (1.20)**. An analyst optimising on average ROI funds
the channel that should be cut.

## Method

Hand-rolled, fit by nonlinear least squares (`scipy`), intervals by bootstrap.

- **Outcome:** `log(revenue)`. The DGP is multiplicative.
- **Adstock:** geometric, θ estimated per channel, bounded [0, 0.95], max lag 12 weeks.
- **Saturation:** Hill, α and κ estimated per channel.
- **Baseline:** 2 Fourier harmonics + linear trend + `holiday_count` + `holiday_retail_count`.

**The specification is deliberately correct**: geometric adstock + Hill + log
outcome is exactly how the data was generated, and also what every open-source
MMM tool defaults to. **Recovery is therefore an upper bound, not a realistic
expectation, and `07-evaluation.md` must say so.**

**Frequentist, not Bayesian.** `03` established that this data cannot
corroborate carryover. A prior would supply an answer and the posterior would
look confident; a bootstrap interval simply comes back wide, which is the honest
picture of what the data knows.

## Controls

`category_demand` — built as a genuine confounder, driving both the outcome and
media planning. **Fit with and without it**, reporting the span between the two.

## Sample

**202 settled weeks.** The final 6 are excluded: Amazon conversions restate
for 42 days and Meta's last 2 weeks run ~28% light. This is what a real refresh
does, and the rule is fixed here so it cannot be mistaken for cherry-picking.

## Decision rule — fixed in advance

> Recommend moving budget from channel A to B **only if** B's estimated marginal
> ROI exceeds A's **and the bootstrap interval on the difference excludes 1.0**.

At 4.06% incremental signal this rule **will refuse to recommend on some
channels**. That is the honest outcome, and stating it now means a null reads as
discipline rather than failure.

## Constraints — tiered by how media is actually bought

| Channel | Max shift | Rationale |
|---|---:|---|
| Linear TV | **±20%** | upfront commitments lock months ahead |
| Meta, YouTube, CTV, branded search, Amazon | **±40%** | bought in-flight |

Total budget held constant. **Branded search is included and the optimizer may
act on it** — if its effect is near zero, the recommendation is to cut it.
`09` carries the real-world caveat without softening the finding.

## Validation no simulated media channel with its own spend

Rolling-origin cross-validation with an expanding window, **plus parameter
recovery against the answer key**. Predictive fit here is mostly seasonality: a
model can forecast revenue well while getting every channel's ROI wrong, which is
precisely MMM's failure mode.

## What would make us abandon this approach

1. **Branded search returns a confidently positive ROI.** The model is inventing
   effects, which disqualifies every other estimate it produced.
2. **The channel ranking flips** across CV folds or across the with/without-control span.

Both are checkable before any recommendation is written.

## Reporting US calendar

Bounds are reported as an analyst without ground truth would have to — then the
answer key reveals which end was correct, and by how much. That quantifies what
the ambiguity actually costs.
