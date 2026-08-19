# 03 - Data Readiness Memo
*Step 03 of 09 | CRISP-DM Phase 2: Data Understanding | Audience: analytics lead.*

This memo explains why the public Robyn candidate data was rejected and why the
project moved to a generated dataset with known truth.

Status: work in progress. This memo documents the candidate-data audit for the
synthetic case-study version of Caio's MMM project framework.

## Verdict

The Robyn file was clean, but it could not support the final decision. It had
too little media signal, an important control variable that could not be
interpreted, and no answer key for validating ROI estimates.

That made it useful as an audit exercise, not as the model-of-record input.

## What Was Usable

- 208 consecutive weekly rows.
- No missing weeks, duplicate weeks, negative spend, or zero-revenue weeks.
- Five named paid channels with enough on/off variation to inspect flighting.
- Clear evidence that seasonality must be controlled before interpreting media.

Clean data, however, is not the same as decision-ready data.

## Why It Failed

| Issue | Business meaning |
|---|---|
| Seasonality explained 80.7% of revenue | Most visible movement was calendar-driven, not media-driven |
| Paid media added only 2.6 percentage points beyond seasonality | The budget signal was too small for a credible reallocation |
| `competitor_sales_B` correlated 0.92 with revenue | The strongest non-media variable could not be interpreted cleanly |
| True parameters were unpublished | Any ROI estimate would be impossible to score |
| No visible saturation curvature | Response curves would mostly come from the model form, not the data |

## What This Ruled Out

- Year-over-year framing, because the first and last years were partial.
- One-off event flags as controls.
- Point-estimate ROI as a headline.
- Carryover or saturation curves presented as observed facts.
- A reallocation recommendation without either an answer key or an experiment.

## What Carried Forward

The audit shaped the generated dataset:

- Seasonality needed to be large enough to create a real modeling problem.
- Media signal needed to be realistic but not invisible: target incremental R2
  was set to 4-6%, and the generated value was 4.1%.
- Media channels needed realistic flighting and correlation, especially linear
  TV and CTV.
- One channel needed a known zero effect so the model could be tested for
  manufactured lift.

## Decision

Generate a synthetic dataset from a pre-registered process, record the true
answers, and test whether the model recovers the decision that a budget owner
would need.

## Next

Continue to `04-data-prep.md`.
