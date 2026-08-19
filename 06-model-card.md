# 06 - Model Card
*Step 06 of 09 | CRISP-DM Phase 4: Modeling | Audience: technical reviewer.*

This file states what was fit, what it recovered, what it missed, and what the
model must not be used for.

Status: work in progress. This model card documents the synthetic case-study
version of Caio's MMM project framework.

## Model Verdict

The model predicts revenue well enough to look credible, but it does not recover
the underlying media mechanics reliably enough to move budget from the model
alone.

That is the important result. Predictive fit is not the same as decision
validity.

## Specification

Plain English: revenue is modeled as baseline demand plus the effect of six paid
media channels, where each channel can carry over across weeks and saturate as
spend rises.

Technical form:

```text
log(revenue) ~ baseline + sum(channel effect after carryover and saturation)
```

| Component | Form |
|---|---|
| Sample | 202 settled weeks |
| Carryover | Geometric adstock, theta bounded between 0 and 0.95 |
| Saturation | Hill curve |
| Baseline | Two seasonal waves, linear trend, holiday count, retail-holiday count |
| Control | Fit with and without `category_demand` |
| Estimation | Nonlinear least squares with non-negative media effects |
| Intervals | Residual block bootstrap, 120 replicates, 13-week blocks |

Fit statistic: R2 is 0.8248 with the demand control and 0.8202 without it.

## Assumptions

1. Media effects add across channels.
2. Media effects scale revenue rather than adding the same dollars every week.
3. Advertising can keep working after the spend week.
4. More spend can saturate but cannot create negative sales.
5. Channel behavior is stable across the four-year window.
6. `category_demand` is a valid external control in the synthetic data; this
   would be hard to prove in real data.

## Recovery Against Truth

Because the data is generated, the model can be scored against known answers.
This check is unavailable in a normal client engagement.

| Channel | True marginal ROI | Estimated marginal ROI | True carryover | Estimated carryover |
|---|---:|---:|---:|---:|
| CTV | 3.63 | 7.54 | 0.55 | 0.59 |
| Meta social | 2.39 | 5.34 | 0.40 | 0.69 |
| YouTube | 2.16 | 3.02 | 0.45 | 0.00 |
| Amazon retail | 1.67 | 0.35 | 0.25 | 0.63 |
| Linear TV | 1.20 | 1.51 | 0.70 | 0.63 |
| Branded search | 0.00 | 5.14 | 0.10 | 0.72 |

What worked:

- The model ranked the two most important ends correctly: CTV high, linear TV
  low.
- Linear TV was identified as a saturated channel.
- The model exposed why intervals need to be shown rather than hidden.

What failed:

- ROI levels were inflated roughly 2-3x.
- Carryover was close for only two of six channels.
- Branded search was estimated as valuable even though its true effect is zero.

## Why Recovery Failed

The failures have different causes, but they point to the same lesson: a model
can explain revenue history while still misreading why revenue moved.

| Failure | Likely cause | Business implication |
|---|---|---|
| ROI levels inflated | Media explains only 4.1% of post-seasonality movement, so small attribution errors become large ROI errors | Use ROI directionally, not as a dollar promise |
| Carryover missed | Weekly data does not contain enough clean stop-start patterns to separate this week's effect from prior weeks' effects | Do not report carryover length as a finding |
| Branded search invented | Branded search is almost always on and rises when demand rises, so the model credits it for demand that would have happened anyway | Test incrementality before protecting the spend |
| Amazon underestimated | Amazon is Q4-loaded, so its spend overlaps with the largest seasonal revenue period and is hard to separate from holiday demand | Treat seasonal channels with extra caution |
| CTV overstated | CTV and linear TV are flighted together often enough that the model can identify the direction, but not the exact split | Test CTV before scaling spend |

The most important failure is branded search. It is not just a bad estimate; it
is the kind of bad estimate that would look credible in a real engagement.

## Intended Use

- Rank channels by marginal ROI as a hypothesis generator.
- Identify where the next experiment should be run.
- Demonstrate why average ROI is the wrong budget metric.
- Demonstrate why a model should be calibrated with experiments before
  reallocation.

## Use With Care

- Use the model to prioritize experiments, not as the sole basis for moving
  budget.
- Treat absolute ROI levels as directional because they are inflated in recovery
  testing.
- Treat carryover and saturation parameters as model assumptions unless they are
  calibrated with experiments.
- Read R2 as forecast fit, not as proof that the media effects are correctly
  assigned.
- Re-estimate the model for any new advertiser, category, or channel mix.

## Next

Continue to `07-evaluation.md`.
