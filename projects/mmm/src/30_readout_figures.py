"""Phase 6 — the readout figure set.

Eight figures, one per claim in 08-readout.md. Every caption states an
implication, never a description. Nothing here is decorative: if a chart does
not carry a claim, it is not in the set.

Writes outputs/readout/*.png
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "simulated"
OUT = ROOT / "outputs" / "readout"

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e3e2df"
BLUE, ORANGE, AQUA, RED = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlecolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": .8,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "normal",
    "axes.titlelocation": "left", "figure.dpi": 150, "lines.linewidth": 2,
    "text.parse_math": False,
})

CH = ["linear_tv", "meta_social", "youtube", "ctv", "search_brand", "amazon_retail"]
LAB = {"linear_tv": "Linear TV", "meta_social": "Meta social", "youtube": "YouTube",
       "ctv": "CTV", "search_brand": "Branded search", "amazon_retail": "Amazon retail"}


def tidy(ax, title=None, sub=None, ylab=None, pad=None):
    if title: ax.set_title(title, pad=pad or (18 if sub else 8))
    if sub: ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=9, color=INK2)
    if ylab: ax.set_ylabel(ylab)
    ax.set_axisbelow(True); ax.grid(axis="x", visible=False)
    return ax


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, bbox_inches="tight")
    plt.close(fig)
    print(f"  {name}")


def main():
    t = pd.read_csv(D / "truth" / "weekly_truth.csv", parse_dates=["week"])
    mt = pd.read_csv(D / "modelling_table.csv", parse_dates=["week"])
    P = json.load(open(D / "truth" / "parameters.json"))
    R = json.load(open(D / "model_results.json"))
    W = R["with_control"]
    TR = P["channels"]
    print("readout figures:")

    # 1 ── the business: seasonality dwarfs media
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.fill_between(t.week, 0, t.revenue / 1e6, color=BLUE, alpha=.18)
    ax.plot(t.week, t.revenue / 1e6, color=BLUE)
    ax.plot(t.week, t.baseline_true / 1e6, color=INK2, linestyle="--", linewidth=1.4)
    ax.text(t.week.iloc[12], t.baseline_true.max() / 1e6 * .55,
            "dashed = baseline before any media", fontsize=8.5, color=INK2)
    mm = t.groupby(t.week.dt.month).revenue.mean()
    tidy(ax, "Revenue swings 3× a year. Media moves it by a few percent.",
         f"peak/trough {mm.max()/mm.min():.1f}× · media adds "
         f"{P['achieved_incremental_r2']:.1%} of explained variance once seasonality is controlled",
         "Revenue ($m/week)")
    save(fig, "fig1_the_business.png")

    # 2 ── the budget: concentration and flighting
    sp = {c: mt[f"{c}_spend"].sum() for c in CH}
    tot = sum(sp.values())
    order = sorted(CH, key=lambda c: -sp[c])
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.4), gridspec_kw={"width_ratios": [1, 1.5]})
    axes[0].barh([LAB[c] for c in order][::-1], [sp[c] / 1e6 for c in order][::-1],
                 color=[ORANGE if c == "linear_tv" else BLUE for c in order][::-1], height=.62)
    for i, c in enumerate(order[::-1]):
        axes[0].text(sp[c] / 1e6, i, f"  {sp[c]/tot:.0%}", va="center", fontsize=9, color=INK2)
    axes[0].set_xlim(0, max(sp.values()) / 1e6 * 1.22); axes[0].grid(axis="y", visible=False)
    tidy(axes[0], "Linear TV takes 28% of the budget", "four-year spend by channel", "")
    axes[0].set_xlabel("Spend ($m)")

    for c, col in zip(["linear_tv", "ctv"], [ORANGE, AQUA]):
        axes[1].vlines(mt.week, 0, mt[f"{c}_spend"] / 1e3, color=col, linewidth=1.1,
                       alpha=.85, label=LAB[c])
    axes[1].legend(frameon=False, fontsize=9, labelcolor=INK2)
    tidy(axes[1], "Both video channels are flighted, and bought together",
         "on/off bursts are what make carryover estimable at all", "Spend ($k/week)")
    plt.tight_layout(); save(fig, "fig2_the_budget.png")

    # 3 ── the pipeline reconciles exactly
    rec = json.load(open(D / "ingest_report.json"))["reconciliation"]
    fig, ax = plt.subplots(figsize=(9, 3.2))
    x = np.arange(len(rec))
    ax.bar(x - .19, [r["truth"] / 1e6 for r in rec], .38, color=INK, label="source of record")
    ax.bar(x + .19, [r["ingested"] / 1e6 for r in rec], .38, color=BLUE, label="after reconciliation")
    ax.set_xticks(x); ax.set_xticklabels([LAB[r["channel"]] for r in rec], rotation=18, ha="right")
    ax.legend(frameon=False, fontsize=9, labelcolor=INK2); ax.grid(axis="x", visible=False)
    worst = max(abs(r["rel_diff"]) for r in rec)
    tidy(ax, "Six platform exports reconcile to the dollar",
         f"different units, grains and week definitions · worst residual {worst:.4%}", "Spend ($m)")
    plt.tight_layout(); save(fig, "fig3_reconciliation.png")

    # 4 ── THE finding: average vs marginal
    avg = [TR[c]["true_roi"] for c in CH]
    mar = [TR[c]["true_marginal_roi"] for c in CH]
    o = np.argsort(avg)[::-1]
    fig, ax = plt.subplots(figsize=(10, 3.8))
    y = np.arange(len(CH))
    ax.hlines(y, [avg[i] for i in o], [mar[i] for i in o], color=GRID, linewidth=3, zorder=1)
    ax.scatter([avg[i] for i in o], y, s=80, color=INK2, zorder=3, label="average ROI")
    ax.scatter([mar[i] for i in o], y, s=80, color=RED, zorder=3, label="marginal ROI — the next dollar")
    ax.set_yticks(y); ax.set_yticklabels([LAB[CH[i]] for i in o]); ax.invert_yaxis()
    ax.axvline(1, color=INK2, linewidth=.9, linestyle=":")
    ax.legend(frameon=False, fontsize=9, labelcolor=INK2); ax.grid(axis="y", visible=False)
    ax.annotate("highest average,\nlowest marginal", xy=(mar[0], 0), xytext=(mar[0] + 1.1, .55),
                fontsize=8.5, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.1))
    tidy(ax, "Linear TV looks like the best channel and is the one to cut",
         "average ROI says what a channel has returned; marginal says what the next dollar returns", "")
    ax.set_xlabel("Return per $1"); plt.tight_layout(); save(fig, "fig4_average_vs_marginal.png")

    # 5 ── what the model recovered
    d = pd.DataFrame([{"ch": LAB[c], "true": TR[c]["true_marginal_roi"],
                       "est": W["estimates"][c]["mroi"],
                       "lo": W["estimates"][c]["mroi_lo"], "hi": W["estimates"][c]["mroi_hi"],
                       "tt": TR[c]["theta"], "et": W["params"][c]["theta"]} for c in CH])
    o = d.sort_values("true", ascending=False).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 3.8))
    y = np.arange(len(o))
    ax.hlines(y, o.lo, o.hi, color=BLUE, linewidth=3, alpha=.3)
    ax.scatter(o.est, y, s=65, color=BLUE, zorder=3, label="model estimate (90% interval)")
    ax.scatter(o["true"], y, s=80, color=INK, marker="D", zorder=4, label="truth")
    ax.set_yticks(y); ax.set_yticklabels(o.ch); ax.invert_yaxis()
    ax.legend(frameon=False, fontsize=9, labelcolor=INK2); ax.grid(axis="y", visible=False)
    cov = int(((o["true"] >= o.lo) & (o["true"] <= o.hi)).sum())
    tidy(ax, "The model got the two ends right and overstated everything",
         f"truth falls inside the interval for {cov} of {len(o)} channels · levels inflated 2–3×", "")
    ax.set_xlabel("Marginal ROI"); plt.tight_layout(); save(fig, "fig5_recovery.png")

    # 6 ── why it failed
    draws = np.array(W["draws"]["search_brand"])
    bs = d[d.ch == "Branded search"].iloc[0]
    fig, ax = plt.subplots(figsize=(10, 3.4))
    ax.hist(draws, bins=32, color=RED, alpha=.65)
    ax.axvline(0, color=INK, linewidth=2.4)
    ax.text(0, ax.get_ylim()[1] * .92, "  truth = 0.00", fontsize=9.5, color=INK, va="top")
    ax.axvline(bs.lo, color=INK2, linestyle="--", linewidth=1.2)
    ax.text(bs.lo, ax.get_ylim()[1] * .55,
            f"  interval starts at {bs.lo:.2f}\n  — it never touches zero",
            fontsize=8.5, color=INK2, va="top")
    ax.grid(axis="x", visible=False)
    tidy(ax, "The model was confident about a channel that does nothing",
         f"branded search · true return $0.00 · estimated ${bs.est:.2f} · 90% interval "
         f"[{bs.lo:.2f}, {bs.hi:.2f}]", "bootstrap replicates")
    ax.set_xlabel("Estimated return per $1"); plt.tight_layout(); save(fig, "fig6_the_null.png")

    # 7 ── the corroborating failure
    fig, ax = plt.subplots(figsize=(5.6, 4.4))
    ax.plot([0, .8], [0, .8], color=INK2, linestyle="--", linewidth=1)
    ok = (d.et - d.tt).abs() <= .10
    ax.scatter(d.tt[ok], d.et[ok], s=90, color=BLUE, zorder=3)
    ax.scatter(d.tt[~ok], d.et[~ok], s=90, color=RED, zorder=3)
    for _, r in d.iterrows():
        ax.annotate(r.ch, (r.tt, r.et), fontsize=8, color=INK2,
                    xytext=(7, -3), textcoords="offset points")
    ax.set_xlim(0, .85); ax.set_ylim(-.06, .85)
    tidy(ax, "Carryover was recovered for two channels of six",
         "dashed line = perfect recovery · red = missed by more than 0.10", "estimated decay")
    ax.set_xlabel("true decay"); plt.tight_layout(); save(fig, "fig7_carryover.png")

    # 8 ── the recommendation: what the test costs
    ann = {c: TR[c]["total_spend"] / 4 for c in CH}
    wk = TR["search_brand"]["total_spend"] / 208
    at_risk = wk * 6 * 0.4
    fig, ax = plt.subplots(figsize=(9, 2.6))
    ax.barh(["Branded search\nspend per year", "At risk in a\n6-week holdout"],
            [ann["search_brand"] / 1e6, at_risk / 1e6], color=[BLUE, ORANGE], height=.55)
    for i, v in enumerate([ann["search_brand"] / 1e6, at_risk / 1e6]):
        ax.text(v, i, f"  ${v:,.2f}m", va="center", fontsize=10, color=INK2)
    ax.set_xlim(0, ann["search_brand"] / 1e6 * 1.3); ax.grid(axis="y", visible=False)
    tidy(ax, f"The test costs ${at_risk/1e3:.0f}k to settle a ${ann['search_brand']/1e6:.2f}m question",
         "40% of markets dark for six weeks", "")
    ax.set_xlabel("$m"); plt.tight_layout(); save(fig, "fig8_the_test.png")


if __name__ == "__main__":
    main()
