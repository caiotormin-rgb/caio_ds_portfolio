"""Generate notebooks/01_eda.ipynb — structure stays simple and flat.

Per section: question -> evidence -> what to look for + references -> blank cell.

The "what to look for" bullets are PROMPTS, never conclusions. They tell Caio
where to point his attention and what would make a reading wrong. If one of them
ever starts to state a finding, it has drifted and should be cut.

All reference URLs were HTTP-checked before being written in.
"""
import os
import nbformat as nbf

nb = nbf.v4.new_notebook()
C = []
md = lambda s: C.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: C.append(nbf.v4.new_code_cell(s.strip()))

def guide(points, refs):
    body = "#### What to look for\n\n" + "\n".join(f"- {p}" for p in points)
    body += "\n\n#### Reference\n\n" + "\n".join(f"- [{t}]({u})" for t, u in refs)
    md(body)
    C.append(nbf.v4.new_markdown_cell("**Your read:**\n\n"))

# --- reference shorthands (all verified 200) ---------------------------------
MER_DATA   = ("Meridian — collecting data", "https://developers.google.com/meridian/docs/user-guide/collect-data")
MER_NAT    = ("Meridian — loading national data", "https://developers.google.com/meridian/docs/user-guide/load-national-data")
MER_SCHEMA = ("Meridian — unified data schema", "https://developers.google.com/meridian/docs/user-guide/mmm-unified-schema")
MER_SPEC   = ("Meridian — model specification", "https://developers.google.com/meridian/docs/basics/model-spec")
MER_CONF   = ("Meridian — configuring the model", "https://developers.google.com/meridian/docs/user-guide/configure-model")
MER_ROI    = ("Meridian demo — ROI, marginal ROI and response curves", "https://github.com/google/meridian/blob/main/demo/ROI_mROI_Response_Curves.ipynb")
JIN        = ("Jin et al. — Bayesian Methods for Media Mix Modeling with Carryover and Shape Effects", "https://research.google/pubs/bayesian-methods-for-media-mix-modeling-with-carryover-and-shape-effects/")
CHAN       = ("Chan & Perry — Challenges and Opportunities in Media Mix Modeling", "https://research.google/pubs/challenges-and-opportunities-in-media-mix-modeling/")
ROBYN      = ("Robyn — adstock and saturation features", "https://facebookexperimental.github.io/Robyn/docs/features")
FPP3       = ("Hyndman & Athanasopoulos — Forecasting: Principles and Practice (decomposition, seasonality)", "https://otexts.com/fpp3/")
VIF        = ("Multicollinearity — what it does to coefficient estimates", "https://en.wikipedia.org/wiki/Multicollinearity")
OSS        = ("Open-Source Media and Marketing Mix Modeling — practice-oriented overview", "https://link.springer.com/article/10.1007/s40547-026-00161-4")

md("""
# MMM — Exploratory Data Analysis
### Meridian simulated national dataset, 156 weeks

**How to use this.** Each section asks one question, renders the evidence, then
gives you prompts and reading. The conclusions go in the **Your read** cells and
they are yours — nothing here writes them for you.

Anything that becomes a *project decision* goes to `DECISIONS.md`, not here.

**Questions, in order**

| # | Question | Why it matters before modeling |
|---|---|---|
| 1 | Is the data complete and regular? | Gaps and duplicates break time-series models silently |
| 2 | What is the outcome doing? | Trend and seasonality compete with media for credit |
| 3 | How is the money split? | Sets which channels can even be meaningfully estimated |
| 4 | What does spend look like week to week? | Flighted vs always-on changes how carryover is identified |
| 5 | Is there enough variation to identify an effect? | A channel that never changes cannot be measured |
| 6 | Are the channels collinear? | Collinearity is the main reason MMMs come out unstable |
| 7 | Do the controls behave? | A control that tracks the outcome will steal media's credit |
| 8 | Is there visible carryover? | Decides whether adstock is warranted, and roughly how long |
| 9 | Is there visible diminishing returns? | The saturation curve is the deliverable — does the data show one? |
| 10 | Are spend and impressions consistent? | Unstable CPM means the two units are not interchangeable |

**Start here if you want background before the data:**
[Meridian — collecting data](https://developers.google.com/meridian/docs/user-guide/collect-data) ·
[Chan & Perry — Challenges and Opportunities in MMM](https://research.google/pubs/challenges-and-opportunities-in-media-mix-modeling/)
""")

code("""
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e3e2df"
BLUE, ORANGE, AQUA, RED = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
DIVERGING = LinearSegmentedColormap.from_list("bl_rd", [BLUE, "#f0efec", RED])

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlecolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "normal",
    "axes.titlelocation": "left", "figure.dpi": 110, "lines.linewidth": 2,
})

def tidy(ax, title=None, sub=None, ylab=None, pad=None):
    if title: ax.set_title(title, pad=pad or (16 if sub else 6))
    if sub:   ax.text(0, 1.015, sub, transform=ax.transAxes, fontsize=8.5, color=INK2)
    if ylab:  ax.set_ylabel(ylab)
    ax.set_axisbelow(True); ax.grid(axis="x", visible=False)
    return ax

import importlib.util
spec = importlib.util.spec_from_file_location("mmm", "../src/01_load.py")
mmm = importlib.util.module_from_spec(spec); spec.loader.exec_module(mmm)
mmm.validate()          # every integrity assertion runs before any analysis
df = mmm.national()

CH      = [f"Channel{i}" for i in range(5)]
SPEND   = [f"{c}_spend" for c in CH]
IMPR    = [f"{c}_impression" for c in CH]
CONTROL = ["competitor_sales_control", "sentiment_score_control", "Promo"]
df["revenue"] = df.conversions * df.revenue_per_conversion
df["total_spend"] = df[SPEND].sum(axis=1)

print(f"{len(df)} weeks | {df.time.min():%Y-%m-%d} to {df.time.max():%Y-%m-%d}")
df.head(3)
""")

md("## 1. Is the data complete and regular?")
code("""
gaps = df.time.diff().dt.days.value_counts().to_dict()
print("day-steps between rows:", gaps)
print("duplicate weeks      :", df.time.duplicated().sum())
print("missing values       :", int(df.isna().sum().sum()))
print("negative spend       :", int((df[SPEND] < 0).sum().sum()))
print("zero-conversion weeks:", int((df.conversions == 0).sum()))
print()
print(df[["conversions", "revenue_per_conversion", "total_spend"]].describe().T.to_string())
""")
guide([
 "Are all the day-steps identical? A single 14-day step means a missing week that silently becomes a jump in every lag and every adstock calculation.",
 "Any duplicated weeks? Duplicates double-weight those observations without warning.",
 "Look at min/max on the outcome. Are there values extreme enough to dominate a squared-error fit?",
 "`revenue_per_conversion` — is it varying at all, or effectively a constant? If constant, revenue carries no information that conversions doesn't.",
 "Ask yourself what you would *not* be able to detect with only 156 rows. That number constrains everything downstream.",
], [MER_SCHEMA, MER_DATA])

md("## 2. What is the outcome doing?")
code("""
fig, ax = plt.subplots(2, 1, figsize=(11, 6.4))

ax[0].plot(df.time, df.conversions/1e6, color=BLUE)
tidy(ax[0], "Conversions per week", "156 weeks, 2021-01 to 2024-01", "Conversions (m)")

m = df.groupby(df.time.dt.month).conversions.mean()/1e6
ax[1].plot(m.index, m.values, color=BLUE, marker="o", markersize=5)
ax[1].set_xticks(range(1, 13))
ax[1].set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
tidy(ax[1], "Mean conversions by calendar month",
     f"peak/trough ratio = {m.max()/m.min():.2f}x", "Conversions (m)")
plt.tight_layout(); plt.show()

t = np.arange(len(df))
slope, icept = np.polyfit(t, df.conversions, 1)
print(f"linear trend: {slope:,.0f} conversions/week "
      f"({slope*52/df.conversions.mean()*100:+.1f}% of mean per year)")
""")
guide([
 "Trend, flat, or stepped? A trend competes with media for credit — anything growing steadily will get attributed to whichever channel also grew.",
 "How strong is seasonality? Compare the peak/trough ratio to what you'd expect for a real advertiser.",
 "Any level shifts or structural breaks — a jump that no media plan would explain? Those usually mean something happened to the business, and the model has no way to know.",
 "The key question: **if you removed all media, what shape would remain?** That residual shape is the baseline the model has to find, and everything it can't explain gets dumped there.",
 "With only three years, how many full seasonal cycles do you actually have to learn seasonality from?",
], [FPP3, CHAN])

md("## 3. How is the money split across channels?")
code("""
tot = df[SPEND].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(9, 3.4))
ax.barh([c.replace("_spend","") for c in tot.index][::-1], (tot/1e6).values[::-1], color=BLUE, height=.62)
for i, v in enumerate((tot/1e6).values[::-1]):
    ax.text(v, i, f"  {v:,.1f}m ({v/(tot.sum()/1e6)*100:.0f}%)", va="center", fontsize=9, color=INK2)
ax.set_xlim(0, (tot/1e6).max()*1.16)
ax.grid(axis="y", visible=False)
tidy(ax, "Total spend by channel, whole period", "Share of paid spend in brackets", "")
ax.set_xlabel("Spend (m)"); plt.tight_layout(); plt.show()

print((tot/tot.sum()).mul(100).round(1).to_string(), "\\n")
print(f"total paid spend : {tot.sum():,.0f}")
print(f"total revenue    : {df.revenue.sum():,.0f}")
print(f"spend / revenue  : {tot.sum()/df.revenue.sum():.1%}")
""")
guide([
 "How concentrated is the budget? A channel at a few percent of spend may simply lack the leverage to be estimated with any precision — and a confident ROI on it would be a red flag, not a finding.",
 "Is the spend/revenue ratio plausible? Compare it against what you'd expect for the kind of advertiser this is meant to represent.",
 "Which channels are large enough that moving money in or out would actually change the business? Those are the ones your recommendation lives or dies on.",
 "Remember the channels are anonymous here. Does the spend pattern hint at what media type each one is — and would you be willing to defend that guess in an interview?",
], [MER_DATA, MER_ROI])

md("## 4. What does each channel's spend look like week to week?")
code("""
fig, axes = plt.subplots(5, 1, figsize=(11, 9), sharex=True)
for ax, c in zip(axes, CH):
    s = df[f"{c}_spend"]/1e3
    ax.vlines(df.time, 0, s, color=BLUE, linewidth=1.4)
    tidy(ax, f"{c}  —  {(s==0).mean():.0%} of weeks at zero spend", ylab="Spend (k)")
axes[-1].set_xlabel("")
fig.suptitle("Weekly spend by channel", x=0.005, ha="left", y=1.0, fontsize=12)
plt.tight_layout(); plt.show()
""")
guide([
 "Which channels are always-on and which are flighted? They are identified very differently — a channel that never turns off gives you almost nothing to learn decay from.",
 "Do the bursts repeat seasonally? If a channel only ever runs in peak weeks, its effect and seasonality are entangled and may not be separable at all.",
 "Look for long dark stretches. Those are where you can actually *watch* an effect decay, and they're what makes adstock estimable.",
 "Does any channel change regime — ramps up partway through and stays there? A regime change breaks the assumption that response is stable across the window.",
 "Does the flighting look like a media plan a human would buy, or like a random number generator? Your answer bears on how much the findings can be said to transfer.",
], [ROBYN, MER_SPEC])

md("## 5. Is there enough variation to identify an effect?")
code("""
v = pd.DataFrame({
    "cv": df[SPEND].std()/df[SPEND].mean(),
    "zero_weeks": (df[SPEND]==0).mean(),
    "p10_p90_ratio": df[SPEND].quantile(.9)/df[SPEND].quantile(.1).replace(0, np.nan),
})
v.index = [i.replace("_spend","") for i in v.index]

fig, ax = plt.subplots(1, 2, figsize=(11, 3.4))
ax[0].bar(v.index, v.cv, color=BLUE, width=.6)
tidy(ax[0], "Coefficient of variation", "higher = more identifying variation", "std / mean")
ax[1].bar(v.index, v.zero_weeks*100, color=BLUE, width=.6)
tidy(ax[1], "Share of weeks dark", "on/off bursts help identify carryover", "% of weeks")
for a in ax: a.grid(axis="x", visible=False)
plt.tight_layout(); plt.show()
print(v.round(3).to_string())
""")
guide([
 "Which channel has the least variation? That one will come back with the widest uncertainty, and it should.",
 "Is the variation genuine on/off cycling, or a handful of spikes? A few spikes means a few observations are carrying the entire estimate.",
 "The blunt test: **would you be comfortable quoting an ROI for a channel that barely moved?** If not, decide now what you'll say about it rather than after the model gives you a number.",
 "Low variation and high collinearity compound each other. Hold this alongside section 6 rather than reading them separately.",
], [CHAN, OSS])

md("## 6. Are the channels collinear?")
code("""
cols = SPEND + ["competitor_sales_control", "sentiment_score_control", "Promo", "conversions"]
cm = df[cols].corr()
cm.index = cm.columns = [c.replace("_spend","").replace("_control","") for c in cols]

fig, ax = plt.subplots(figsize=(7.6, 6.4))
im = ax.imshow(cm, cmap=DIVERGING, vmin=-1, vmax=1)
ax.set_xticks(range(len(cm))); ax.set_xticklabels(cm.columns, rotation=45, ha="right")
ax.set_yticks(range(len(cm))); ax.set_yticklabels(cm.index)
for i in range(len(cm)):
    for j in range(len(cm)):
        ax.text(j, i, f"{cm.iloc[i,j]:.2f}", ha="center", va="center", fontsize=7.5,
                color=INK if abs(cm.iloc[i,j]) < .55 else "#ffffff")
ax.grid(False)
tidy(ax, "Correlation matrix", "diverging scale, gray = no relationship", pad=22)
fig.colorbar(im, ax=ax, shrink=.72)
plt.tight_layout(); plt.show()

off = cm.loc[[c.replace("_spend","") for c in SPEND], [c.replace("_spend","") for c in SPEND]]
off = off.where(~np.eye(len(off), dtype=bool)).abs().stack()
print(f"strongest channel-to-channel pair: {off.idxmax()} r = {off.max():.3f}")
""")
guide([
 "Which channel pairs are strongly related? When two channels move together, the data cannot tell you which one did the work — the *sum* is estimable, the split is not.",
 "Does any channel correlate with a **control**? That's worse than channel-to-channel, because the control is not something you can reallocate.",
 "Look at the bottom row. Are the raw channel-to-outcome correlations near zero? If so, what does that imply about how much work the model has to do — and would a naive analyst have concluded media doesn't work?",
 "Correlation is pairwise. Several channels can be jointly collinear without any single pair looking bad. What would you need to compute to detect that?",
], [VIF, CHAN])

md("## 7. Do the controls behave, or does something dominate the outcome?")
code("""
z = lambda s: (s - s.mean())/s.std()
fig, ax = plt.subplots(2, 1, figsize=(11, 6.2), sharex=True)

ax[0].plot(df.time, z(df.conversions), color=BLUE, label="conversions")
ax[0].plot(df.time, z(df.competitor_sales_control), color=ORANGE, label="competitor sales")
ax[0].plot(df.time, z(df.sentiment_score_control), color=AQUA, label="sentiment")
ax[0].legend(frameon=False, fontsize=8.5, ncol=3, labelcolor=INK2)
tidy(ax[0], "Outcome and controls, standardised to a common scale",
     "one axis, z-scored — no dual axis", "z-score")

ax[1].vlines(df.time, 0, df.Promo, color=BLUE, linewidth=1.4)
tidy(ax[1], f"Promo  —  active in {(df.Promo>0).mean():.0%} of weeks", ylab="Promo")
plt.tight_layout(); plt.show()

print(df[CONTROL + SPEND].corrwith(df.conversions).round(3).to_string())
""")
guide([
 "Does any control track the outcome closely enough to absorb most of its variance? If so, media gets estimated off whatever is left over, and the ROIs come back small for a reason that has nothing to do with media.",
 "**Is anything here actually a mediator rather than a control?** If media influences it, and you control for it, you delete part of the effect you're trying to measure. This is the single most common way a well-intentioned control ruins an MMM.",
 "Is `Promo` a control or a channel? It has a budget owner and a spend implication — so whose lever is it, and should a reallocation be allowed to touch it?",
 "Sentiment: is it a cause of conversions, a consequence of them, or both? Write down which, because the model can't tell and will assume you were right.",
], [CHAN, MER_CONF])

md("""
## 8. Is there visible carryover?
Correlation of each channel's spend at lag *k* with conversions today.
A peak at k>0, or a slow decay, is a hint that adstock is warranted.
""")
code("""
LAGS = range(0, 9)
fig, axes = plt.subplots(1, 5, figsize=(13, 2.9), sharey=True)
for ax, c in zip(axes, CH):
    r = [df[f"{c}_spend"].shift(k).corr(df.conversions) for k in LAGS]
    ax.bar(list(LAGS), r, color=BLUE, width=.62)
    ax.axhline(0, color=INK2, linewidth=.8)
    tidy(ax, c, ylab="corr" if c == "Channel0" else None)
    ax.set_xlabel("lag (weeks)"); ax.grid(axis="x", visible=False)
fig.suptitle("Cross-correlation: spend at lag k vs conversions today",
             x=0.005, ha="left", y=1.06, fontsize=12)
plt.tight_layout(); plt.show()
""")
guide([
 "Does correlation peak at lag 0, or later? A later peak is a hint — not proof — that the effect takes time to land.",
 "Does it decay smoothly, or jump around? Smooth decay is consistent with adstock. Jumping around is usually noise wearing a costume.",
 "**The trap:** this is raw correlation with nothing controlled for. If both spend and conversions are seasonal, you will see a lag pattern that is pure seasonality. What would you need to do to rule that out before believing any of these shapes?",
 "How many weeks of carryover would you consider *plausible* for each media type, before looking? Writing that down first stops you from rationalising whatever the chart shows.",
], [JIN, ROBYN])

md("""
## 9. Is there visible diminishing returns?
Weeks binned by spend level; the dot is mean conversions in that bin.
A flattening at the right-hand end is the saturation the model is meant to find.
""")
code("""
fig, axes = plt.subplots(1, 5, figsize=(13, 3.0), sharey=True)
for ax, c in zip(axes, CH):
    s = df[f"{c}_spend"]
    ax.scatter(s/1e3, df.conversions/1e6, s=10, color=BLUE, alpha=.35, linewidths=0)
    q = pd.qcut(s, 5, duplicates="drop")
    b = df.groupby(q, observed=True).agg(x=(f"{c}_spend","mean"), y=("conversions","mean"))
    ax.plot(b.x/1e3, b.y/1e6, color=ORANGE, marker="o", markersize=5)
    tidy(ax, c, ylab="Conversions (m)" if c == "Channel0" else None)
    ax.set_xlabel("Spend (k)")
fig.suptitle("Spend vs conversions, with quintile means (orange)",
             x=0.005, ha="left", y=1.06, fontsize=12)
plt.tight_layout(); plt.show()
""")
guide([
 "Does the quintile line bend over at the top, stay straight, or slope down?",
 "**The trap:** this is bivariate and uncontrolled. High-spend weeks may also be high-season weeks, or weeks when a promo ran. Does any shape you see survive that suspicion?",
 "If a line slopes *downward*, resist reading it as 'this channel hurts sales'. What does it more likely say about **when** the planner chose to spend?",
 "This is the closest thing here to a preview of your actual deliverable — the saturation curve. If you can't see a bend now, what would it mean if the model produces a confident one later?",
], [JIN, MER_ROI])

md("## 10. Are spend and impressions consistent?")
code("""
fig, axes = plt.subplots(1, 5, figsize=(13, 2.9), sharex=True)
for ax, c in zip(axes, CH):
    cpm = (df[f"{c}_spend"] / df[f"{c}_impression"].replace(0, np.nan)) * 1000
    ax.plot(df.time, cpm, color=BLUE)
    tidy(ax, f"{c}  (r={df[f'{c}_spend'].corr(df[f'{c}_impression']):.3f})",
         ylab="Cost per 1k impressions" if c == "Channel0" else None)
    ax.tick_params(axis="x", labelrotation=45, labelsize=7)
fig.suptitle("Implied CPM over time — flat means spend and impressions are interchangeable",
             x=0.005, ha="left", y=1.06, fontsize=12)
plt.tight_layout(); plt.show()
""")
guide([
 "Is CPM flat, drifting, or jumpy? Flat means spend and impressions carry identical information and the choice between them is free.",
 "If CPM drifts, the choice matters: **spend measures what it cost, impressions measure what was delivered.** Media effects come from delivery; budget decisions are made in money. Which unit belongs on which side of your model?",
 "Rising CPM over time would be a real-world signal of auction pressure or audience exhaustion. Does anything like that appear here — and if not, what does that tell you about the simulation?",
 "Whichever unit you choose, you'll need the other one to convert a modelled effect back into a budget recommendation. Note now how you'd do that.",
], [MER_DATA, MER_NAT])

md("""
---
## Where this leaves us

Fill in once the sections above are worked through. Anything that turns into a
project decision goes into `DECISIONS.md` — not here.

**Questions this raised that the data can't answer:**

**Things to check before modeling:**

---

### Further reading

**The two papers behind most MMM practice**
- [Jin et al. — Bayesian Methods for MMM with Carryover and Shape Effects](https://research.google/pubs/bayesian-methods-for-media-mix-modeling-with-carryover-and-shape-effects/) — where adstock and Hill saturation come from
- [Chan & Perry — Challenges and Opportunities in Media Mix Modeling](https://research.google/pubs/challenges-and-opportunities-in-media-mix-modeling/) — the honest account of what MMM can and cannot identify. Read this one before defending any result.

**Where the field is now**
- [Open-Source Media and Marketing Mix Modeling — practice-oriented overview](https://link.springer.com/article/10.1007/s40547-026-00161-4)
- [Packaging Up Media Mix Modeling (arXiv)](https://arxiv.org/abs/2403.14674)
- [Estimating Ad Effectiveness Using Geo Experiments](https://research.google/pubs/estimating-ad-effectiveness-using-geo-experiments-in-a-time-based-regression-framework/) — relevant to the Phase 5 geo step

**Tooling**
- [Meridian docs](https://developers.google.com/meridian) · [model specification](https://developers.google.com/meridian/docs/basics/model-spec) · [getting-started notebook](https://github.com/google/meridian/blob/main/demo/Meridian_Getting_Started.ipynb)
- [Robyn — adstock and saturation](https://facebookexperimental.github.io/Robyn/docs/features) — different framework, same concepts, often explained more plainly
- [PyMC-Marketing MMM example](https://www.pymc-marketing.io/en/stable/notebooks/mmm/mmm_example.html)
""")

# --- preserve Caio's work -----------------------------------------------------
# The notebook is generated, but the "Your read" cells are HIS. Regenerating must
# never destroy them. Pull the existing text forward, in order, before writing.
OUT = "notebooks/01_eda.ipynb"
kept = 0
if os.path.exists(OUT):
    old = nbf.read(OUT, as_version=4)
    old_reads = [c.source for c in old.cells
                 if c.cell_type == "markdown" and c.source.startswith("**Your read:**")]
    new_reads = [i for i, c in enumerate(C)
                 if c.cell_type == "markdown" and c.source.startswith("**Your read:**")]
    for i, text in zip(new_reads, old_reads):
        if text.strip() != "**Your read:**":
            C[i] = nbf.v4.new_markdown_cell(text)
            kept += 1
    # Warn about anything else he added that generation will drop.
    extra = [c for c in old.cells
             if c.cell_type == "code" and not c.source.strip()
             and c.source not in {x.source for x in C}]
    if extra:
        print(f"note: dropping {len(extra)} empty cell(s) added outside the generator")

nb["cells"] = C
nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbf.write(nb, OUT)
print(f"wrote {OUT} — {len(C)} cells" + (f", preserved {kept} filled 'Your read' cell(s)" if kept else ""))
