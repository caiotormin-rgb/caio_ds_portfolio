# 07 — Evaluation memo
*CRISP-DM Phase 5: Evaluation. Cap: 600w.*

> **Evaluation is not model diagnostics.** Goodness-of-fit lives in `06`.
> This asks whether the business question in `00` actually got answered.
>
> **STATUS:** WRITTEN · **Done when:** ✅ the pre-registered rule applied and the answer stated, whichever way it went

## The verdict

**The model is disqualified. The reallocation must not be shipped from it.**

A pre-registered abandon criterion fired. That the headline recommendation
happens to be *correct* does not rescue it — and explaining why is the point of
this memo.

## Against the pre-registered decision rule

> Recommend moving budget from A to B only if B's marginal ROI exceeds A's **and
> the bootstrap interval on the difference excludes 1.0.**

**3 of 30 channel pairs pass**, and all three point the same way:

| From | To | Median gap | 90% interval |
|---|---|---:|---|
| Linear TV | CTV | 7.61 | [2.39, 13.96] |
| Amazon retail | CTV | 7.47 | [0.27, 13.61] |
| YouTube | CTV | 5.33 | [0.06, 12.13] |

The rule permits a recommendation: **move budget into CTV, primarily out of
linear TV.** Against the answer key that is **correct** — CTV genuinely has the
highest marginal return (3.63) and linear TV among the lowest (1.20).

The rule also did its main job: it **refused** on 27 of 30 pairs. At 4.06%
incremental signal, most channel comparisons are not resolvable, and pre-committing
to the threshold means those silences read as discipline rather than omission.

## Against the pre-registered abandon criteria — **TRIGGERED**

> Abandon if branded search returns a **confidently positive** ROI.

| | |
|---|---|
| True marginal ROI | **0.00** — by construction |
| Estimated | **5.14** |
| 90% interval | **[0.64, 10.93]** — excludes zero |

**The model confidently found a large effect for a channel that has none.**
Not an imprecise estimate that happens to be wrong — a confident one.

Under the criterion fixed in `05` before any model existed, that disqualifies
every other estimate the model produced. A model that manufactures effects cannot
be trusted where it happens to agree with truth.

## Why this is the useful outcome

Interval coverage is otherwise reasonable: **truth falls inside the 90% interval
for 5 of 6 channels.** The one miss is the null. So the failure is specific and
diagnosable — the model does not systematically mis-estimate, it *cannot
distinguish a channel that works from one that is merely always-on and correlated
with demand*.

Branded search is smooth, always-on, and moves with the business. Every property
that makes it a top performer in a naive read is also what makes its null
undetectable. **This is exactly what eBay found experimentally in 2015** when
branded search ads turned out to be close to worthless.

**And in a real engagement, this check would be unavailable.** We only know the
truth because we built it. Without an answer key, nothing in the model output
flags branded search as suspect — its estimate looks as credible as CTV's.

That is the finding: **MMM alone cannot detect an invented effect.** The missing
instrument is an incrementality experiment — a geo holdout on branded search
would settle in weeks what this model gets confidently wrong.

## What the control decision cost

Fit with and without `category_demand`: R² 0.8248 vs 0.8202. Estimates move, but
the ranking is stable across both — the span is not what disqualifies this model.

## Limitations

- **The specification is deliberately correct.** Recovery here is an **upper
  bound**; a real advertiser's response is not literally Hill.
- **Levels are inflated 2–3×** and must never be quoted.
- **Carryover recovered on 2 of 6 channels.** YouTube's θ collapsed to 0.00
  against a true 0.45, branded search's inflated to 0.72 against 0.10.
- **Rank correlation is +0.60** — the ends are right, the middle is not.
- One model was fit. Industry practice (Robyn) generates thousands and selects on
  fit **and business plausibility**. A plausibility criterion is precisely what
  would have flagged branded search.

## What would falsify this conclusion

An incrementality test on branded search returning a positive lift. That would
mean the model was right and the DGP unrealistic — and it is the one experiment
that would settle it.

## Where this model would break

Any advertiser with an always-on channel correlated with demand — which is most
of them, since branded search, retargeting and affiliate all share that shape.
