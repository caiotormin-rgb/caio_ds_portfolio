"""Generate notebooks/03_results.ipynb — same flat structure as the EDA.

One question per section, chart, then what it means. This notebook does the
thing no real engagement can: score every estimate against a known answer key.

Regeneration preserves any filled "Your read" cells, keyed by section heading.
"""
import os
import nbformat as nbf

nb = nbf.v4.new_notebook()
C = []
md = lambda s: C.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: C.append(nbf.v4.new_code_cell(s.strip()))
read = lambda: C.append(nbf.v4.new_markdown_cell("**Your read:**\n\n"))

md("""
# MMM — Results
### Scored against the answer key

Every number below is compared to the truth that generated the data. No real
engagement can do this, which is the whole reason the dataset was simulated
simulated dataset after three real candidates each failed on identification.

**Read `05-analysis-plan.md` first.** It was committed before any model existed,
so nothing here was chosen after seeing results.

| # | Question |
|---|---|
| 1 | Did the model get the ranking right? |
| 2 | How wrong are the levels? |
| 3 | Did it recover carryover? |
| 4 | Did it find the planted null? |
| 5 | Does the decision rule permit a recommendation? |
| 6 | How much did the control choice matter? |
""")

code("""
import json, numpy as np, pandas as pd, matplotlib.pyplot as plt

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e3e2df"
BLUE, ORANGE, AQUA, RED = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlecolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": .8,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "normal",
    "axes.titlelocation": "left", "figure.dpi": 110, "lines.linewidth": 2,
})
def tidy(ax, title=None, sub=None, ylab=None):
    if title: ax.set_title(title, pad=16 if sub else 6)
    if sub: ax.text(0, 1.015, sub, transform=ax.transAxes, fontsize=8.5, color=INK2)
    if ylab: ax.set_ylabel(ylab)
    ax.set_axisbelow(True); ax.grid(axis="x", visible=False); return ax

R = json.load(open("../data/simulated/model_results.json"))
T = json.load(open("../data/simulated/truth/parameters.json"))["channels"]
CH = ["linear_tv", "meta_social", "youtube", "ctv", "search_brand", "amazon_retail"]
LABEL = {"linear_tv": "Linear TV", "meta_social": "Meta social", "youtube": "YouTube",
         "ctv": "CTV", "search_brand": "Branded search", "amazon_retail": "Amazon retail"}

W = R["with_control"]
d = pd.DataFrame([{
    "channel": LABEL[c],
    "true_mroi": T[c]["true_marginal_roi"], "est_mroi": W["estimates"][c]["mroi"],
    "lo": W["estimates"][c]["mroi_lo"], "hi": W["estimates"][c]["mroi_hi"],
    "true_theta": T[c]["theta"], "est_theta": W["params"][c]["theta"],
    "share": T[c]["budget_share"],
} for c in CH])
print(f"bootstrap replicates: {W['n_boot']} | R2 with control {W['r2']:.4f} "
      f"| without {R['without_control']['r2']:.4f}")
d.round(3)
""")

md("## 1. Did the model get the ranking right?")
code("""
o = d.sort_values("true_mroi", ascending=False).reset_index(drop=True)
fig, ax = plt.subplots(figsize=(10, 3.8))
yv = np.arange(len(o))
ax.hlines(yv, o.true_mroi, o.est_mroi, color=GRID, linewidth=2, zorder=1)
ax.scatter(o.true_mroi, yv, s=70, color=INK, zorder=3, label="true")
ax.scatter(o.est_mroi, yv, s=70, color=BLUE, zorder=3, label="estimated")
ax.set_yticks(yv); ax.set_yticklabels(o.channel); ax.invert_yaxis()
ax.legend(frameon=False, fontsize=8.5, labelcolor=INK2)
ax.grid(axis="y", visible=False)
tidy(ax, "Marginal ROI: truth vs estimate, ordered by truth",
     "the decision needs the order, not the level", "")
ax.set_xlabel("Marginal ROI"); plt.tight_layout(); plt.show()

from scipy.stats import spearmanr
rho = spearmanr(d.true_mroi, d.est_mroi).statistic
print(f"rank correlation (Spearman): {rho:+.3f}")
print(f"highest true mROI : {d.loc[d.true_mroi.idxmax(),'channel']}")
print(f"highest est  mROI : {d.loc[d.est_mroi.idxmax(),'channel']}")
print(f"lowest  true mROI : {d.loc[d.true_mroi.idxmin(),'channel']}")
print(f"lowest  est  mROI : {d.loc[d.est_mroi.idxmin(),'channel']}")
""")
read()

md("## 2. How wrong are the levels?")
code("""
fig, ax = plt.subplots(figsize=(10, 3.8))
yv = np.arange(len(d))
ax.hlines(yv, d.lo, d.hi, color=BLUE, linewidth=3, alpha=.35)
ax.scatter(d.est_mroi, yv, s=60, color=BLUE, zorder=3, label="estimate (90% interval)")
ax.scatter(d.true_mroi, yv, s=70, color=INK, marker="D", zorder=4, label="truth")
ax.set_yticks(yv); ax.set_yticklabels(d.channel); ax.invert_yaxis()
ax.legend(frameon=False, fontsize=8.5, labelcolor=INK2); ax.grid(axis="y", visible=False)
covered = int(((d.true_mroi >= d.lo) & (d.true_mroi <= d.hi)).sum())
tidy(ax, "Estimated marginal ROI with 90% bootstrap intervals",
     f"truth falls inside the interval for {covered} of {len(d)} channels", "")
ax.set_xlabel("Marginal ROI"); plt.tight_layout(); plt.show()

d["ratio"] = d.est_mroi / d.true_mroi.replace(0, np.nan)
print(d[["channel", "true_mroi", "est_mroi", "lo", "hi", "ratio"]].round(2).to_string(index=False))
""")
read()

md("## 3. Did it recover carryover?")
code("""
fig, ax = plt.subplots(figsize=(5.2, 4.4))
ax.plot([0, .8], [0, .8], color=INK2, linestyle="--", linewidth=1)
ax.scatter(d.true_theta, d.est_theta, s=80, color=BLUE, zorder=3)
for _, r in d.iterrows():
    ax.annotate(r.channel, (r.true_theta, r.est_theta), fontsize=8,
                color=INK2, xytext=(6, -3), textcoords="offset points")
ax.set_xlim(0, .8); ax.set_ylim(-.05, .8)
tidy(ax, "Carryover: true vs estimated", "dashed line = perfect recovery", "estimated θ")
ax.set_xlabel("true θ"); plt.tight_layout(); plt.show()

err = (d.est_theta - d.true_theta).abs()
print(f"within 0.10 of truth: {int((err<=.10).sum())} of {len(d)} channels")
print(d[["channel", "true_theta", "est_theta"]].assign(abs_err=err.round(2)).round(2).to_string(index=False))
""")
read()

md("""
## 4. Did it find the planted null?
Branded search was built with a true effect of **exactly zero** — the
incrementality test. A model that invents an effect here is disqualified under
the abandon criteria in `05` the pre-registered abandon criteria.
""")
code("""
bs = d[d.channel == "Branded search"].iloc[0]
draws = np.array(W["draws"]["search_brand"])
fig, ax = plt.subplots(figsize=(9, 3.2))
ax.hist(draws, bins=30, color=BLUE, alpha=.75)
ax.axvline(0, color=INK, linewidth=2, label="truth = 0.00")
ax.axvline(bs.est_mroi, color=ORANGE, linewidth=2, label=f"estimate = {bs.est_mroi:.2f}")
ax.legend(frameon=False, fontsize=8.5, labelcolor=INK2); ax.grid(axis="x", visible=False)
share_at_zero = float((draws <= 0.001).mean())
tidy(ax, "Branded search — bootstrap distribution of marginal ROI",
     f"{share_at_zero:.0%} of replicates land at zero; 90% interval "
     f"[{bs.lo:.2f}, {bs.hi:.2f}]", "replicates")
ax.set_xlabel("Marginal ROI"); plt.tight_layout(); plt.show()

print(f"point estimate      : {bs.est_mroi:.2f}   (truth 0.00)")
print(f"90% interval        : [{bs.lo:.2f}, {bs.hi:.2f}]")
print(f"interval excludes 0 : {bool(bs.lo > 0)}")
print()
print("the pre-registered abandon criteria abandon criterion — 'branded search returns a confidently positive ROI':")
print(f"  TRIGGERED" if bs.lo > 0 else "  NOT triggered — the interval includes zero, so the model is not confident")
""")
read()

md("""
## 5. Does the decision rule permit a recommendation?
`05` fixed the rule before any model was fit the pre-registered decision rule:

> Recommend moving budget from A to B **only if** B's marginal ROI exceeds A's
> **and the bootstrap interval on the difference excludes 1.0.**

The interval on the *difference* needs paired draws — it cannot be built from
two separate intervals.
""")
code("""
draws = {c: np.array(W["draws"][c]) for c in CH}
n = min(len(v) for v in draws.values())
rows = []
for a in CH:
    for b in CH:
        if a == b: continue
        diff = draws[b][:n] - draws[a][:n]
        lo, hi = np.percentile(diff, [5, 95])
        rows.append(dict(**{"from": LABEL[a], "to": LABEL[b]},
                         gap=float(np.median(diff)), lo=float(lo), hi=float(hi),
                         passes=bool(lo > 0)))
p = pd.DataFrame(rows)
ok = p[p.passes].sort_values("gap", ascending=False)
print(f"{len(ok)} of {len(p)} channel pairs pass the pre-registered rule\\n")
print(ok.round(2).to_string(index=False) if len(ok) else "NO PAIR PASSES — the rule refuses to recommend.")
""")
read()

md("## 6. How much did the control choice matter?")
code("""
Wo = R["without_control"]
cmp = pd.DataFrame([{
    "channel": LABEL[c], "truth": T[c]["true_marginal_roi"],
    "with_control": W["estimates"][c]["mroi"],
    "without_control": Wo["estimates"][c]["mroi"],
} for c in CH])
cmp["span"] = (cmp.with_control - cmp.without_control).abs()

fig, ax = plt.subplots(figsize=(10, 3.6))
yv = np.arange(len(cmp))
ax.hlines(yv, cmp.without_control, cmp.with_control, color=GRID, linewidth=3)
ax.scatter(cmp.with_control, yv, s=55, color=BLUE, label="with control", zorder=3)
ax.scatter(cmp.without_control, yv, s=55, color=ORANGE, label="without control", zorder=3)
ax.scatter(cmp.truth, yv, s=70, color=INK, marker="D", label="truth", zorder=4)
ax.set_yticks(yv); ax.set_yticklabels(cmp.channel); ax.invert_yaxis()
ax.legend(frameon=False, fontsize=8.5, ncol=3, labelcolor=INK2); ax.grid(axis="y", visible=False)
tidy(ax, "What the control decision costs reporting the span",
     "the span is what an analyst without an answer key would have to report", "")
ax.set_xlabel("Marginal ROI"); plt.tight_layout(); plt.show()

cmp["closer"] = np.where((cmp.with_control - cmp.truth).abs()
                         < (cmp.without_control - cmp.truth).abs(), "with", "without")
print(cmp.round(2).to_string(index=False))
print(f"\\ncontrol version closer to truth on {int((cmp.closer=='with').sum())} of {len(cmp)} channels")
""")
read()

md("""
---
## Where this leaves us

Fill in once the sections above are worked through. Anything that becomes a
project decision goes to `05-analysis-plan.md`, and the conclusions belong in
`07-evaluation.md`.
""")

OUT = "notebooks/03_results.ipynb"
kept = 0
if os.path.exists(OUT):
    old = nbf.read(OUT, as_version=4)
    prev, cur = {}, None
    for c in old.cells:
        if c.cell_type == "markdown" and c.source.lstrip().startswith("## "):
            cur = c.source.lstrip().split("\n")[0].strip()
        elif c.cell_type == "markdown" and c.source.startswith("**Your read:**") and cur:
            if c.source.strip() != "**Your read:**":
                prev[cur] = c.source
    cur = None
    for i, c in enumerate(C):
        if c.cell_type == "markdown" and c.source.lstrip().startswith("## "):
            cur = c.source.lstrip().split("\n")[0].strip()
        elif (c.cell_type == "markdown" and c.source.startswith("**Your read:**")
              and cur in prev):
            C[i] = nbf.v4.new_markdown_cell(prev[cur]); kept += 1

nb["cells"] = C
nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbf.write(nb, OUT)
print(f"wrote {OUT} — {len(C)} cells" + (f", preserved {kept} read(s)" if kept else ""))
