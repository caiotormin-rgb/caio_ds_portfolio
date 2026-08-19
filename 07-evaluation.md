# 07 - Evaluation Memo
*Step 07 of 09 | CRISP-DM Phase 5: Evaluation | Audience: analytics lead.*

Evaluation asks whether the model answered the business question, not just
whether it fit revenue history.

Status: work in progress. This evaluation memo documents the synthetic
case-study version of Caio's MMM project framework.

## Verdict

**Do not ship the reallocation from this model.**

The model points in the right direction: move money into CTV, primarily out of
linear TV. But it also fails the control test that was fixed before modeling:
it reports a confidently positive return for branded search, a channel with a
true effect of zero.

That failure disqualifies the model as a basis for moving money.

## What the Model Would Recommend

The pre-registered rule allowed three channel moves, all pointing toward CTV:

| Move budget from | Move budget to | Estimated advantage | 90% interval |
|---|---|---:|---|
| Linear TV | CTV | 7.61 | [2.39, 13.96] |
| Amazon retail | CTV | 7.47 | [0.27, 13.61] |
| YouTube | CTV | 5.33 | [0.06, 12.13] |

Against the answer key, the direction is broadly right: CTV truly has the
highest marginal ROI, and linear TV is among the lowest.

## Why That Is Not Enough

Branded search was built to have no effect. The model should have estimated it
near zero or returned an uncertain interval.

It did not:

| Check | Result |
|---|---:|
| True marginal ROI | 0.00 |
| Estimated marginal ROI | 5.14 |
| 90% interval | [0.64, 10.93] |

This is not a noisy estimate that happened to be wrong. It is a confident wrong
answer.

## Interpretation

The model cannot distinguish a channel that causes sales from a channel that is
always on and moves with demand. Branded search has exactly that shape: when
people are already interested in the brand, they search for it and click ads.

The other misses are consistent with the same identification problem. Media is a
small signal after seasonality is removed, so ROI levels are easy to overstate.
Carryover is also hard to recover from weekly data unless channels have clean
on/off patterns. CTV and linear TV often run in the same periods, so the model
can see the broad streaming-vs-TV direction more easily than it can assign the
exact return to each channel.

In a real engagement, the answer key would not exist. The branded-search estimate
would look as credible as the CTV estimate, and the model would be tempting to
ship.

## What Still Worked

- The model correctly found the direction of the TV-to-CTV opportunity.
- The pre-registered rule refused to act on 27 of 30 channel pairs.
- The failure was specific and useful: it identified the need for an
  incrementality test.

## Limitations

- The data-generating process is favorable to the model, so recovery here is an
  upper bound.
- ROI levels are inflated and should not be quoted as business truth.
- Carryover was recovered for only two of six channels.
- Only one model was fit; production MMM workflows often compare many plausible
  models and select from a fit/plausibility frontier.

## Decision

Do not move budget yet. Run a branded-search incrementality test first. If the
test shows branded search creates real lift, the model failure becomes evidence
that the synthetic setup was unrealistic. If the test shows little or no lift,
cut branded search and use the experiment to calibrate the next MMM.

## Next

Continue to `08-readout.md`.
