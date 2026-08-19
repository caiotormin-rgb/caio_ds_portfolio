# Industry alignment — what we match, what we're missing, what to cut

A review of this project against how MMM is actually practised, with the
reasoning behind each choice explained in plain terms.

---

## Part 1 — The concepts, explained plainly

These are the ideas the whole project rests on. If a reader understands only
this section, they can follow everything else.

### Adstock: advertising has a memory

A TV campaign that runs in week 1 is still selling in week 3. People saw it,
remembered it, bought later. **Adstock is the decay rate of that memory** — a
θ of 0.7 means 70% of last week's effect carries into this week, 49% into the
next, and so on.

Why it matters: if you ignore it, you credit only the week the money was spent,
and long-memory channels like TV look worse than they are.

### Saturation: the tenth billboard sells less than the first

Put one billboard on a highway and it works. Put ten and the tenth adds almost
nothing — the same drivers have already seen your ad. **Saturation is the point
where more money stops buying proportionally more response.** The "knee" of the
curve is where returns start flattening.

### Marginal vs average ROI: the distinction the whole project turns on

A restaurant's most profitable table is the one by the window. That does **not**
mean adding twenty more window tables earns the same — there is only one window.

- **Average ROI** = what a channel has returned *in total*, historically.
- **Marginal ROI** = what the *next dollar* into it would return.

Budgets are decided at the margin. In our data linear TV has the **highest
average ROI (5.03) and the lowest non-zero marginal ROI (1.20)** — it looks like
the best channel and is the one to cut. An analyst optimising on average ROI
funds exactly the wrong thing. This is the single most common real mistake in
media budgeting.

### Why branded search is the interesting test

When someone types your brand name into Google and clicks your ad — would they
have found you anyway? This is one of the most argued-about questions in the
field, and it has a famous answer: **eBay ran a large-scale experiment
(Blake, Nosko & Tadelis, 2015) and found branded search ads were close to
worthless** — the customers were coming regardless.

We built branded search with a true effect of exactly zero. Whether the model
finds that null is a real test, not a synthetic one.

### Why we pre-registered everything

In clinical trials you declare your hypothesis and success criteria *before*
running the study, so results cannot be reinterpreted after the fact. The
marketing equivalent: **agree the success metric with the client before the
campaign, not after it.**

Every parameter, threshold and abandon criterion in this project was committed
to git before the relevant code existed. The git log is the proof. It costs
nothing and it is the difference between analysis and storytelling.

### Why intervals, not point estimates

We resample the data many times and refit, to see how much the answer moves.
Because weeks are not independent — seasonality links them — we resample
**contiguous 13-week blocks** rather than individual weeks. A single number with
no interval hides how much the data actually knows.

---

## Part 2 — Where we already match industry practice

| Practice | Us | Industry |
|---|---|---|
| Two-stage fitting: transforms optimised outside, coefficients solved inside | ✅ | Exactly how Robyn is built |
| Non-negative media coefficients | ✅ | Standard — a channel can waste money but not destroy revenue |
| Geometric adstock + Hill saturation | ✅ | Default in Robyn, Meridian and PyMC-Marketing |
| Multiplicative (log) outcome | ✅ | Standard for retail, where seasonality scales the business |
| Marginal ROI drives reallocation | ✅ | Correct, and frequently got wrong |
| Constrained optimiser | ✅ | Real plans have contracts and minimums |
| ROI as ranges, never point estimates | ✅ | Explicitly recommended in MMM practice |
| Data readiness treated as the bulk of the work | ✅ | "60% data readiness, 40% modelling" |

---

## Part 3 — Two things industry does that we don't

### 3.1 Don't fit one model — fit thousands and choose from a frontier

**This is our biggest gap.** Robyn does not produce a single model. It generates
thousands across different hyperparameters and presents a **Pareto front** scored
on two axes:

1. **Predictive error** — how well it fits.
2. **Business plausibility** (`DECOMP.RSSD`) — how far each channel's *share of
   modelled effect* sits from its *share of spend*. A model claiming a channel
   with 3% of budget drives 40% of revenue is flagged as implausible even if it
   fits beautifully.

You then choose from the frontier rather than trusting one optimiser run.

**Why this matters for us specifically:** our single fit gives branded search a
marginal ROI of 3.45 against a true 0.00. A plausibility criterion is exactly the
kind of check that would flag it. We have one model and no way to ask "is there
an equally good fit that is more believable?"

**Recommendation: adopt a simplified version.** Fit ~200 models from random
hyperparameter starts, score each on fit *and* decomposition distance, and show
the frontier. It is maybe 40 lines on top of what exists, and it converts a
single point estimate into a defensible selection.

### 3.2 Calibrate with experiments

Both Meridian and Robyn support using geo-lift or holdout test results as priors
on channel effects. It is now considered best practice, because an experiment
measures incrementality directly where a model can only infer it.

**Recommendation: mention, don't build.** We have no experiment to calibrate
against, and inventing one would be circular. But `07-evaluation.md` should say
this is the missing ingredient and what it would fix — that is a stronger
statement than silence.

---

## Part 4 — What to simplify

| Area | Now | Suggested |
|---|---|---|
| Planted defects | 14, across 6 sources | **Keep 6–8.** Each should teach something distinct; several currently overlap (three separate unit problems teach one lesson) |
| EDA notebook | 11 sections | **The readout needs 4–5 charts.** Keep the notebook long for working; the deliverable is short |
| With/without control | Two full fits, dual reporting throughout | **Report one headline number and one sensitivity line.** The span is a footnote, not a parallel narrative |
| Source exports | 6 | Right number. Two spreadsheets and four APIs is realistic |

**What not to simplify:** the pre-registration, the marginal-vs-average
distinction, and the reconciliation. Those are the parts that make this read as
professional work rather than a tutorial.
