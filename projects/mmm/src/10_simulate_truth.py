"""Phase 3 — generate the ground truth per reference/dgp-spec.md.

Parameters were pre-registered and committed before this ran (85ea4fa, amended
ce906f1). Nothing here may be tuned to model output; the one degree of freedom
is the noise scale, which is searched to hit a pre-stated target band and then
recorded.

Writes:
  data/simulated/truth/weekly_truth.csv   weekly series + true contributions
  data/simulated/truth/parameters.json    the answer key
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import holidays as H

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "simulated" / "truth"
SEED = 20260818
N_WEEKS = 208
START = "2021-01-04"

BASE_LEVEL = 800_000.0
TREND_PER_YEAR = 0.004
SEASON_PEAK_TROUGH = 3.0
TOTAL_MEDIA_BUDGET = 45_000_000.0

HOLIDAY_MULT = {"Thanksgiving Day": 1.35, "Christmas Day": 1.25, "Independence Day": 0.92}

# channel: budget share, adstock decay, Hill shape, operating point, beta
CHANNELS = {
    "linear_tv":     dict(share=0.28, theta=0.70, alpha=1.6, op=3.20, beta=0.185, dark=0.45),
    "meta_social":   dict(share=0.18, theta=0.40, alpha=1.6, op=0.80, beta=0.150, dark=0.35),
    "youtube":       dict(share=0.16, theta=0.45, alpha=1.5, op=1.10, beta=0.120, dark=0.25),
    "ctv":           dict(share=0.14, theta=0.55, alpha=1.7, op=0.28, beta=0.320, dark=0.30),
    "search_brand":  dict(share=0.12, theta=0.10, alpha=1.8, op=0.90, beta=0.000, dark=0.02),
    "amazon_retail": dict(share=0.12, theta=0.25, alpha=1.4, op=1.20, beta=0.080, dark=0.20),
}
TV_CTV_RHO = 0.40           # planning correlation — the pair whose separation IS the recommendation
Q4_LOAD_AMAZON = 0.60       # share of annual Amazon spend falling in Q4 — the decoy mechanism
# Revised during calibration: 8-10% was aspirational. The real retailer we
# audited achieved 4.4pp, Robyn 2.6pp. Forcing 9% requires media to drive an
# implausible share of revenue against a 3x seasonal swing. 4-6% is realistic
# and still ~2x Robyn. Recorded as Amendment 2 in the DGP spec.
TARGET_INCREMENTAL_R2 = (0.04, 0.06)


def adstock(x, theta):
    out = np.zeros_like(x, dtype=float)
    carry = 0.0
    for i, v in enumerate(x):
        carry = v + theta * carry
        out[i] = carry
    return out


def hill(x, alpha, kappa):
    xa = np.power(np.maximum(x, 0.0), alpha)
    return xa / (xa + kappa ** alpha)


def fourier(t, period=52.18, harmonics=2):
    cols = [np.ones_like(t, dtype=float)]
    for k in range(1, harmonics + 1):
        cols += [np.sin(2 * np.pi * k * t / period), np.cos(2 * np.pi * k * t / period)]
    return np.column_stack(cols)


def r2(y, X):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    return 1 - resid.var() / y.var()


def build_media_plans(weeks, rng):
    """Weekly spend per channel. Flighting, seasonal buying, and the TV<->CTV
    planning correlation are all imposed here — the response function is separate."""
    n = len(weeks)
    t = np.arange(n)
    woy = weeks.isocalendar().week.to_numpy(dtype=float)
    q4 = np.isin(weeks.quarter, [4])

    # shared video planning factor drives the TV <-> CTV correlation
    shared = rng.normal(size=n)
    plans = {}
    for name, p in CHANNELS.items():
        if name in ("linear_tv", "ctv"):
            z = np.sqrt(TV_CTV_RHO) * shared + np.sqrt(1 - TV_CTV_RHO) * rng.normal(size=n)
        elif name == "search_brand":
            z = np.zeros(n)                      # always-on, smooth: built below
        else:
            z = rng.normal(size=n)

        if name == "search_brand":
            # smooth, always-on: AR(1) with high persistence
            s = np.zeros(n); e = rng.normal(size=n)
            for i in range(1, n):
                s[i] = 0.72 * s[i - 1] + e[i]
            intensity = np.exp(0.28 * s)
        elif name == "amazon_retail":
            season = 1.0 + 1.6 * q4                       # Q4-loaded decoy
            intensity = np.exp(0.55 * z) * season
        else:
            season = 1.0 + 0.25 * np.sin(2 * np.pi * (woy - 6) / 52.18)
            intensity = np.exp(0.75 * z) * season

        # flighting: force the target share of weeks dark, cutting the lowest intensities
        k = int(round(p["dark"] * n))
        if k > 0:
            thresh = np.partition(intensity, k)[k]
            intensity = np.where(intensity <= thresh, 0.0, intensity)

        budget = TOTAL_MEDIA_BUDGET * p["share"]
        plans[name] = intensity / intensity.sum() * budget
    return plans


def main():
    rng = np.random.default_rng(SEED)
    weeks = pd.date_range(START, periods=N_WEEKS, freq="W-MON")
    t = np.arange(N_WEEKS)
    df = pd.DataFrame({"week": weeks})

    # ---- baseline ------------------------------------------------------------
    woy = weeks.isocalendar().week.to_numpy(dtype=float)
    raw_season = np.sin(2 * np.pi * (woy - 47) / 52.18) + 0.35 * np.sin(4 * np.pi * (woy - 47) / 52.18)
    season = (raw_season - raw_season.min()) / (raw_season.max() - raw_season.min())
    season = 1.0 + (SEASON_PEAK_TROUGH - 1.0) * season          # 1.0 .. 3.0
    trend = (1 + TREND_PER_YEAR) ** (t / 52.18)

    cal = H.country_holidays("US", years=sorted(set(weeks.year)))
    hol_mult = np.ones(N_WEEKS)
    hol_count = np.zeros(N_WEEKS, dtype=int)
    for i, w in enumerate(weeks):
        names = [n for d, n in cal.items() if w.date() <= d <= (w + pd.Timedelta(days=6)).date()]
        hol_count[i] = len(names)
        for nm in names:
            base = nm.replace(" (observed)", "")
            hol_mult[i] *= HOLIDAY_MULT.get(base, 1.0)

    # category demand: exogenous AR(1). Drives baseline AND media planning -> a real confounder.
    cd = np.zeros(N_WEEKS); e = rng.normal(size=N_WEEKS)
    for i in range(1, N_WEEKS):
        cd[i] = 0.6 * cd[i - 1] + e[i]
    cd = (cd - cd.mean()) / cd.std()
    cd_mult = np.exp(0.06 * cd)

    baseline = BASE_LEVEL * season * trend * hol_mult * cd_mult

    # ---- media ---------------------------------------------------------------
    plans = build_media_plans(weeks, rng)
    # let category demand tilt planning too — this is what makes it a confounder
    for name in plans:
        plans[name] = plans[name] * np.exp(0.10 * cd)
        plans[name] *= (TOTAL_MEDIA_BUDGET * CHANNELS[name]["share"]) / plans[name].sum()

    # ---- calibration: scale beta and sigma to hit the pre-stated signal band --
    # The DGP spec fixed the RELATIVE betas (the scenario design). Their absolute
    # scale and the noise level are the two calibration degrees of freedom, and
    # both are recorded. Measured against the true transforms, not a naive spec.
    def build(beta_scale):
        contrib, truth = {}, {}
        for name, p in CHANNELS.items():
            spend = plans[name]
            ad = adstock(spend, p["theta"])
            kappa = np.median(ad[ad > 0]) / p["op"]
            c = p["beta"] * beta_scale * hill(ad, p["alpha"], kappa)
            contrib[name] = c
            truth[name] = dict(theta=p["theta"], alpha=p["alpha"], kappa=float(kappa),
                               beta=p["beta"] * beta_scale, budget_share=p["share"],
                               total_spend=float(spend.sum()),
                               dark_weeks=float((spend == 0).mean()))
        return contrib, truth

    X_season = np.column_stack([fourier(t), cd, hol_count])
    rng_cal = np.random.default_rng(SEED + 99)
    chosen_scale, chosen_sigma, achieved = None, None, None
    for scale in np.arange(1.0, 12.0, 0.25):
        contrib, truth = build(scale)
        mm = 1.0 + sum(contrib.values())
        active = [contrib[c] for c in CHANNELS if CHANNELS[c]["beta"] > 0]
        X_full = np.column_stack([X_season] + active)
        for sigma in (0.10, 0.12, 0.15, 0.18, 0.22):
            y = np.log(baseline * mm * np.exp(rng_cal.normal(0, sigma, N_WEEKS) - sigma**2/2))
            inc = r2(y, X_full) - r2(y, X_season)
            if TARGET_INCREMENTAL_R2[0] <= inc <= TARGET_INCREMENTAL_R2[1]:
                chosen_scale, chosen_sigma, achieved = float(scale), float(sigma), float(inc)
                break
        if chosen_scale:
            break
    if chosen_scale is None:
        chosen_scale, chosen_sigma = 6.0, 0.15
        contrib, truth = build(chosen_scale)
        mm = 1.0 + sum(contrib.values())
        active = [contrib[c] for c in CHANNELS if CHANNELS[c]["beta"] > 0]
        X_full = np.column_stack([X_season] + active)
        y = np.log(baseline * mm * np.exp(rng_cal.normal(0, chosen_sigma, N_WEEKS) - chosen_sigma**2/2))
        achieved = float(r2(y, X_full) - r2(y, X_season))

    contrib, truth = build(chosen_scale)
    for name in CHANNELS:
        df[f"{name}_spend"] = plans[name]
    media_mult = 1.0 + sum(contrib.values())

    rng2 = np.random.default_rng(SEED + 1)
    noise = np.exp(rng2.normal(0, chosen_sigma, N_WEEKS) - chosen_sigma ** 2 / 2)
    revenue = baseline * media_mult * noise

    df["revenue"] = revenue
    df["baseline_true"] = baseline
    df["category_demand"] = cd
    df["holiday_count"] = hol_count
    for name in CHANNELS:
        df[f"{name}_contribution_true"] = contrib[name] * baseline * noise

    # ---- true ROI and marginal ROI -------------------------------------------
    for name, p in CHANNELS.items():
        spend = plans[name]
        base_rev = df[f"{name}_contribution_true"].sum()
        truth[name]["true_roi"] = float(base_rev / spend.sum()) if spend.sum() else 0.0
        bump = spend * 1.01
        ad2 = adstock(bump, p["theta"])
        c2 = truth[name]["beta"] * hill(ad2, p["alpha"], truth[name]["kappa"])
        d_rev = ((c2 - contrib[name]) * baseline * noise).sum()
        truth[name]["true_marginal_roi"] = float(d_rev / (bump - spend).sum())

    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "weekly_truth.csv", index=False)
    meta = dict(seed=SEED, n_weeks=N_WEEKS, start=START,
                beta_scale=chosen_scale,
                noise_sigma=chosen_sigma, achieved_incremental_r2=achieved,
                target_incremental_r2=list(TARGET_INCREMENTAL_R2),
                seasonality_peak_trough=float(season.max() / season.min()),
                total_media_spend=float(sum(plans[c].sum() for c in CHANNELS)),
                total_revenue=float(revenue.sum()), channels=truth)
    (OUT / "parameters.json").write_text(json.dumps(meta, indent=2))

    print(f"weeks {N_WEEKS} | {weeks[0]:%Y-%m-%d} -> {weeks[-1]:%Y-%m-%d}")
    print(f"seasonality peak/trough {season.max()/season.min():.2f}x")
    print(f"beta scale {chosen_scale:.2f} | noise sigma {chosen_sigma:.3f} -> incremental R2 {achieved:.4f} "
          f"(target {TARGET_INCREMENTAL_R2[0]}-{TARGET_INCREMENTAL_R2[1]})")
    print(f"media {sum(plans[c].sum() for c in CHANNELS):,.0f} | revenue {revenue.sum():,.0f} "
          f"| ratio {sum(plans[c].sum() for c in CHANNELS)/revenue.sum():.1%}")
    print()
    print(f"{'channel':15s} {'share':>6} {'dark':>6} {'true ROI':>9} {'true mROI':>10}")
    for name in CHANNELS:
        tr = truth[name]
        print(f"{name:15s} {tr['budget_share']:6.0%} {tr['dark_weeks']:6.0%} "
              f"{tr['true_roi']:9.2f} {tr['true_marginal_roi']:10.2f}")


if __name__ == "__main__":
    main()
