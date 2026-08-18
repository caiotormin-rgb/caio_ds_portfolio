# 03 — Data readiness memo + initial patterns
*Phase 2: Data Understanding. Cap 600w.*

## Completeness — clean
Zero missing values in any column. 208 consecutive Monday-dated weeks, no gaps,
no duplicates. Verified by assertion in `src/01_load.R`, not by eyeball.

## Sufficiency — comfortable
208 observations against a guideline minimum of 80–100 for a stable MMM, and
four years against the customary two-year minimum. With 5 media variables plus
controls, the ~10:1 observations-to-variable ratio holds with room to spare.

## Problem 1 — the control that eats the model
`competitor_sales_B` correlates **0.916 with revenue**. No media channel exceeds
0.44. Revenue swings 3.3× seasonally (June trough ~868K, November peak ~2.87M)
and competitor sales tracks that swing almost exactly — which strongly suggests
it is carrying **shared category seasonality**, not competitive pressure.

This is the central modeling decision, and it is a genuine fork:
- **Include it** and it absorbs nearly all outcome variance. Media effects are
  then estimated off a small residual and will likely be **under-credited** —
  producing a conservative, possibly useless reallocation.
- **Exclude it** and any real competitive effect becomes omitted-variable bias.
- **Decompose it** — model seasonality explicitly (holidays, Fourier terms) and
  use only the residual of competitor sales as the control.

Deferred to Caio. Nothing downstream is safe until it is settled.

## Problem 2 — the data is easier than reality
Pairwise correlation among the five spend channels never exceeds **0.15**.
Real media plans are strongly collinear — channels flight together and budgets
move together — and that collinearity is the main reason real MMMs are unstable.
This dataset has that difficulty removed. The model will therefore behave better
here than it would on a client engagement, and the writeup must say so.

## Pattern — flighted vs. always-on
Four of five channels are dark more than half the time: OOH 59.1% zero weeks,
print 58.2%, TV 55.8%, Facebook 51.4%. Search is the exception at 15.4% —
**effectively always-on**. Two consequences: on/off bursts give good identifying
variation for carryover, but "average weekly spend" is a meaningless summary for
the flighted channels and must not appear in the readout.

## Pattern — an unusual mix
OOH is **61.9% of paid spend**, with Facebook at 3.1%. That is atypical for a
consumer brand, so conclusions about *which* channel wins are specific to this
advertiser and will not generalize. Total paid spend is 3.83% of revenue.
Revenue itself has no trend (−65/week, p = 0.94) — a flat, mature brand.

## What this rules out
- **No answer key.** True parameters are unpublished, so estimated ROIs cannot be
  scored against truth. This is precisely why the recovery check exists.
- **No year-over-year analysis** without adjustment: 2015 contributes only 6 weeks
  (peak season) and 2019 only 45 (missing the November peak). Raw annual means
  are misleading and the naive read — "revenue fell in 2019" — is an artifact.
- **`events` is unusable.** 206 of 208 weeks are `"na"`; `event1` and `event2`
  occur once each. Drop it rather than pretend it controls for anything.
- **Never model both spend and exposure** for Facebook (r = 0.991) or search
  (r = 0.983). Pick one unit per channel.
- **No claim of generality** for the channel ranking, given the OOH-dominated mix.

## Open — Caio's call, Phase 2
1. Treatment of `competitor_sales_B` (the fork above).
2. Spend vs. exposure for Facebook and search — near-interchangeable here.
3. Holiday market: DE per Robyn's demo convention, or none.
