# Caio Tormin — Data Science Portfolio

**Status: themes not chosen yet.** The projects listed below are draft proposals.
Curated deliberately — 3 sharp projects beat 8 half-finished ones.

## The through-line

Every project applies a **commercial analytics method** to a **public or social
question**. That combination is the differentiator: MMM people don't touch
public budgets, and civic-data people don't know MMM.

| # | Project | Method sold | Personal angle |
|---|---------|-------------|----------------|
| 1 | [How Pix Ate Brazil](projects/pix-adoption/BRIEF.md) | product adoption, diffusion, cohorts | 21st-century change, demographics |
| 2 | [Diminishing Returns on Public Money](projects/public-mmm/BRIEF.md) | **MMM** — adstock, saturation, budget allocation | public spending, social services |
| 3 | [Did It Actually Work?](projects/did-it-work/BRIEF.md) | incrementality, causal inference | policy evaluation |

Two tracks — see [docs/STRUCTURE.md](docs/STRUCTURE.md):
**Track A (industry)** projects ship a real business artifact chain organized by
CRISP-DM's six phases — brief, source inventory, data dictionary, readiness memo,
transformation log, pre-registered analysis plan, model card, evaluation memo,
readout, activation one-pager. **Track B (personal interest)**
projects are fluid and lightly academic — a question, a stated prior, and an
honest account of where he was wrong.
Every project is readable at three depths and names the person who acts on it.
Each project carries a `DECISIONS.md` logging the judgment calls in Caio's own
words; that file becomes the "How I approached it" section of the writeup.

**Build order: 1 → 2 → 3.** Project 1 is first because it produces a beautiful
chart fastest. Momentum matters more than starting with the flagship.

---

## STATUS

**Active project:** `projects/mmm/` — end-to-end MMM, Track A.
**Use case:** classic budget reallocation, constrained optimizer.

**Phase 1 (Business Understanding): CLOSED.** See `projects/mmm/00-brief.md`.
**Phase 2 (Data Understanding): IN PROGRESS.** Blocked on choosing the dataset.

**Next action:** Caio works through `projects/mmm/notebooks/01_eda.ipynb` and
fills the ten "Your read" cells. Nothing else moves.

**D8 — dataset switched to Robyn `dt_simulated_weekly`** after a readiness audit
rejected the Meridian sample (no flighting, 1.07x seasonality, no spend-outcome
signal at national or geo grain). 208 weeks, real named channels, 3.31x
seasonality, 4/5 channels flighted, all five sloping upward.

**Phase 2 artifacts:** `00` closed · `01` **STALE, rewrite** · `02` **STALE,
rewrite** · `03` waiting on Caio's reads. Notebook rebuilt and current.

**Agreed sequence — do not skip, do not skip the decisions inside it:**
find the right data → ingest → prepare → **Caio analyzes it himself, with help**
→ review and discuss → *then* modeling strategy.
Modeling questions are OUT OF BOUNDS until that discussion has happened.
Every decision gets an explicit, logged entry in `DECISIONS.md` — no implicit calls.

**Note:** the other three drafted projects (`pix-adoption`, `public-mmm`,
`did-it-work`) are still Claude's disposable drafts and are all civic — Caio has
ruled that civic domains belong to Track B, not Track A. Do not build them.

*(Claude: update this block at the end of every session. One next action. Not a list.)*
