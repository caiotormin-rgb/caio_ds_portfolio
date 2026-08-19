# 00 — Project brief
*Phase 1: Business Understanding. Cap 400w.*

**STATUS: Phase 1 closed. Objective, decision, decision-maker, success criteria
and constraints are settled. `[ASSUMED]` marks items Claude proposed that Caio
accepted implicitly rather than stated — revisit if they start driving results.**

## Objective
Quantify how much of revenue each media channel actually drives, establish where
each channel sits on its diminishing-returns curve, and recommend a reallocation
of the **same total budget** that increases revenue.

## The decision this informs
How to split next year's media budget across TV, out-of-home, print, Facebook,
and search — specifically, which channels get more, which get held flat, and
which get cut.

## Who makes that decision
Head of Media / marketing analytics lead at a consumer brand running both
offline and digital, briefing a CMO who signs off. [ASSUMED — the persona is
implied by the channel mix in the candidate dataset.]

## Success criteria
1. Channel contributions and ROIs reported **as ranges, not point estimates**.
2. A saturation curve per channel showing where current spend sits on it.
3. A reallocation scenario at constant total budget, with the projected revenue
   change stated as a range.
4. The recommendation survives the constraint test below — i.e. it is executable,
   not just optimal.

## Constraints
- Total budget is fixed. This is a reallocation, not a business case for more money.
- **DECIDED: the reallocation is constrained.** The optimizer must respect real
  media-planning constraints — channel floors and caps, and a maximum year-over-year
  shift per channel. Rationale: the recommendation has to be executable, not just
  optimal. An unconstrained optimizer that says "put everything in search" is the
  classic naive MMM output and gets dismissed in the room. Exact limits are set in
  `05-analysis-plan.md` and fixed before optimization runs.
- No paid tools. Open-source stack only.

## Deliverables
The CRISP-DM chain 00–09 per `~/.claude/data-project-structure.md`.

## Phase 5 addition — geo robustness check (D2)
After the national chain is complete, re-fit hierarchically on
`geo_all_channels.csv` (40 geos x 156 weeks — verified to be this same
simulation, unaggregated) and report whether the channel ranking and the
direction of the reallocation hold.

**Scope wall — all four bind:**
1. It starts **only after `00`-`09` are all drafted for the national model.**
   Not in parallel. Not "while I'm in there."
2. It answers **one question**: does the ranking and reallocation direction
   survive? Not a second model of record, not a geo-level recommendation, not
   new channels, not a restarted artifact chain.
3. It lives in **`07-evaluation.md` plus at most one chart** in the readout.
4. **If the national model turns out under-identified** and geo has to become
   the primary model, that is an explicit re-decision logged in `05-analysis-plan.md`
   with the reason — never a silent drift into scope.

## Explicitly out of scope
Attribution comparison, experiment calibration, methods stress-testing. All
parked in `PARKING-LOT.md`.

## Next
Phase 2 — Data Understanding. Dataset not yet chosen.
