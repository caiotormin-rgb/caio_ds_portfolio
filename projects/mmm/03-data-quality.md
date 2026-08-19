# 03 — Data readiness memo + initial EDA
*CRISP-DM Phase 2: Data Understanding. Cap: 600w.*

> **STATUS:** WRITTEN
> **Blocked by:** nothing
> **Done when:** ✅ completeness, sufficiency, patterns and an explicit "what this rules out"
>
>
> **ROLE CHANGED simulated dataset.** This memo assesses **Robyn's `dt_simulated_weekly`**,
> which was the candidate modelling dataset when it was written. It is no longer
> that — the project now generates its own data. Nothing here is retracted: every
> figure was measured and remains true of that dataset. **Its role is now the
> evidence that justified simulating**, and the closing section states that
> conclusion. A second readiness pass on the generated data follows in
> `notebooks/02_eda.ipynb` once it exists.
>
> Written from the reads in `notebooks/01_eda.ipynb`. Sections 1 and 5 of that
> notebook were Claude-drafted at Caio's request; everything else is his,
> captured during the EDA interview of 2026-08-18.

## Completeness

Clean. 208 consecutive Monday weeks, no gaps, duplicates, missing values,
negative spend or zero-revenue weeks — asserted on every run by `src/01_load.py`.

Two constraints rather than defects:

- **`events` is dead.** 206 of 208 weeks are `"na"`; `event1` and `event2` occur
  once each. Unusable at n=1.
- **Partial years at both ends** (2015: 6 weeks, peak only; 2019: 45, no
  November). Raw year-over-year comparison is an artefact.

## Sufficiency

208 rows against five channels each needing a coefficient, a decay and a
saturation parameter, plus controls and seasonality. Workable, not generous.

**Identifying variation is ample** — CV 0.79–1.94, max/min to 1,518×, and 10–15
dark runs of 3+ weeks in each flighted channel. Exactly where Meridian failed.

**But variation is not the binding constraint. Signal is.** Seasonality alone
explains **80.7%** of revenue; all five channels together add **2.6 percentage
points** on top. That is the entire signal budget for this project.

## Patterns worth carrying into modeling

- **Seasonality dominates and was never controlled in any first-pass chart.**
  Revenue swings 3.31× (June 0.87m → November 2.87m), no trend (p = 0.94). Two
  Fourier harmonics suffice — one already captures 0.792 of the 0.807 three reach.
- **Removing seasonality reverses the channel ranking.** TV is strongest under
  all four treatments tried (0.29–0.31); paid search's raw lead of 0.443 falls to
  0.09–0.16; Facebook's apparent efficiency collapses from 0.318 to 0.007–0.113.
  Over-correction is not the risk — only 4–22% of each channel is seasonally
  absorbable.
- **Media-to-media collinearity is a non-issue: VIF 1.03–1.05.** Unusual, and it
  removes the most common reason MMMs come out unstable.
- **Decay is identifiable for all five** — minimum adstock-pair correlation
  0.59–0.61 flighted, 0.80 search. Oscillation identifies decay, not darkness;
  search is weakest because it is smooth (AC(1) +0.712, negative elsewhere).

## Problems

**1. `competitor_sales_B` correlates 0.92 with revenue** — against 0.44 for the
best channel. Entered as-is it absorbs nearly all outcome variance and media is
estimated off a small residual. It is a confounder, a mediator, or a seasonality
proxy, and **the data cannot distinguish them.** `newsletter` has the same
problem in miniature: +0.52 with search, ~0 with everything else, and a symmetric
lead/lag profile peaking at zero — the signature of a common cause.
*Fork resolved at the reported span: fit both ways and report the span.*

**2. Out-of-home takes 61.9% of budget and is weakest by every measure** — raw
correlation +0.095, at or below zero under all four seasonality treatments,
+0.13m across spend quintiles against Facebook's +0.97m on a twentieth of the
budget. Three readings stay open: `ooh_S` is a grouping not a channel; the
distortion is deliberate in the simulation; or OOH is a branding lever whose
consistent lift weekly correlation cannot see.

**3. No saturation curvature anywhere.** All five slope upward, none bend.

## What this rules out

- **Year-over-year framing**, given partial years at both ends.
- **`events` as a control**, at n=1.
- **Point estimates as headline numbers.** At 2.6pp of incremental signal,
  intervals will be wide and a point estimate would be dishonest.
- **Response curves as an empirical finding.** With no visible curvature, the
  Hill shape comes from the functional form, not the data.
- **Any carryover length presented as evidence.** Raw cross-correlation always
  draws a decay curve in seasonal data; deseasonalised, every lag profile is
  noise. The data does not decide this — the specification will, and `05` must
  say so.
- **Exposure-based specification.** Tested and rejected at the spend-not-exposure decision on evidence.

## Open questions for Phase 3

1. Is `ooh_S` one channel or a bucket? Nothing here answers it, and the
   recommendation reads very differently either way.
2. Does `newsletter` enter the model, and on which side of the the reported span bounds?
3. Holiday features: count or per-holiday flags? Four weeks carry two holidays,
   so a flag discards information. Reformation Day (2017) is n=1.

---

## Conclusion — why this dataset was not used

The problems above are not tidiness issues. Two of them are fatal to the
deliverable, and neither can be modelled away:

**1. There is almost nothing to model.** Seasonality alone explains 80.7% of
revenue; all five channels together add 2.6 percentage points. Every interval
would be wide, and a reallocation built on that is a recommendation nobody can
act on.

**2. The strongest non-media variable is undecidable.** `competitor_sales_B`
correlates 0.92 with revenue, and the data cannot distinguish confounder from
mediator from seasonality proxy. Robyn's own documentation says competitor sales
*should* carry a negative coefficient and provides a mechanism to force it; the
bundled data produces **+0.99**, near-unit elasticity — the signature of category
demand, not competition. That contradiction is
[an open issue](https://github.com/facebookexperimental/Robyn/issues/1073) in
Robyn's tracker with no maintainer answer.

**3. Nothing can be validated.** True parameters are unpublished, so an estimated
ROI cannot be scored against anything. Combined with (1) and (2), the project
would have produced a number with no defence.

**Decision simulated dataset:** generate the dataset from a pre-registered DGP with a
known answer key. The measurements above are the justification, and they make the
case better than an assertion would — three candidates audited on identification
criteria, each failure diagnosed to a cause.

**What carries forward** as design requirements for the DGP, from the reads above:
- Seasonality must be controlled before any correlation is believed, and it is
  specified as smooth terms rather than dummies.
- Carryover cannot be read from raw cross-correlation in seasonal data, so decay
  must be *set* and *recovered*, never inferred from a lag plot.
- Media collinearity must be present and non-trivial — Robyn's VIF of 1.03–1.05
  is unrealistically clean.
- The signal level must be set deliberately, not discovered: 8–10% incremental,
  against Robyn's 2.6pp.
