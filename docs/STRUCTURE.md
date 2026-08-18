# Structure — hub

Two tracks, different shapes, same discipline.

- **Track A — industry projects** → [TRACK-A-INDUSTRY.md](TRACK-A-INDUSTRY.md)
  Real business artifact chain (00–07). Proves he can do the job.
- **Track B — personal interest projects** → [TRACK-B-PERSONAL.md](TRACK-B-PERSONAL.md)
  Fluid, inquisitive, lightly academic. Proves he's worth an hour of conversation.
- **The public site** → [PORTFOLIO-SITE.md](PORTFOLIO-SITE.md)

## Universal rules — both tracks, no exceptions

### 1. Locked central question
Written before work starts. In Caio's words. If work doesn't sharpen it, it's out.

### 2. Hard chart budget
Set in the brief. Replace, never append.

### 3. `DECISIONS.md`
Judgment calls in Caio's words, logged as they happen — including rejected
options. Showing you considered a fancier method and chose not to use it is a
stronger signal than using it.

### 4. The three-layer rule
Every project readable at three depths; a reader stopping at any layer gets
something complete.

| Layer | Reader | Gets | Time |
|-------|--------|------|------|
| 1 | Executive, recruiter skimming | One sentence, one number, one implied decision | 15 sec |
| 2 | The manager who owns the domain | Charts + so-what captions, the trade-off | 3 min |
| 3 | Technical screener, peer analyst | Method, assumptions, code, why not the fancier approach | unbounded |

**Layer 3 is always separated, never woven into layer 2.** Method detail mixed
into narrative is the most common way portfolio projects lose their audience.

### 5. Captions state implications, not descriptions
- Bad: "Adoption rate by age band over time."
- Good: "Over-60 adoption inflected 14 months after under-30 — the segment
  wasn't resistant, it was reached late."

If a caption can only describe, the chart probably isn't earning its slot.

### 6. Honest limitations, written before the charts get polished
Senior analysts are identified by this section. Juniors omit it.

## Repo layout
```
projects/<slug>/
  BRIEF.md / 00-brief.md    depending on track
  DECISIONS.md
  data/     raw/ (gitignored) + cached/ (small, committed)
  src/      numbered scripts, run top to bottom
  outputs/  charts, never over budget
```
