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

