# Decisions — MMM project

Caio's judgment calls, logged as they happen. Rejected options matter as much
as chosen ones. CRISP-DM loops get recorded here too.

Format:
## [date] — Phase N — the decision
**Options on the table:**
**Chose:**
**Why:** (Caio's words)
**Rules out:**

---

## 2026-08-17 — Phase 1 — Scope of the project
**Decided:** End-to-end MMM-style project, "strongly related to MMM" but not
required to be textbook commercial MMM.
**Status:** Domain not yet chosen. Phase 1 in progress.

## 2026-08-17 — Phase 1 — Domain must be commercial, not civic
**Options Claude put up:** election spend→votes, public spending→social outcome,
public health campaign→uptake. All three civic.
**Caio's call:** rejected all three. "It has to be relevant to typical MMM use
cases within the job industries I'm targeting. Track B will focus on personal
domains."
**Rules out:** civic/public-sector framing for Track A. Public-data-as-subject is
a Track B move. Track A must resemble the work an advertiser or agency actually
commissions.
**Consequence:** data feasibility becomes the hard constraint, since real
advertiser spend is not public. Solving that is now the Phase 1/2 problem.

## 2026-08-17 — Phase 1 — Use case: classic budget reallocation
**Options on the table:** (a) MMM vs. attribution disagreement, using a simulated
DGP with known truth; (b) classic budget reallocation; (c) MMM + geo-experiment
calibration; (d) methods stress-test, "where does MMM break".
**Chose:** (b) classic budget reallocation.
**Why:** It is the bread-and-butter MMM deliverable and matches what agencies
actually ship, so it reads immediately to the people hiring for these roles.
**Rules out:** For THIS project — attribution comparison, experiment calibration,
and methods stress-testing. All three are strong ideas and go to PARKING-LOT.md,
not into this build.
**Accepted trade-off:** This is the use case every MMM tutorial covers, so
differentiation must come from execution quality — the data-prep and evaluation
artifacts — not from novelty of the question.

**Data constraint established (Phase 1 → feeds Phase 2):**
Meta Ad Library exposes spend only for political/issue ads; commercial ad spend
is not public. So Track A data must be a recognized demo dataset or simulated.
Robyn's `dt_simulated_weekly`: ~205 weeks (2015-12-14 to 2019-11-11), revenue,
TV/OOH/Print/Facebook/Search spend, newsletter (organic), competitor sales and
events as controls. Meridian wants 80-100+ observations minimum.
**Not yet decided:** which dataset. That is a Phase 2 call.

## 2026-08-17 — Phase 1 — Constrained reallocation
**Options:** constrained only / unconstrained then constrained (report both) /
unconstrained only.
**Chose:** constrained — realistic planning limits.
**Why:** The recommendation has to be executable, not just optimal. Media is
bought under real limits — upfront TV commitments, agency contracts, minimum
viable spend to run a channel at all.
**Rules out:** headline-maximizing unconstrained lift numbers. Accepts a smaller
reported revenue gain in exchange for a recommendation that could actually be
carried out.
**Note:** the "report both and treat the gap as the insight" option was
considered and declined. If it's wanted later it's a small add-on, not a rebuild.

**PHASE 1 CLOSED.**

---

# Phase 2 — Data Understanding

## 2026-08-17 — Phase 2 — Dataset: Robyn's dt_simulated_weekly + recovery check
**Options:** (a) Robyn's dataset alone; (b) Robyn's dataset as the deliverable
plus one self-simulated dataset with known parameters to prove the pipeline
recovers them; (c) simulate everything.
**Chose:** (b).
**Why:** Robyn's dataset is recognized in the field and is the right structure
for a reallocation deliverable. The recovery check answers the question a sharp
interviewer always asks — with no ground truth, how do you know the model works.
**Rules out:** basing the actual reallocation recommendation on invented data.
**Scope wall:** the recovery check is ONE simulated dataset and ONE section of
`06-model-card.md`. It is not a second project. If it starts growing, it stops.

## 2026-08-17 — Phase 2 — Data profiled, three open forks
**Done (mechanical):** downloaded both RData files, profiled, exported CSVs,
wrote `01-data-sources.md`, `02-data-dictionary.md`, `03-data-quality.md`.
**Correction to secondary sources:** published write-ups say ~205 weeks from
2015-12-14; direct inspection gives 208 weeks from 2015-11-23. Primary file wins.
**Open forks requiring Caio:** (1) treatment of `competitor_sales_B` (r=0.916
with revenue); (2) spend vs. exposure for Facebook/search; (3) holiday market.

## 2026-08-17 — PACING — Caio: "too fast wait"
Claude ran ahead: downloaded data, wrote 01/02/03, and queued the next judgment
call before Caio had absorbed the previous step. "Work together through each
phase" means one step, then stop and wait — not a sprint with checkpoints.
**Standing rule:** finish one step, report it, stop. Do not pre-fetch the next
decision. Wait to be asked to continue.

## 2026-08-17 — PROCESS — Caio sets the working sequence
"Let's stay on data sources, data quality, dictionary first. Then I'll want to
see the data myself (with your help), we'll discuss what we see, before we move
to the modeling strategy. Otherwise I'm just clicking next next next."

**The sequence, in order — do not skip or merge:**
1. Review 01 / 02 / 03 together. Caio reads, challenges, corrects.
2. Caio looks at the data himself, with Claude's help.
3. **Discuss what we see.** An actual conversation, not a decision prompt.
4. Only then: modeling strategy.

**Standing rule:** a judgment call may not be put to Caio before he has seen the
evidence it rests on. Asking him to decide from Claude's prose summary makes him
a rubber stamp, which defeats the purpose of the portfolio.

**Parked:** baseline charts were built early (`src/02_baseline_charts.R`,
3 PNGs in `outputs/`). They belong to step 2, not now. Two known defects to fix
before showing: colliding direct labels in fig 2 left panel, clipped x-axis
title in fig 2 right panel.

## 2026-08-17 — Phase 2 — CRISP-DM LOOP: Caio rejects R, reopens the data source
"I don't want to use R, maybe Robyn not ideal. Let's think of other sources."
This is Data Understanding looping back on itself — the documented CRISP-DM
cycle, not a mistake. Logged as such.

**Note:** the R dependency was already discharged — both RData files are exported
to `data/cached/*.csv`, so the Robyn *data* is usable from Python without R. The
tooling objection and the dataset objection are separable.

**Candidates evaluated (downloaded and profiled, not read about):**
- `pymc-marketing/data/mmm_example.csv` — 179 wks, but only TWO channels in
  scaled 0-1 units with no currency. **Cannot support a budget reallocation
  deliverable.** Ruled out on fit, not quality.
- Google Meridian ships 7 simulated CSVs. The first one fetched
  (`hypothetical_geo_all_channels.csv`, 38 wks) has **no outcome column** —
  documentation claimed otherwise. Fetched the real ones instead.
- `meridian/national_all_channels.csv` — 156 wks, 5 paid channels
  (spend + impressions), organic, 2 named controls, Promo, conversions.
- `meridian/geo_all_channels.csv` — same fields, 40 geos x 156 wks = 6,240 rows.

**Evidence gathered for the comparison — see next entry once Caio has reviewed.**

## 2026-08-17 — Phase 2 — DECIDED: Python only, no R
**Caio:** "I don't want to use R."
**Rules out:** Robyn as a *modeling tool*, and any R-based workflow.
**Does NOT rule out:** the Robyn dataset — already exported to CSV, usable from
Python. Tooling and data are separate decisions.
**Consequence:** `src/01_load.R` and `src/02_baseline_charts.R` are dead. They
get rewritten in Python once the dataset is fixed. A Python environment
(pandas/numpy) is not yet set up — currently only stdlib is available.

## 2026-08-17 — Phase 2 — CLAUDE MADE A CALL IT SHOULD HAVE ASKED ABOUT
Claude chose which candidate sources to evaluate (PyMC-Marketing, Meridian) and
which diagnostics to run, then presented a comparison already narrowed toward
Meridian geo. Caio was not asked which candidates to consider.
**Handing back:** if there are other sources Caio wants on the table, they go on
the table before the dataset decision is made.

## 2026-08-17 — Phase 2 — OPEN DECISION D1: which dataset
**Status: OPEN. Blocks ingestion, preparation, and everything after.**
Evidence gathered and reviewed by Caio: profiles of all four candidates.
Options: Robyn (208wk national) / Meridian national (156wk) / Meridian geo
(40 geos x 156wk) / other, not yet proposed.
**Not yet decided. Do not proceed past this.**

## 2026-08-17 — Phase 2 — D1 RESOLVED (provisionally): Meridian national
**Caio:** "leaning towards meridian national."
**Status: LEANING, not locked.** Work proceeds on it; revisit before Phase 3 closes.
**Chose:** `meridian/national_all_channels.csv` — 156 weeks, 2021-01-25 to
2024-01-15, 5 paid channels (spend + impressions), 1 organic, controls
`competitor_sales_control` / `sentiment_score_control` / `Promo`, outcome
`conversions` with `revenue_per_conversion`.
**Rules out (for now):** Robyn's 208-week set, Meridian's 40-geo panel,
pymc-marketing's 2-channel example.
**Accepted trade-off:** national data is close to analysis-ready, so the Phase 3
data-prep artifact will be thinner than the geo panel would have produced.
**Next per Caio:** an EDA notebook with visualizations, structure kept simple,
aimed at the critical questions that must be answered before modeling.

## 2026-08-17 — Phase 2 — EDA notebook built
**Caio:** "create a notebook aimed at allowing extensive EDA with visualizations
for critical questions we need to answer. keep structure simple."
**Built:** `notebooks/01_eda.ipynb`, generated by `src/make_eda_notebook.py`
(regenerate rather than hand-editing, so the notebook stays reproducible).
10 sections, flat structure, one question each.
**Design choice — Claude's, flagged for challenge:** the notebook renders
evidence and computes facts but writes **no conclusions**. Every section ends in
an empty "Your read" cell. This is deliberate, per the standing rule that Caio's
judgment must be his own and not a ratification of Claude's.
**Claude chose the 10 questions.** That is a judgment call Caio did not make —
if the list is wrong or incomplete, it changes before any analysis is done.
**Environment:** `.venv` (Python 3.14, pandas 3.0, matplotlib 3.11). R scripts
`src/01_load.R` and `src/02_baseline_charts.R` are now dead and should be deleted
once the dataset is locked.

## 2026-08-17 — Housekeeping — dead code and stale docs cleared
**Deleted (irreversible — repo is not under version control):** `src/01_load.R`,
`src/02_baseline_charts.R`, 3 R-generated PNGs in `outputs/`, both Robyn `.RData`
files, both Robyn cached CSVs, and `pymc_mmm_example.csv`.
**Archived rather than deleted, to `_archive/`:** the three Robyn-era artifacts
(`01-data-sources`, `02-data-dictionary`, `03-data-quality`) and Claude's three
unendorsed civic project drafts. Judgment calls, so not Claude's to destroy.
Added `.gitignore`.

## 2026-08-17 — Phase 2 — FINDING: national is the geo panel aggregated
Verified numerically, not assumed: summing `geo_all_channels.csv` over its 40
geos reproduces `national_all_channels.csv` to floating-point precision
(max relative difference 1.8e-16 on conversions, 5.1e-16 on Channel3 spend).
**Why it matters:** the geo panel is not an alternative dataset, it is the same
simulation at a finer grain. National can carry the deliverable now, and geo can
be added later as a hierarchical robustness check **without changing datasets,
story, or any prior decision.** De-risks D1 considerably.

## 2026-08-17 — Phase 2 — All 7 Meridian simulated files catalogued
| file | rows | weeks | geos | paid ch | organic | Promo | extras |
|---|---|---|---|---|---|---|---|
| national_media | 156 | 156 | - | 4 | no | no | - |
| national_media_rf | 156 | 156 | - | 4 | no | no | Channel3 reach + frequency |
| **national_all_channels** | 156 | 156 | - | **5** | yes | yes | current choice |
| geo_media | 3,120 | 156 | 20 | 4 | no | no | population |
| geo_media_rf | 3,120 | 156 | 20 | 4 | no | no | population, Ch3 reach + freq |
| geo_all_channels | 6,240 | 156 | 40 | 5 | yes | yes | population |
| hypothetical_geo_all_channels | 1,520 | 38 | 40 | 5 | yes | yes | **no outcome column — unusable** |
Note: `_media` files name the control `competitor_activity_score_control`;
`_all_channels` files use `competitor_sales_control`. Different variables.

## 2026-08-17 — Phase 1/2 — DECIDED (D2): national first, geo as a bounded second step
**Options:** geo-first (Meridian's intended design) / national-first with geo
added later / national only.
**Chose:** national first, then geo as a defined robustness step.
**Claude recommended this**; Caio agreed. Reasoning on the record:
- National IS the geo panel aggregated (verified, 1.8e-16), so nothing done now
  is discarded — EDA, prep, artifacts and story all transfer intact.
- Completing one full CRISP-DM chain before adding sophistication matters more
  than a better model that never ships.
- It produces an evaluation/robustness section, which most portfolios lack.
**Accepted risk, stated in advance:** 156 weekly observations is thin for ~15+
media parameters plus controls and seasonality. Meridian is designed geo-first
because 40 geos x 156 weeks gives far more identifying variation and lets
partial pooling stabilise estimates. The national model may come out unstable.
**Scope wall written into `00-brief.md`.** Without it this becomes the tail that
turns a finished project into an unfinished one.

## 2026-08-17 — Prior art survey: who else has built on this dataset
**Third-party work is essentially nonexistent.** GitHub search for Meridian MMM
returns 353 repos but nearly all are keyword noise. The only dedicated
third-party demos are `daeexe/Meridian` (1 star) and
`bhauryal-eliya/Meridian-Demo` (0 stars). No one has published a serious
end-to-end Meridian project with a full artifact chain.
**Implication:** differentiation is available — but NOT in the modeling.

**Google's own 7 demo notebooks are the real prior art**, and two of them cover
this exact deliverable:
- `ROI_mROI_Response_Curves.ipynb` — ROI, marginal ROI, saturation curves
- `Meridian_Scenario_Planner_Beta.ipynb` — budget scenario planning
Plus `Meridian_Getting_Started`, `_Jax`, `_RF_Demo`, `RF_Data_Simulation`, `_MLflow`.

**Consequence for this project:** the model-and-optimise path is well paved by
Google. The portfolio value therefore sits almost entirely in what surrounds it —
the data artifacts, the pre-registered analysis plan, the evaluation memo, the
activation one-pager, and this decision log. Running the demo notebook is not
the project. Reconfirms the trade-off accepted when the use case was chosen.

## 2026-08-17 — Phase 2 — D1 LOCKED: Meridian national
Writing `01-data-sources.md` commits the choice. Previously "leaning"; now locked.
`meridian_national_all_channels.csv` is the primary source;
`meridian_geo_all_channels.csv` is retained **only** for the D2 Phase 5
robustness step. Reversible, but reversing it now means rewriting `01`.

## 2026-08-17 — Phase 2 — Ingestion formalised
`src/01_load.py` replaces the dead R loader. Exposes `national()` / `geo()` and
asserts on every run: row counts, weekly regularity, panel balance, no missing
values, expected columns, non-negative spend, positive outcome, and the
**national == geo-aggregated identity**. That last assertion turns a one-off
finding into a permanent regression test — if the two files ever stop being the
same simulation, the notebook fails loudly instead of quietly modelling the wrong
thing.
`data/candidates/` renamed to `data/raw/` now that the shortlist is closed.
The EDA notebook calls `mmm.validate()` before any analysis runs.

## 2026-08-18 — Phase 2 — 02-data-dictionary written, two corrections to earlier claims
Field stats computed from the data, not carried over from memory. Two things
Claude had stated earlier were wrong and are corrected in the document:

1. **`revenue_per_conversion` is not constant.** It has 156 distinct values.
   The practical conclusion still holds — CV is 0.076%, full range spans 0.45%
   of the mean, and `revenue` correlates 0.99994 with `conversions` — but the
   file does vary and the document says so.
2. **Zero-week shares quoted earlier came from the wrong file.** Those figures
   (Channel0 11.1%, Channel1 29.0%, Channel2 58.4% ...) were from
   `hypothetical_geo_all_channels.csv`. In the actual national file **only
   Channel2 has dark weeks, at 2.6%** — every other channel is always-on.

**New finding: CPM is fixed per channel** (7.3327 / 9.6412 / 7.4309 / 7.7928 /
7.7919), constant to floating-point noise. Spend and impressions are therefore
an exact linear rescale of one another, not merely highly correlated. The
spend-vs-exposure modelling choice carries no information either way — it is a
units decision, not a modelling one.

**Also noted:** `Promo` is never zero — a continuous always-on intensity, not an
on/off flag as previously described.

## 2026-08-18 — Phase 2 — Platform spec research (subagent), and what it rules out
Full condensed spec in `reference/platform-data-specs.md`. Findings that change
what is worth simulating:

**Reach is not additive.** It is set cardinality, so weekly reach is a union,
not a sum — naive summation overcounts by 30-70%. Both Google and Meta state
their reach metrics cannot be aggregated. A real weekly reach series is
assembled by ~156 separate API calls per platform, not a `groupby`.
**Consequence for MMM:** impressions/spend stay the additive media driver;
reach and frequency can only be diagnostics or covariates. Any simulated reach
series built by summing days would have an impossible reach-to-impression ratio
and would be caught immediately.

**Three things cannot be simulated as native fields at all:**
- **Branded vs non-branded** — no API field, no enum, anywhere. Analysts regex
  the keyword text. Only admissible as an explicitly derived analyst column.
- **Search volume** — not in performance reporting. Separate service, monthly,
  bucketed (10/50/100/500/1K/5K/10K), not joinable to weekly performance.
- **YouTube organic impressions / thumbnail CTR** — do not exist in the YouTube
  Analytics API, only in the Studio UI. Paid video reach comes from the Google
  Ads API. Conflating the two APIs is the classic synthetic-data tell.

**Google Search Console is effectively ruled out for this project:** 16-month
retention means a 156-week series is unobtainable via the standard API.
Simulating one implies a BigQuery bulk export or three years of monthly manual
pulls, which is a lot of implied backstory for little modelling gain.

**Realism details worth respecting if we simulate:** impression share is clipped
to [0.1, 1.0] with anything below reported as exactly 0.0999 (lost-IS clipped at
0.9001); Google Ads `conversions` is a fractional DOUBLE, so integer conversions
are a tell; Meta `ctr` is percent 0-100 while Google and GSC are ratios 0-1;
Meta serialises all numerics as JSON strings; Trends is an integer index 0-100
in which exactly one period equals 100, and a 3-year window natively returns
weekly data.

**Still open:** whether to add simulated sources at all, and the channel naming
proposal. Neither decided.

## 2026-08-18 — Phase 2 — D3: channel names assigned as a disclosed convention
**Context:** source channels are `Channel0`-`Channel4` with no media type. Caio
asked for them to be named and documented; Claude proposed a mapping from
behavioural signatures and Caio approved the direction.
**Evidence is weak.** Four of five CPMs sit between 7.33 and 7.79, no channel
shows TV-like flighting or search-like smoothness. Google's simulation simply
did not encode media-type character.
**Assigned:** Channel3 -> TV/CTV (moderate), Channel1 -> YouTube/premium video
(moderate, only distinctive CPM at 9.64), Channel2 -> Out-of-home (moderate;
burstiest, only channel with dark weeks, 17.1% of annual spend in October),
Channel0 -> Programmatic display (weak), **Channel4 -> Paid social (no evidence
whatsoever — an assignment, not an inference)**.
**Rules recorded in `02-data-dictionary.md`:** disclose the convention wherever a
name appears; no claim may rest on a name; modelling code uses raw identifiers
and names are a presentation layer applied only at readout.
**Rules out:** treating any media-type conclusion as a finding of the analysis.

## 2026-08-18 — Phase 2 — D4: which simulated sources to add
Direction approved by Caio. Build order by value-to-invention-cost:
1. **Holiday calendar** — real public data, zero invention. The only addition
   that raises credibility rather than spending it.
2. **Trends-style branded interest index** — integer 0-100, exactly one period
   equal to 100, zeros meaningful, generated at weekly grain (which a 3-year
   Trends window returns natively). A legitimate brand-demand control.
3. **Branded / non-branded paid search** — highest modelling value. Must be
   presented as an **analyst-derived** column, never an API field. Underlying
   rows must respect IS clipping ([0.1,1.0], sub-0.1 as exactly 0.0999) and
   fractional DOUBLE conversions.
4. **Reach & frequency on one video channel** — **demoted to diagnostic only**,
   not a model driver, per the non-additivity finding. Generated directly at
   weekly grain; `reach <= impressions` and `frequency = impressions/reach`.

**RULED OUT: Google Search Console.** 16-month retention makes a 156-week series
unobtainable via the standard API. Simulating one implies a BigQuery bulk export
or three years of manual monthly pulls — a lot of implied backstory for little
modelling gain.

**Boundary that must hold:** every column is tagged as Google's simulation or
ours. `01-data-sources.md` and `06-model-card.md` both carry the split. Adding
invented data to an already-simulated dataset costs credibility; the mitigation
is that the boundary is never blurred.
**Nothing generated yet.** Build order above is proposed, not executed.

## 2026-08-18 — Phase 2 — D5: EDA on Google's data BEFORE any augmentation
**Agreed:** do not generate simulated columns yet. Caio works through
`notebooks/01_eda.ipynb` on the unmodified Meridian data first, so
`03-data-quality.md` documents the real dataset rather than one we partly built.
**Rules out:** describing, in a data-quality memo, a dataset that was never
looked at in its original form.
**Consequence:** D4's build order (holidays -> Trends index -> branded search ->
R&F diagnostic) is queued behind the EDA, not cancelled. The branded/non-branded
question stays open and gets decided after the reads, since the Trends index and
the branded search split only make sense as a pair.

## 2026-08-18 — Phase 2 — D6: augmentation built (items 1, 2, 4). Item 3 NOT built.
Caio overrode D5 and asked for the data now. Built `src/02_simulate_sources.py`
-> `data/simulated/augmented_weekly.csv`, 156 x 15, joining 1:1 on `time`.
`data/raw/` is never written to; every column carries a provenance tag.

**Built:**
- 9 **real** holiday columns (US federal calendar, `holidays` 0.103).
- `brand_interest_index` — **simulated, and deliberately a MEDIATOR.** Built from
  contemporaneous + adstocked upper-funnel media, so r = +0.64 with Channel3 and
  +0.79 with Channel1. Controlling for it would delete media effect. Documented
  as such in `01` and `02` so it can never be used as an innocent control.
- Reach/frequency for Channel1 and Channel4 — **simulated diagnostics only**,
  generated at weekly grain. Frequencies 1.62-2.10 and 1.52-2.52, inside the
  1.2-4.0 band for national buys.

**Three defects found and fixed before shipping:**
1. `holiday_july4` fired 8 times in 3 years — substring matching caught
   "Juneteenth National **Independence Day**". Now exact-name matching after
   stripping "(observed)". Juneteenth got its own flag.
2. `holiday_blackfriday` was an exact duplicate of `holiday_thanksgiving`
   (Black Friday always falls in that week). Dropped — perfectly collinear.
3. `brand_interest_index` correlated **negatively** with the media that built it,
   because pure adstock on an always-on series is dominated by its slow-moving
   level. Rebuilt as 65% contemporaneous / 35% adstocked; now +0.64 / +0.79.

**ITEM 3 (branded / non-branded paid search) DELIBERATELY NOT BUILT.**
It is not a preference — it is a defect. Google generated `conversions` without
any search channel, so a simulated search channel would have **exactly zero true
effect** on the outcome. The MMM would correctly estimate its ROI as noise, and
a reallocation recommendation touching it would be meaningless. The only ways
round it both have costs, and the choice is Caio's:
  (a) Inject a real search effect into a **new** `conversions_augmented` column,
      leaving Google's `conversions` untouched. Coherent, but the modelled
      outcome then becomes partly ours and the deliverable changes meaning.
  (b) Drop item 3. The `brand_interest_index` still stands on its own as a
      mediator demonstration, though it loses its intended pair.
**Not decided. Nothing built either way.**

## 2026-08-18 — Phase 2 — D7: option (b). Simulated search channel dropped.
**Caio:** "it has to be b. i intend to bring better data later on but gotta start
with this."
**Chose:** (b) — do not build a branded/non-branded paid search channel, and do
not create a `conversions_augmented` column.
**Why:** the project's credibility rests on Google owning the outcome. Option (a)
would have spent exactly that.
**Rules out:** any simulated media channel with its own spend, for as long as
`conversions` comes from Google's simulation. The constraint is structural, not
stylistic — a channel that did not exist when the outcome was generated cannot
have a recoverable effect.
**Consequence:** `brand_interest_index` stands alone as a mediator demonstration
rather than as half of a brand/search pair. That is still a genuine and
uncommon thing to show.

**Standing context — this dataset is a starting point, not the destination.**
Caio intends to bring better data later. Architectural implication, worth
protecting: `src/01_load.py` is the single swap point. Everything downstream —
the EDA notebook, and every artifact from `04` on — reads through it rather than
touching CSVs directly. Keep it that way, so replacing the source is a change to
one file rather than a rewrite. When real data arrives, the simulated
augmentation columns should be re-examined for whether they are still needed at
all.

## 2026-08-18 — Tooling — generator made non-destructive
`src/make_eda_notebook.py` previously overwrote the notebook wholesale. Once
Caio starts filling "Your read" cells, that would silently destroy his work —
the single most valuable content in the file.
**Fixed:** the generator now reads the existing notebook first and carries any
filled "Your read" text forward, in order, before writing. Verified with a
sentinel: written, regenerated, survived. It also warns when dropping cells
added outside the generator.
**Also noted:** an empty code cell added from the IDE was swept into commit
6a6370f by a blanket `git add -A`. Harmless, but the commit message did not
mention it. Prefer scoped `git add` when the working tree has Caio's edits in it.

## 2026-08-18 — EDA notebook — channel labels on plots, and Claude's first-pass notes
**Labels:** plot titles and axes now carry the assigned names (`Channel3 · TV / CTV`
on panels, `C3 TV` where space is tight). A disclosure cell sits directly above
section 1 restating that names are a convention with weak-to-moderate evidence
and none for Channel4. Per D3, raw identifiers remain canonical in all code.

**First-pass notes — a deliberate reversal, at Caio's request.** Each section now
carries a "Claude's first pass" block above the still-empty "Your read" cell.
Every figure in those notes was computed from the data, not recalled. They are
labelled *anchors to argue with, not answers*, and Caio's cell stays his.
**Risk accepted and recorded:** an anchor biases the reader. Caio asked for it
after working with blank cells, and a first pass he disagrees with is more
useful to him than a blank page. If his reads start merely echoing the notes,
this was the wrong call and should be reverted.

**What the first pass actually says — the four that matter:**
1. Only C2 ever goes dark, 2.6% of weeks. Everything else is always-on, so
   **adstock will be weakly identified almost everywhere.**
2. **The largest channel has the least variation** (C3 TV: 40% of spend, CV 0.31,
   p90/p10 2.26) while the smallest has the most (C2: CV 0.87, p90/p10 20.3).
   The budget decision that matters most rests on the weakest evidence.
3. **Media is more entangled with the control than with other media** —
   C4↔competitor_sales 0.75 and C3↔competitor_sales 0.70, versus a worst
   channel-pair of 0.70.
4. **Nothing is visible in raw form.** No carryover (all |r| ≤ 0.18, peak lags
   scattered with no decay shape), no saturation bend, and three of five channels
   slope *downward* across spend quintiles. The entire result will come from the
   model specification rather than from anything observable — which raises the
   stakes on `05-analysis-plan.md` being written before any model is fit.

## 2026-08-18 — Phase 2 — OPEN QUESTION: what is `competitor_sales_control`?
Caio asked where it comes from in Google's documentation. Checked
`collect-data`, `basics/model-spec` and `advanced-modeling/control-variables`.

**Finding: it is undocumented.** Google's docs never mention competitor *sales*.
They give **competitor impressions**, temperature, and Google Query Volume as
control examples. The simulated datasets ship with **no README, no data
dictionary** — the repo path holds only `csv/`, `pkl/` and `xlsx/` directories.
So the column's real-world referent and units are unknown; the name is
suggestive, not definitional.

**Units problem:** observed values are mean ≈ 0, range −1.95 to +2.13, i.e.
pre-standardised. But Meridian does **not** population-scale controls by default
(`control_population_scaling_id` is opt-in, and the docs say competitor
impressions *should* be scaled). So this column arrived standardised from the
generator. "Competitor sales" that is z-scored is an index, not sales, and
nothing anchors it to a real quantity.

**The bigger issue — Meridian's own mediator warning applies here.** From
`advanced-modeling/control-variables`: *"Mediator variables shouldn't be included
as control variables, because including them will bias causal inference estimates
on the treatment variables."* Google's worked example is query volume — a
mediator for non-search channels, a confounder for search ads.
We measured `competitor_sales_control` correlating **0.75 with Channel4 spend and
0.70 with Channel3 spend.** If our media affects competitor sales (share
capture), it is a mediator and controlling for it destroys part of the media
effect. If it drives both our media planning and our KPI, it is a confounder and
omitting it biases the other way. **The data cannot distinguish these, and the
choice is a modelling assumption that must be stated in `05-analysis-plan.md`.**

**Also noted:** controls enter Meridian linearly with geo-specific coefficients
(`γ^[C]_{g,i} z_{g,t,i}`, `γ ~ Normal`) — no adstock, no saturation.

**Unresolved.** Belongs in `03-data-quality.md` (Caio's) and forces a decision in `05`.

## 2026-08-18 — Phase 2 — Caio: the Meridian sample cannot yield productive analysis
Tested rather than debated. Two findings.

**1. Robyn's dataset is strictly better on every identification-relevant axis.**

| | Meridian national | Robyn dt_simulated_weekly |
|---|---|---|
| weeks | 156 | **208** |
| seasonality peak/trough | 1.07x | **3.31x** |
| channels >20% dark weeks | **0/5** | **4/5** |
| CV per channel | 0.31-0.87 | **0.79-1.94** |
| max abs corr(spend, outcome) | 0.18 | **0.44** |
| quintile Q5 > Q1 | **2/5** | **5/5** |
| implied CPM variation | ~1e-8 (constant) | **0.252** |

Robyn's known weakness — `competitor_sales_B` correlating 0.916 with revenue —
is a *modelling challenge*, and an interesting one. Meridian's problem is an
*identification failure*, which no modelling choice can fix.

**2. The geo panel does NOT rescue it.** Meridian is designed geo-first, so this
was worth testing before abandoning the dataset. It fails for a specific reason:
- within-geo correlations 0.02-0.13, no better than national
- between-geo 0.02-0.22
- **spend per capita barely varies across geos (CV 0.04-0.13)**
- **channel mix is nearly identical in every geo** — Channel3's share ranges only
  0.380-0.414 across all 40 markets, sd 0.009
Geo-level MMM works because different markets receive different mixes. Here every
geo gets the same plan scaled by population, so there is no cross-sectional
variation to exploit. D2's Phase 5 robustness step is therefore also dead.

**CLAUDE ERROR TO OWN:** dropping Robyn at D1 conflated tooling with data. Caio
ruled out R; the data is a flat table readable in Python via `pyreadr`, with no
R anywhere. The distinction was flagged at the time and then not acted on.

**Not wasted:** the diagnostics above are a **data readiness assessment** — a
real pre-engagement artifact, and per industry practice a good MMM project is
~60% data readiness. Two candidate datasets audited on identification criteria,
with a documented go/no-go, is legitimate `01`/`03` content whichever way we go.

**Open — Caio's call.** Options presented: (A) switch to Robyn in Python,
(B) keep Meridian and reframe the deliverable as a readiness assessment,
(C) build our own simulator with known ground truth and a longer period.

## 2026-08-18 — Phase 2 — D8: SWITCHED to Robyn `dt_simulated_weekly` (option A)
Caio chose A after the readiness audit. Reverses D1.

**Done:**
- Robyn's `dt_simulated_weekly` and `dt_prophet_holidays` re-fetched and converted
  to CSV **in Python via `pyreadr`**; the `.RData` artefacts were deleted after
  conversion. **No R anywhere.** The original D1 rationale ("no R") conflated
  tooling with data and was wrong.
- `src/01_load.py` rewritten: `weekly()`, `holidays(country)`, and `validate()`.
  Beyond the usual integrity checks it now asserts **the two properties that
  justified the switch** — at least 4 of 5 channels dark >20% of weeks, and month
  peak/trough seasonality above 3.0x. If either stops holding, the identification
  argument in `01`/`03` is void and the loader fails loudly.
- EDA notebook fully regenerated on the new data: 53 cells, 9 figures, 10 reads,
  no errors. Channel names are now **real** (TV, out-of-home, print, Facebook,
  paid search), so **D3's invented naming convention is obsolete** — dropped.
- Meridian files moved to `data/audit/`. They are evidence for the readiness
  assessment, not modelling inputs.

**Marked STALE, rewrite required:** `01-data-sources.md`, `02-data-dictionary.md`
(both describe Meridian as primary), and `src/02_simulate_sources.py` (references
`Channel0-4` and `conversions`, which no longer exist).

**Also dead:** D2's geo robustness step — Robyn is national only. And D6's
augmentation columns, until rebuilt against the new schema.

**What the new data looks like:** 208 weeks 2015-11 to 2019-11; TV / OOH / print /
Facebook / paid search; revenue outcome; `newsletter` organic;
`competitor_sales_B` control; `events` unusable (206/208 "na"). Seasonality
3.31x, no trend (p=0.94), 4/5 channels flighted 51-59% dark, all five channels
sloping upward across spend quintiles, and unit cost genuinely varying
(Facebook CV 0.252, search CV 0.124). Its problem is `competitor_sales_B` at
r=0.92 with revenue — a modelling problem, which is the kind worth having.

## 2026-08-18 — Phase 2 — 01 and 02 rebuilt for Robyn
Both rewritten from computed field statistics, not carried over. Stale markers
removed. `01` is 327 prose words, `02` is 127 — both inside cap.

**`01` now carries the data readiness assessment as a first-class section**, with
the Meridian rejection documented as a comparison table plus the geo test that
also failed. That turns a dead end into the most defensible part of Phase 2:
most portfolios never show a dataset they rejected, let alone the criteria.

**Facts recorded that shape later phases:**
- Robyn licence confirmed **MIT** (repo last pushed 2026-01-26).
- `dt_prophet_holidays` covers **1995-2044, 123 countries**. Market is undecided:
  DE gives 37 holiday dates in-window, US gives 44. Deferred to `05`.
- **TV, out-of-home and print are spend-only** — no exposure column exists. So a
  spend-vs-exposure modelling choice can apply to at most 2 of 5 channels, or
  must be dropped for consistency. This is a constraint, not a preference.
- **`ooh_S` is 61.9% of spend but has the weakest outcome correlation of any
  channel (+0.095).** `search_S` is 8.5% of spend and the strongest (+0.443).
- Partial years at both ends (2015: 6 weeks, 2019: 45) make raw YoY invalid.

**Still open:** `05` must decide the holiday market, the treatment of
`competitor_sales_B`, and whether `newsletter` enters the model.

## 2026-08-18 — EDA notebook — first-pass notes sharpened with post-rebuild facts
The notes were already Robyn-current (regenerated at D8). Four additions, each a
fact established while rebuilding `01`/`02` that the notes did not yet carry:
- **s2:** a holiday calendar exists (123 countries) but the **market is
  undecided** — DE 37 dates in-window, US 44. Deferred to `05`.
- **s3:** the project's central tension stated up front — **out-of-home takes
  61.9% of budget with the weakest outcome correlation (+0.095); paid search
  takes 8.5% with the strongest (+0.443).**
- **s6:** full correlation ranking (search +0.443, TV +0.420, Facebook +0.318,
  print +0.230, OOH +0.095) — **almost exactly inverse to budget share.**
- **s10:** the constraint, not just the observation — TV, OOH and print have no
  exposure column, so an exposure-based specification covers at most 2 of 5
  channels or must be abandoned for consistency. Decide in `05`, not mid-model.

## 2026-08-18 — Phase 2 — Market resolved: Germany (inferred, not stated)
Caio asked whether Robyn's docs name a region. **They do not.** The dataset's
roxygen block says only "Simulated MMM data".

**But three converging signals in Robyn's source point to DE:**
1. `R/R/data.R:29` — commented provenance: `read.csv('data/de_simulated_data.csv')`
2. `R/R/inputs.R:136` — documented example uses `prophet_country = "DE"`
3. `demo/demo.R:67` and `:298` — the official demo sets `prophet_country = "DE"`

Strong enough to adopt DE as the working assumption (37 holiday dates in-window,
10 distinct; US would give 44/13). **Recorded as inferred, never as stated** —
`05-analysis-plan.md` confirms it, and the writeup must not present it as a
documented fact.

**Documentation defect found:** `data.R` describes `revenue` as *"Daily total
revenue"* while the dataset is weekly. Trust the data over the docs — same
lesson as the 208-vs-205-weeks discrepancy found earlier.

## 2026-08-18 — Phase 2 — D9: DE holiday calendar adopted
**Caio:** "lets adopt DE holidays."
**Chose:** `dt_prophet_holidays` filtered to `country == "DE"`.
**Why:** three converging signals in Robyn's source (commented provenance path
`data/de_simulated_data.csv`; `prophet_country = "DE"` in both the documented
example and the official demo). Never formally stated — **the writeup must say
inferred, not documented.**
**Rules out:** US and the other 121 country calendars. If the DE assumption is
ever challenged, US is the fallback (44 dates in-window vs 37) and the swap is a
one-argument change to `holidays()`.

**Coverage validated on the weekly grid (Phase 2 work, not Phase 3):**
- 37 holiday dates in-window, **10 distinct** holidays.
- 9 of the 10 recur in all four years (Christmas Day, Second Day of Christmas,
  New Year's Day, Good Friday, Easter Monday, Labor Day, Ascension Day, Whit
  Monday, German Unity Day). **Reformation Day appears once** — 2017, the
  Reformation's 500th anniversary, a one-off national holiday in Germany. At
  n=1 it is unusable as a control, exactly like `events`.
- **33 of 208 weeks (15.9%) contain at least one holiday**; 4 weeks contain two.
- Naive mean revenue is 1.92m in holiday weeks vs 1.80m otherwise — a +6.7%
  gap, but uncontrolled and confounded with December seasonality. Not a finding.

**Deferred to Phase 3:** turning this into weekly features. `01_load.py` stays
ingestion and validation only — the holiday-to-week mapping is a transformation
and belongs in `04-data-prep.md`, not in the loader.

## 2026-08-18 — Phase 2 — FINDING: seasonality was never controlled, and it reverses the ranking
Added as notebook subsection **2b** with a plain-language rationale.

**The problem:** revenue swings 3.31x across the year and so does spend, so every
raw correlation partly measures "November is busy" rather than "this channel
works". Nothing before 2b controlled for it.

**The fix:** subtract each variable's seasonal average from **both** sides, then
correlate the remainder — i.e. compare weeks only against other weeks in the same
part of the year. Equivalent to a regression with time fixed effects (FWL).

**Four treatments checked, because a result that holds under only one is an
artefact of that choice:**

| method | TV | OOH | Print | Facebook | Search | params |
|---|---:|---:|---:|---:|---:|---:|
| raw | 0.420 | 0.095 | 0.230 | 0.318 | **0.443** | 0 |
| month means | **0.290** | 0.012 | 0.125 | 0.061 | 0.144 | 12 |
| week-of-year | **0.292** | -0.070 | 0.185 | 0.007 | 0.138 | 53 |
| month x year | **0.311** | -0.028 | 0.122 | 0.074 | 0.161 | 49 |
| Fourier, 3 harmonics | **0.311** | -0.013 | 0.139 | 0.113 | 0.090 | 7 |

**TV is strongest under all four. OOH is at or below zero under all four.
Search's raw lead was the calendar. Facebook nearly vanishes.** The Fourier row
carries most weight — 7 parameters against 49, and smooth seasonality is closer
to how a calendar behaves than a step function.

**Stated limitation:** this over-corrects. Media bought deliberately into peak
season has its real effect stripped out too, so these are **floors, not point
estimates**.

**Caio's read (interview, captured to notebook 2b):** *"It seemed obvious we
already had seasonality controls — dummies at least — but we didn't... Facebook
was indeed distorted by seasonality. Out-of-home is still weak, saving missing
context or an overlooked KPI."*

**Pre-commitment for `05-analysis-plan.md`:** seasonality is controlled with
**smooth terms (Fourier / prophet), not month dummies**, on the degrees-of-freedom
argument above. Recorded before any model is fit.

## 2026-08-18 — Tooling — BUG FOUND AND FIXED: read-cell preservation was position-keyed
Inserting subsection 2b shifted every "Your read" cell by one, and the generator
silently reassigned all three of Caio's captured answers to the **wrong sections**
— the budget-split read landed on 2b, the controls read on 6, the OOH read on 8.
Caught by inspection, not by any test.
**Fixed:** preservation is now keyed by **section heading**, never by position,
and it warns loudly if a filled read has no matching section in the new build.
Misplaced reads repaired.
**Lesson worth keeping:** the mechanism protecting his work was itself the thing
that corrupted it. Any "safe" preservation scheme needs a stable key.

## 2026-08-18 — Phase 2 — CLAUDE ERROR, corrected by Caio: search adstock IS identifiable
Claude claimed paid search's adstock was "unidentifiable" because it is never
dark for more than 2 weeks. **Wrong, and it would have driven a bad
specification.** Caio: *"can't we rely on level of spend alone? it may never go
dark but spend oscillates."*

**Test run:** correlation between `adstock(spend, theta)` series across
theta in {0, 0.2, 0.4, 0.6, 0.8}. If all pairs sit near 0.99 the decay parameter
is unidentified. Minimum pair correlation by channel — print 0.593, TV 0.604,
OOH 0.608, Facebook 0.611, **paid search 0.801**. All identifiable; search
weakest but well clear of degenerate.

**The right diagnostic is jumpiness, not darkness.** Search moves a median 12.7%
week-over-week with 39 weeks of >30% swings. What weakens it is smoothness:
search has AC(1) = +0.712 while the other four have *negative* AC(1)
(-0.065 to -0.246) — burst-stop-burst makes adstock transforms maximally
distinguishable.

**Consequence:** search stays in the carryover specification. Expect wider
intervals on its decay parameter, and say so rather than reporting a point
estimate. (Threshold of 0.9 is a Claude rule of thumb, not a standard.)

**Caio's read on carryover, captured to notebook s8:** the raw chart is
contaminated, the deseasonalised version is noise, and *"the data does not decide
this — the specification will"*. That must be stated explicitly in `05`.

## 2026-08-18 — Phase 2 — D10: every headline number ships as a RANGE, not a point
**Caio:** "bounds."
**Context:** the demand-proxy question (`newsletter`, `competitor_sales_B` —
control or mediator?) cannot be settled by this data. Caio's instinct was to keep
the signals and caveat later; the problem is that including demand proxies does
not add uncertainty, it **systematically deflates** media effects in a known
direction, and a footnote does not tell a decision-maker by how much.
**Chosen instead:** fit both ways and report the span.
**Rules out:** any single point estimate as a headline number.

**This is the third place the same answer has surfaced** — raw vs deseasonalised,
four seasonality treatments, and now controls in vs out. That is not coincidence:
this dataset cannot identify things sharply. So it becomes a structural
commitment rather than three separate patches.

**Pre-commitment for `05-analysis-plan.md`:** every headline number is reported
as a range across the specification choices we could not resolve — seasonality
treatment, demand proxies in/out, and carryover length. Coincidentally this is
also what industry practice demands of MMM deliverables: ROI as ranges, never
point estimates.

## 2026-08-18 — Phase 2 — D11: spend, not exposure, for all five channels
**Caio:** "agreed."
**Chose:** model on spend across all five channels.
**Why, on evidence rather than convenience:** deseasonalised, spend and exposure
give identical correlations with revenue (Facebook +0.113 vs +0.110; search
+0.093 vs +0.095); unit cost shows no trend across four years (r = -0.013 and
-0.081), so there is no auction-pressure story exposure would capture; and TV,
out-of-home and print have no exposure column at all, so exposure would force a
mixed specification covering 2 of 5 channels.
**Rules out:** exposure-based and mixed specifications. `facebook_I` and
`search_clicks_P` are retained for diagnostics only, never as model inputs.

## 2026-08-18 — EDA notebook — first-pass notes consolidated
Swept and rewritten at Caio's request: brief on the unremarkable, explicit tags
on what carries into later phases. 767 words across 11 sections, 9 tagged
**[MODELING]** or **[FEATURE ENG]**.

**The findings tagged as consequential:**
- **[FEATURE ENG]** drop `events`; DE holidays usable for 33 of 208 weeks, minus
  Reformation Day at n=1.
- **[MODELING]** seasonality explains 80.7% and media adds 2.6 points on top —
  the entire signal budget. Two Fourier harmonics suffice.
- **[MODELING]** `newsletter` is a demand proxy (symmetric lead/lag peaking at
  zero), so it belongs in the D10 bounds alongside `competitor_sales_B`.
- **[MODELING]** decay is identifiable for all five channels, but the data will
  not corroborate any particular value — the estimate must not be presented as
  an empirical finding.
- **[MODELING]** no saturation bend is visible anywhere, so the Hill curve comes
  from the functional form. This limits how far the response curves can be
  claimed as evidence.
- Media-to-media collinearity is a non-issue (VIF 1.03-1.05) — worth stating
  because it removes the usual reason MMMs come out unstable.

## 2026-08-18 — D12: STAY on Robyn. Scope held.
**Caio:** "i fear this will add too much complexity than initially scoped" ->
"stay as is."
**Chose:** finish the chain on `dt_simulated_weekly`. No third dataset, no AMSS,
no difficulty ladder.

**Why, beyond the head-to-head:**
- **Caio's nine interview reads are keyed to Robyn's channels.** They are the
  portfolio content that shows his judgment. A 13-channel retailer invalidates
  all of them and the interview restarts. That cost does not appear in any
  comparison table and it is the largest one.
- Robyn's weak signal (2.6pp incremental) is **reportable, not disqualifying** —
  D10 already commits to ranges, and "media explains little once seasonality is
  controlled" is a finding.
- `01`'s data-readiness audit is already the unusual asset. A third candidate
  does not strengthen it.
- AMSS would reopen D1 (no R) and add a toolchain.

**Claude's failure to own:** the original scope was one dataset, a constrained
reallocation, ten artifacts. Since then: one dataset switch, an augmentation
layer built then abandoned, four platform APIs researched, and a third dataset
plus second simulator proposed. Each step was individually defensible; together
they are exactly the drift Caio warned about in his first message. Claude was
generating optionality instead of braking.

## 2026-08-18 — Phase 2 CLOSED: 03-data-quality written
Written from the nine interview reads plus measured figures. **612 prose words
against a 600 cap — 2% over, and left there deliberately.** Trimming further
would have cost a measured figure or a stated limitation. Noted rather than
quietly ignored; the counting method also charges for markdown emphasis, so the
true prose count is a little lower. Provenance stated in the header: notebook sections 1 and 5
were Claude-drafted at Caio's request, everything else is his.

**Three open questions handed to Phase 3:**
1. Is `ooh_S` one channel or a bucket? Nothing in the data answers it, and the
   recommendation reads very differently either way.
2. Does `newsletter` enter the model, and on which side of the D10 bounds?
3. Holiday features — count or per-holiday flags? Four weeks carry two holidays,
   so a binary flag discards information; Reformation Day is n=1.

**PHASE 2 COMPLETE.** `00` closed, `01`/`02`/`03` written. Phase 3 (`04-data-prep`)
is unblocked.

## 2026-08-18 — D13: simulate the dataset ourselves; market switches DE -> US
**Caio:** "let's just simulate the entire dataset, control for what we want, and
introduce a few typical scenarios of MMM optimization" -> "can we switch to us
instead of de".

**Chose:** generate the modelling dataset from a known DGP. **Supersedes D9**
(DE holidays) — with a simulated dataset the market is a choice, not an
inference, and US is the more legible default for the roles being targeted.

**Why this narrows rather than expands scope:**
- It ends the dataset search permanently. Three candidates audited, each with a
  measured identification failure; this is the terminal answer, not a fourth try.
- It supplies the one thing no real dataset offers — **an answer key**. The
  reallocation acquires a knowable right answer.
- It dissolves the open problems in one move: no mislabeled control, no
  confounder-or-mediator argument, no 2.6pp signal ceiling, no undecidable
  carryover. Those become parameters we set.

**The EDA work becomes the justification, not waste.** The narrative is "three
datasets audited, each one's identification failure measured, therefore
simulation with known truth." Every figure we computed is the evidence for that.

**Accepted cost:** "you made up your data" is the obvious critique. Two
mitigations, both required: the audit trail explains *why*, and realism is
calibrated to properties we **measured** (3.31x seasonality, 51-59% dark weeks
offline, always-on search, unit-cost CV 0.12-0.25) rather than chosen by taste.
**Also lost:** roughly half of Caio's interview reads — the Robyn-specific ones.
The methodological ones (seasonality must be controlled first; carryover cannot
be read from raw correlation) survive as **design requirements for the DGP**.

**Window fixed:** 2021-01-04 to 2024-12-23, **208 weeks, four complete calendar
years** (52/52/52/52). The partial-year defect flagged in `03` simply disappears
— we control the calendar now.

**US calendar measured:** 51 holiday dates, 46 of 208 weeks affected (22.1%),
11 distinct holidays each recurring 4-5 times. No n=1 problem, unlike DE's
Reformation Day. Brings the retail moments that matter — Thanksgiving/Black
Friday, Independence Day, Memorial Day, Labor Day.

**Still open:** the five-scenario list (saturated / underinvested / long
carryover / immediate / dud). Nothing generated until it is fixed and the DGP
parameters are committed to `04-data-prep.md`.

## 2026-08-18 — D14: modern digital channel mix; CTV is the under-invested channel
**Caio:** "can we do a more digital modern MMM, with video, mobile, etc" ->
"ok ctv it is."
Recorded as **Amendment 1** to `reference/dgp-spec.md`, dated, with the original
preserved. Nothing had been generated, so pre-registration holds.

**Six channels:** linear TV 28% (over-invested, cut), Meta social 18%, YouTube
16%, CTV 14% (under-invested, fund), branded search 12% (β = 0), Amazon retail
media 12% (seasonal decoy).

**Three design improvements, not just cosmetics:**
1. **The dud becomes branded search.** Same test — does the model invent an
   effect — but now it is the question marketing teams actually argue about.
   Always-on, smooth, correlates beautifully with revenue, *supposed* to look
   like a winner. Correctly returning ~zero is a real result.
2. **The decoy becomes Amazon retail media.** Q4 concentration is genuine
   behaviour for retail media, not a contrivance.
3. **Collinearity moves to linear TV <-> CTV (rho ~ 0.4).** The original TV-print
   pairing was realistic but tested nothing anyone cares about. Separating linear
   from CTV **is** the recommendation, so the model's hardest task now coincides
   with the decision's hardest question.

**Also:** "cut linear, fund streaming" is the defining media shift of the
2021-2024 window, which makes the reallocation a strategic finding rather than
two unrelated observations sharing a budget.

**Blocking generation:** Amazon Ads API and DSP export field specs are unverified.
Research agent running. **Field names will not be invented.**

## 2026-08-18 — Phase 3 — truth generated; two calibration amendments
`src/10_simulate_truth.py` run. Ground truth in `data/simulated/truth/`.

**Amendment 2 to the DGP spec, both recorded not hidden:**
1. **Signal target 8-10% → 4-6%.** Aspirational originally; against a 3x seasonal
   swing, 9% needs media driving ~half of revenue. The real retailer we audited
   achieved 4.4pp, Robyn 2.6pp. **Achieved 4.06%.**
2. **CTV beta 0.145 → 0.320.** At the registered value CTV's marginal ROI (1.65)
   fell below Meta's (2.39), so the designed "fund CTV" story did not hold.
   Scenario-design correction — no model has been run, so nothing is fitted to output.

**Two bugs found and fixed during generation:**
- Marginal ROI was computed with the *unscaled* beta while contributions used the
  scaled one, producing large negative nonsense (-1306 for TV). Caught because the
  numbers were obviously impossible.
- Calibration initially measured incremental R² using `log1p(spend)`, which
  understates signal that is genuinely present. That is misspecification, not
  absence — calibrating to it would have inflated the true media effect. Now
  measured against the true transforms.

**All six designed roles hold.** The headline: **linear TV has the highest
average ROI (5.03) and the lowest non-zero marginal ROI (1.20).** An analyst
reading average ROI funds it further; the correct answer is to cut it. That
inversion is the entire case for marginal analysis, and the model either recovers
it or does not.

## 2026-08-18 — Phase 3 — six source exports generated
`src/11_project_to_sources.py` → `data/simulated/exports/` (9 files, ~570KB).
**16 defect instances across 5 sources**, catalogued in `_planted_defects.json`.

**Verified present in the files:**
- Google Ads search: `ctr` as ratio (0.042), `cost_micros` (23788665690),
  **fractional conversions** (1122.825), and the **`0.0999` sentinel** — with no
  value strictly between 0 and 0.0999, which is the actual API behaviour.
- Meta: **daily** rows, every numeric a **JSON string**, `ctr` as **percent**
  (1.7945 vs Google's 0.042), last 2 weeks understated.
- DV360: header of display names, then a **blank line**, then a **`Grand Total`
  row 5 fields wide against a 10-field header**, then a metadata footer. Reach in
  a **separate file**, as the platform requires.
- Amazon: 1,155 rows against 1,456 possible days — **zero-activity rows omitted
  entirely**, so absence must be distinguished from zero.
- TV agency: `dd/mm/yyyy` dates, and a 14-row block where `gross_cost` is
  1000x smaller than its neighbours.

**Defect 14 is deliberately not in any file.** Week-boundary misalignment is
introduced *by the analyst* if ingest uses `pandas.resample("W")`, which defaults
to Sunday-ending against Google Ads' Monday weeks. It can only be detected by
checking, not by inspecting a source.

**One defect failed to plant on the first run:** the impression-share sentinel.
The beta(7,3) draw never dipped below the 0.1 floor, so no `0.0999` values
existed. Caught by asserting the count rather than assuming. Fixed.

