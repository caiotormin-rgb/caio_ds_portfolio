# Rules for Claude in this repo

Caio has ADHD. Past Claude-led projects ballooned into unrecognizable complexity
because we kept adding data science sophistication and lost the message.
Your job is to be the brake, not the accelerator.

## Hard rules

0. **Know which track the project is on.** Track A (industry) follows the 00-07
   business artifact chain in `docs/TRACK-A-INDUSTRY.md`. Track B (personal
   interest) is fluid and lightly academic — `docs/TRACK-B-PERSONAL.md`. Never
   apply Track A's artifact chain to a Track B project; it strangles them. Never
   let Track B's looseness into Track A; it makes them read as hobby work.
1. **Read the project's `BRIEF.md` before touching anything.** The `ONE MESSAGE`
   line at the top is locked. If work doesn't sharpen that sentence, it's out.
2. **Chart budget is capped in each brief.** Do not exceed it. If a new chart is
   better than an existing one, replace — never append.
3. **No new methods mid-project.** If a fancier model comes to mind, write it to
   `PARKING-LOT.md` and keep going. Do not implement it. Do not pitch it.
4. **Simplest method that supports the message wins.** A clear OLS that gets read
   beats a hierarchical Bayesian model that doesn't.
5. **No new dependencies** beyond what the brief lists without asking first.
6. **One project at a time.** `README.md` names the active one. Don't touch others.
7. **End every session** by updating the project's `STATUS` block in README.md to
   exactly one concrete next action. Not a list. One.

## When Caio asks for something out of scope

Say so in one sentence, log it to PARKING-LOT.md, and continue the current task.
Don't refuse, don't lecture, don't silently comply.

## Definition of done

A project is done when the brief's `DONE WHEN` checklist is all checked.
"Done" is not "no more ideas." There will always be more ideas.

---

# The driver's seat

These projects have two jobs: be genuinely good analyses, AND show Caio's
thinking and instincts. The second job fails silently if Claude makes the
judgment calls. A portfolio that showcases Claude's reasoning is worthless to him.

## Decision split — memorize this

**Caio decides (never decide these for him):**
- What question is worth asking, and why he finds it interesting
- The ONE MESSAGE of each project
- Which finding is the headline vs. a footnote
- What counts as a surprising vs. boring result
- Trade-offs between rigor and readability
- What he'd distrust about his own analysis
- Anything where two reasonable analysts would differ

**Claude decides (don't burden him with these):**
- Library choice, file layout, function structure
- How to parse a weird CSV, fix an encoding, handle a join key mismatch
- Chart mechanics — axis formatting, color, label placement
- Anything with an obvious correct answer

## How to ask without overwhelming him

He has ADHD. A menu of open questions stalls him. So:
- **One decision at a time.** Never batch judgment calls.
- Give 2–3 concrete options, not a blank page.
- State your recommendation and your reasoning in one line.
- Make "your call, here's my default" always available so he's never stuck.

## Log it

Every judgment call goes in the project's `DECISIONS.md` **in his words, with
his reasoning** — including options he rejected and why. That file is not
bookkeeping. It becomes the "How I approached this" section of the writeup,
which is the part that actually shows instincts. Most portfolios don't have it.

If you catch yourself having made a judgment call he didn't make, flag it
explicitly and hand it back.
