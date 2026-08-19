# 05 - Analysis / Measurement Plan
*Step 05 of 09 | CRISP-DM Phase 4: Modeling | Audience: technical reviewer.*

This file fixes the metric, model, sample, and decision rule before the model is
fit.

Status: work in progress. This plan documents the synthetic case-study version
of Caio's MMM project framework.

## Primary Metric

Use **marginal ROI**: the expected return from the next dollar spent in each
channel.

Do not optimize on average ROI. Linear TV is designed to show why: it has the
highest historical average ROI, but the lowest non-zero marginal ROI. It looks
like the best channel if you ask the wrong question.

## Decision Rule

Recommend moving budget from channel A to channel B only when the model can say,
with uncertainty included, that the next dollar in B is meaningfully better than
the next dollar in A.

Operationally: B's estimated marginal ROI must exceed A's, and the bootstrap
interval on the difference must exclude 1.0.

This rule is intentionally strict. If the data cannot resolve a channel pair,
the answer should be "do not move money from this model."

## Model

The model is a marketing mix model fit with open-source Python:

| Component | Choice | Why |
|---|---|---|
| Outcome | `log(revenue)` | Retail seasonality scales the business rather than adding a fixed amount |
| Carryover | Geometric adstock | Advertising can keep working after the spend week |
| Saturation | Hill curve | Additional spend can still help, but each extra dollar may help less |
| Baseline | Two annual seasonal waves, trend, holiday counts | Controls the large non-media pattern before estimating media |
| Estimation | Nonlinear least squares | Transparent and reproducible |
| Intervals | 13-week block bootstrap | Preserves seasonal dependence better than resampling individual weeks |

The specification is deliberately favorable to the model: it matches how the
data was generated and resembles common open-source MMM defaults. Recovery here
is therefore an upper bound, not a promise of real-world performance.

## Controls

Fit with and without `category_demand`, an external demand variable that drives
both sales and media planning in the simulation. Report whether the channel
ranking survives that sensitivity check.

## Sample

Fit on 202 settled weeks. The final 6 weeks are excluded because Meta and Amazon
conversion reporting can still change near the end of a refresh window.

## Budget Constraints

| Channel | Maximum move | Rationale |
|---|---:|---|
| Linear TV | +/-20% | Upfront commitments make large short-term moves unrealistic |
| Meta social | +/-40% | Bought more flexibly |
| YouTube | +/-40% | Bought more flexibly |
| CTV | +/-40% | Bought more flexibly |
| Branded search | +/-40% | Bought more flexibly |
| Amazon retail media | +/-40% | Bought more flexibly |

Total spend must remain fixed.

## Abandon Criteria

Abandon the model as a basis for reallocation if either condition occurs:

1. Branded search receives a confidently positive ROI, even though its true
   effect is zero.
2. The channel ranking flips across validation folds or across the with/without
   demand-control sensitivity check.

The first criterion is the central test. It asks whether the model can avoid
inventing a return for an always-on channel that moves with demand.

## Validation

Use two checks:

- Forecast validation: does the model predict revenue reasonably?
- Recovery validation: does the model recover the known answer key?

Forecast validation alone is not enough. A model can predict seasonal revenue
well while getting media ROI wrong.

## Next

Continue to `06-model-card.md`.
