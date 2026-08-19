"""Phase 4 — fit the MMM exactly as pre-registered in 05-analysis-plan.md.

Two-stage, which is how Robyn and most production MMMs are actually built:
  outer  scipy optimises the nonlinear transform parameters (theta, alpha, kappa)
  inner  given those transforms, coefficients are solved in closed form with a
         non-negativity constraint on media

That keeps the nonlinear search to 18 parameters instead of 33 on 202 rows, and
it is far more stable than throwing everything at one optimiser.

Per the reported span/the reported span the model is fit twice — with and without `category_demand` — and the
span is reported. Intervals come from a moving-block bootstrap frequentist with bootstrap intervals.

Writes data/simulated/model_results.json
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.optimize import minimize, lsq_linear

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "simulated"
SEED = 20260818
N_BOOT = 120
BLOCK = 13                       # quarter-length blocks preserve seasonal structure

CH = ["linear_tv", "meta_social", "youtube", "ctv", "search_brand", "amazon_retail"]
BASE = ["sin1", "cos1", "sin2", "cos2", "trend", "holiday_count", "holiday_retail_count"]
MAX_LAG = 12


def adstock(x, theta):
    """Geometric carryover, truncated at MAX_LAG as pre-registered."""
    w = theta ** np.arange(MAX_LAG)
    return np.convolve(x, w)[: len(x)]


def hill(x, alpha, kappa):
    xa = np.power(np.maximum(x, 0.0), alpha)
    return xa / (xa + kappa ** alpha)


def resolve_kappas(df, params):
    """Absolute kappa per channel, anchored to the FITTING data.

    Must be resolved once and then held fixed. If kappa is recomputed from
    whatever frame is passed in, scaling spend also scales kappa and the Hill
    transform becomes scale-invariant — which silently forces every marginal
    ROI to exactly zero. That bug is easy to write and hard to see.
    """
    ks = []
    for i, c in enumerate(CH):
        th, _, kf = params[3 * i: 3 * i + 3]
        ad = adstock(df[f"{c}_spend"].to_numpy(float), th)
        pos = ad[ad > 0]
        ks.append(max((np.median(pos) if len(pos) else 1.0) * kf, 1e-9))
    return np.array(ks)


def transforms(spend, params, kappas):
    cols = []
    for i, c in enumerate(CH):
        th, al, _ = params[3 * i: 3 * i + 3]
        ad = adstock(spend[f"{c}_spend"].to_numpy(float), th)
        cols.append(hill(ad, al, kappas[i]))
    return np.column_stack(cols)


def solve_linear(X_media, X_base, y):
    """Coefficients in closed form. Media constrained non-negative — standard MMM
    practice, since a channel cannot plausibly destroy revenue."""
    X = np.column_stack([np.ones(len(y)), X_base, X_media])
    n_free = 1 + X_base.shape[1]
    lo = np.r_[np.full(n_free, -np.inf), np.zeros(X_media.shape[1])]
    hi = np.full(X.shape[1], np.inf)
    r = lsq_linear(X, y, bounds=(lo, hi), max_iter=200)
    return r.x, X


def fit_once(df, use_control, x0=None, seed=0):
    y = np.log(df.revenue.to_numpy(float))
    base_cols = BASE + (["category_demand"] if use_control else [])
    X_base = df[base_cols].to_numpy(float)

    def obj(p):
        Xm = transforms(df, p, resolve_kappas(df, p))
        beta, X = solve_linear(Xm, X_base, y)
        return float(np.mean((y - X @ beta) ** 2))

    rng = np.random.default_rng(seed)
    if x0 is None:
        x0 = np.concatenate([[0.4, 1.5, 1.0] for _ in CH])
    bounds = [(0.0, 0.95), (0.5, 3.0), (0.1, 5.0)] * len(CH)
    best, best_v = x0, obj(x0)
    for _ in range(3):                       # a few restarts; the surface is bumpy
        cand = np.array([rng.uniform(lo, hi) for lo, hi in bounds])
        r = minimize(obj, cand, bounds=bounds, method="L-BFGS-B",
                     options=dict(maxiter=300))
        if r.fun < best_v:
            best, best_v = r.x, r.fun
    r = minimize(obj, best, bounds=bounds, method="L-BFGS-B", options=dict(maxiter=600))
    p = r.x
    kap = resolve_kappas(df, p)
    Xm = transforms(df, p, kap)
    beta, X = solve_linear(Xm, X_base, y)
    return dict(params=p, kappas=kap, beta=beta, base_cols=base_cols, mse=float(r.fun),
                r2=float(1 - np.var(y - X @ beta) / np.var(y)))


def roi_and_mroi(df, fit):
    """Contribution, ROI and marginal ROI on the revenue scale."""
    y = np.log(df.revenue.to_numpy(float))
    Xm = transforms(df, fit["params"], fit["kappas"])
    X_base = df[fit["base_cols"]].to_numpy(float)
    b = fit["beta"]
    n_free = 1 + X_base.shape[1]
    media_b = b[n_free:]
    fitted = np.exp(np.column_stack([np.ones(len(y)), X_base, Xm]) @ b)
    out = {}
    for i, c in enumerate(CH):
        # contribution: revenue with this channel on, minus with it zeroed
        Xm0 = Xm.copy(); Xm0[:, i] = 0.0
        base0 = np.exp(np.column_stack([np.ones(len(y)), X_base, Xm0]) @ b)
        contrib = float((fitted - base0).sum())
        spend = float(df[f"{c}_spend"].sum())
        # marginal: +1% spend on this channel
        d2 = df.copy(); d2[f"{c}_spend"] = d2[f"{c}_spend"] * 1.01
        Xm2 = transforms(d2, fit["params"], fit["kappas"])   # kappa HELD FIXED
        f2 = np.exp(np.column_stack([np.ones(len(y)), X_base, Xm2]) @ b)
        dspend = float(d2[f"{c}_spend"].sum() - spend)
        out[c] = dict(contribution=contrib,
                      roi=contrib / spend if spend else 0.0,
                      mroi=float((f2 - fitted).sum() / dspend) if dspend else 0.0,
                      coef=float(media_b[i]))
    return out


def block_resample_residuals(resid, rng):
    """Block-resample RESIDUALS, not rows.

    Resampling and reordering rows destroys the spend sequence, and adstock is
    defined on that sequence — every replicate would estimate carryover on a
    history that never existed. That is why the first attempt produced point
    estimates lying outside their own intervals.

    Residual bootstrap holds the media design fixed and only perturbs the
    outcome, which is the correct scheme for a time-series response model.
    Blocks preserve the autocorrelation in the residuals.
    """
    n = len(resid)
    out = []
    while len(out) < n:
        s = rng.integers(0, max(n - BLOCK, 1))
        out.extend(resid[s: s + BLOCK])
    return np.array(out[:n])


def main():
    f = pd.read_csv(D / "model_frame.csv", parse_dates=["week"])
    fit_df = f[f.settled].reset_index(drop=True)       # 202 settled weeks — the unsettled tail is excluded
    print(f"fitting on {len(fit_df)} settled weeks of {len(f)}\n")

    results = {}
    for use_control in (True, False):
        tag = "with_control" if use_control else "without_control"
        fit = fit_once(fit_df, use_control, seed=SEED)
        est = roi_and_mroi(fit_df, fit)
        print(f"{tag}: R2 {fit['r2']:.4f}")
        results[tag] = dict(r2=fit["r2"], estimates=est,
                            params={c: dict(theta=float(fit["params"][3*i]),
                                            alpha=float(fit["params"][3*i+1]),
                                            kappa=float(fit["kappas"][i]))
                                    for i, c in enumerate(CH)})

        # residual bootstrap — media design fixed, outcome perturbed
        y = np.log(fit_df.revenue.to_numpy(float))
        Xm = transforms(fit_df, fit["params"], fit["kappas"])
        Xb = fit_df[fit["base_cols"]].to_numpy(float)
        yhat = np.column_stack([np.ones(len(y)), Xb, Xm]) @ fit["beta"]
        resid = y - yhat

        rng = np.random.default_rng(SEED + (1 if use_control else 2))
        boots = {c: dict(roi=[], mroi=[]) for c in CH}
        for b in range(N_BOOT):
            sub = fit_df.copy()
            sub["revenue"] = np.exp(yhat + block_resample_residuals(resid, rng))
            try:
                bf = fit_once(sub, use_control, x0=fit["params"], seed=SEED + b)
                be = roi_and_mroi(sub, bf)
                for c in CH:
                    boots[c]["roi"].append(be[c]["roi"])
                    boots[c]["mroi"].append(be[c]["mroi"])
            except Exception:
                continue
            if (b + 1) % 40 == 0:
                print(f"   bootstrap {b+1}/{N_BOOT}")
        for c in CH:
            for k in ("roi", "mroi"):
                v = np.array(boots[c][k])
                results[tag]["estimates"][c][f"{k}_lo"] = float(np.percentile(v, 5))
                results[tag]["estimates"][c][f"{k}_hi"] = float(np.percentile(v, 95))
        # keep the raw draws: the pre-registered decision rule needs the interval on the DIFFERENCE between
        # two channels' marginal ROI, which cannot be built from separate intervals
        results[tag]["draws"] = {c: boots[c]["mroi"] for c in CH}
        results[tag]["n_boot"] = int(len(boots[CH[0]]["roi"]))

    (D / "model_results.json").write_text(json.dumps(results, indent=2))

    truth = json.load(open(D / "truth" / "parameters.json"))["channels"]
    print(f"\n{'channel':15s} {'true mROI':>10} {'est mROI':>9} {'90% interval':>18}  {'true θ':>7} {'est θ':>6}")
    e = results["with_control"]["estimates"]
    p = results["with_control"]["params"]
    for c in CH:
        print(f"{c:15s} {truth[c]['true_marginal_roi']:10.2f} {e[c]['mroi']:9.2f} "
              f"  [{e[c]['mroi_lo']:6.2f}, {e[c]['mroi_hi']:6.2f}]  "
              f"{truth[c]['theta']:7.2f} {p[c]['theta']:6.2f}")


if __name__ == "__main__":
    main()
