# Track A — Industry projects

> **Canonical copy:** `~/.claude/data-project-structure.md` — this structure is
> Caio's default for all data projects, not just this portfolio.
> If you change it here, change it there too.

These must read like real work artifacts, not a notebook someone tidied up.
The spine is **CRISP-DM's six phases**, and the document names below are the
real ones used in industry.

**Word caps are hard.** These artifacts are credible because they're terse.
A bloated data dictionary isn't more professional, it's less.

---

## Phase 1 — Business Understanding
*Learn the main goals of the project. Plan what you need to solve.*

| File | Real-world name | Contents | Cap |
|------|-----------------|----------|-----|
| `00-brief.md` | Project brief / kickoff | Objective. **The decision this informs and who makes it.** Success criteria. Deliverables. Constraints. | 400w |

If `00` can't name a decision and a decision-maker, stop. The project is trivia.

## Phase 2 — Data Understanding
*Gather early data. Check the quality and find initial patterns.*

| File | Real-world name | Contents | Cap |
|------|-----------------|----------|-----|
| `01-data-sources.md` | Data request / source inventory | Every source: owner, grain, coverage window, refresh cadence, how obtained, licence | 500w |
| `02-data-dictionary.md` | Data dictionary | Table: Field / Type / Required / Definition / Example / Notes | table only |
| `03-data-quality.md` | Data readiness memo + initial EDA | Gaps, coverage holes, known biases, first patterns seen, and **what this rules out** | 600w |

## Phase 3 — Data Preparation
*Clean, format, and fix the raw data. This step often takes the most time.*

| File | Real-world name | Contents | Cap |
|------|-----------------|----------|-----|
| `04-data-prep.md` | Transformation log / feature spec | Join keys and what didn't match. Deflation, normalization, per-capita bases. Constructed features and why. Rows dropped and the count. Reconciliation back to source totals. | 600w |

**This phase is the portfolio differentiator.** It's the largest share of real
project time and the part every other portfolio omits. Caio's stated strength —
scattered data from many sources — is *only* visible here. Do not let this file
be an afterthought; it is arguably the most important document in Track A.

## Phase 4 — Modeling
*Pick machine learning or statistical tools. Build and test models.*

| File | Real-world name | Contents | Cap |
|------|-----------------|----------|-----|
| `05-analysis-plan.md` | Analysis / measurement plan | **Written and dated BEFORE modeling.** Primary metric, method, controls, and the decision rule — "we act if X" — fixed in advance | 400w |
| `06-model-card.md` | Model card | Spec, assumptions, hyperparameters, validation, diagnostics, intended use, **prohibited use** | 600w |

Pre-registering the decision rule before seeing results is what separates
analysis from storytelling. It's standard in real incrementality work and it
costs nothing to do honestly here.

## Phase 5 — Evaluation
*Check if the model meets the business goals and works correctly.*

| File | Real-world name | Contents | Cap |
|------|-----------------|----------|-----|
| `07-evaluation.md` | Evaluation memo | Does it answer `00`'s question — not just does it fit. Business-goal check against the pre-registered rule. Limitations. **What would falsify this.** Where it would break | 600w |

Note the distinction CRISP-DM is making: **evaluation is not model diagnostics.**
R² belongs in `06`. This file asks whether the business actually got its answer.
Missing that distinction is the most common junior mistake.

## Phase 6 — Deployment
*Put the model into use. Plan how to watch and update it over time.*

| File | Real-world name | Contents | Cap |
|------|-----------------|----------|-----|
| `08-readout.md` | Readout ("walking deck") | Findings chart by chart, readable unattended | 800w |
| `09-recommendations.md` | Activation one-pager + monitoring plan | What to increase / maintain / reduce. Scenarios. What to do Monday. **Plus: refresh cadence, what would trigger a rebuild, how the model decays** | 400w |

"No activation plan" is a named top cause of real MMM failure. A finding without
an action isn't a deliverable. And real MMM practice refreshes on a cadence
(rolling the window forward, reusing hyperparameters) rather than rebuilding
from scratch — saying so in `09` reads as operational maturity.

---

## `DECISIONS.md` — runs across all six phases
Judgment calls in Caio's words, logged as they happen, including rejected options.

## CRISP-DM is a cycle, not a line
Phases loop — especially Data Understanding ↔ Data Preparation, and Evaluation
back to Business Understanding. **Record the loops in `DECISIONS.md`.** A project
that shows one honest backtrack ("the join failed, so I redefined the grain")
is more credible than one that pretends the path was straight.

## MMM-specific expected outputs
If the project is MMM, `08-readout.md` must contain: base vs. incremental
decomposition, contribution by channel, ROI **as ranges, not point estimates**,
marginal ROI, response/saturation curves showing where each channel sits on
diminishing returns, and budget reallocation scenarios.

## Two decks, not one
Industry practice: a **walking deck** meant to be read alone, and a
**presentation deck** meant to be talked through. Caio needs the walking deck —
the reader is a recruiter with nobody presenting to them.

## Three-layer rule maps onto the phases
Layer 1 (exec): `00` + `09`. Layer 2 (domain manager): `08`.
Layer 3 (technical screener): `02`, `04`, `05`, `06`, `07`.
