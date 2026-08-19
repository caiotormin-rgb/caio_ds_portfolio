# 09 - Activation One-Pager
*Step 09 of 09 | CRISP-DM Phase 6: Deployment | Audience: budget owner.*

This file turns the readout into the next action.

Status: work in progress. This is the activation plan for the synthetic
case-study version of Caio's MMM project framework.

## Recommendation

**Do not move budget yet.** The model found a plausible reallocation, but it did
not pass a pre-set control test. Run one experiment first: a six-week branded
search holdout with about **$62,000** of spend at risk against a **$1.35m**
annual budget line.

## Why Not Reallocate Now

The model says to move money from linear TV into CTV. That direction is correct
against the answer key.

But the model also reports a strong return for branded search, a channel known
to have no true effect in this dataset. That makes the result useful for
prioritizing the next test, but not yet strong enough to carry a budget move.

## First Experiment: Branded Search Holdout

| Item | Plan |
|---|---|
| Test | Turn branded search off in 40% of matched markets |
| Control | Keep branded search on in comparable markets |
| Duration | 6 weeks |
| Spend at risk | About $62,000 |
| Budget line tested | $1.35m per year |
| Primary metric | Total orders in test markets vs. control markets |
| Diagnostic to watch | Whether organic search clicks rise as paid clicks fall |
| Decision threshold | If measured lift is below breakeven, cut branded search and retest at a lower maintenance level |

This experiment answers the exact question the model could not settle: did
branded search create incremental sales, or would those customers have arrived
anyway?

## Then Test the Reallocation

1. **CTV incrementality test.** The model's strongest funding recommendation
   should be tested before money moves at scale.
2. **Linear TV reduction test.** Test the reduction at the practical ceiling
   of about +/-20%, or roughly $630,000 per year, before next year's upfront
   negotiations.

## Then Rebuild the MMM

Use the experiment results to calibrate the next model. An experiment measures
incrementality directly where the MMM can only infer it. Calibration turns the
model from a plausible historical explanation into a more credible budget tool.

## Monday Actions

1. Select test and control markets matched on baseline sales.
2. Confirm the breakeven lift threshold before the test starts.
3. Book the six-week branded-search holdout outside Q4.
4. Define the organic-search monitoring report.
5. Schedule the CTV and linear TV test design review.

## Monitoring

Rebuild the model when any of these occurs:

- A holdout or lift test completes.
- Channel mix shifts by more than 20%.
- A new channel launches.
- Twelve months pass.

Do not refresh this model on a schedule until the identification problem is
addressed.
