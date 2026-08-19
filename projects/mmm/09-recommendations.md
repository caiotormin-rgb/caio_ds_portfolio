# 09 — Activation one-pager
*CRISP-DM Phase 6: Deployment. Cap: 400w.*

> **STATUS:** WRITTEN · **Done when:** ✅ actionable Monday without a follow-up question

## The recommendation

**Do not move budget yet.** The model failed a test we set before running it, so
it cannot carry a reallocation. **Run one experiment first — it costs about
$62,000 and settles a $1.35m-a-year question in six weeks.**

## Why we are not recommending the reallocation

The model says shift budget from linear TV into CTV. It also reports a **strong
return on branded search — a channel we can show has none.** Not an uncertain
estimate: a confident one, with an interval that excludes zero.

A model that manufactures a return where none exists cannot be trusted on the
returns it reports elsewhere, even where it happens to be right. Nothing in the
output flags branded search as the suspect one — its estimate looks exactly as
credible as CTV's.

## Do this first — branded search geo holdout

| | |
|---|---|
| **Test** | Switch branded search off in 40% of markets, matched to the rest on baseline sales |
| **Duration** | 6 weeks |
| **Spend at risk** | **~$62,000** — against a $1.35m annual line item |
| **Primary metric** | Total orders in test markets vs control, difference-in-differences |
| **Watch** | Whether organic search clicks rise as paid falls. That is the cannibalisation question |
| **Decide before starting** | The lift below which branded search gets cut. Fix it now, not after |

This is the same test **eBay ran in 2015**, which found their branded search ads
were close to worthless. It is cheap, fast, and it resolves the exact failure
that disqualified the model.

## Then, in order

1. **CTV incrementality test** — before moving real money into it. The model's
   most confident recommendation deserves the most scrutiny, not the least.
2. **Linear TV reduction test.** Upfront commitments cap movement at **±20%, or
   ~$630,000 a year.** Test at that ceiling before negotiating next year's
   upfronts, when the decision becomes expensive to reverse.

## Then rebuild the model

Feed the experiment results back in as priors. Both Meridian and Robyn support
this, and it is current best practice: an experiment measures incrementality
directly where a model can only infer it. That converts the model from something
that produced a plausible wrong answer into something calibrated against a
measured one.

## What to do Monday

1. Pick the test and control markets; check they match on baseline sales.
2. Write down the lift threshold that would cut branded search. Circulate it.
3. Book the holdout with the search team for a 6-week window outside Q4.

## Monitoring

Rebuild when any of these occurs: an experiment completes, the channel mix shifts
more than 20%, a new channel launches, or 12 months pass. **Do not refresh a
disqualified model on a schedule** — fix the identification problem first.
