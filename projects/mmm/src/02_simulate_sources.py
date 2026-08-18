"""STALE — written against the Meridian columns (Channel0-4, conversions).
D8 switched the project to Robyn. The holiday logic is reusable; the brand
index and reach/frequency blocks reference columns that no longer exist.
Do not run. Rewrite or retire before use.
"""

"""Phase 2 — build the augmentation table.

Writes data/simulated/augmented_weekly.csv, keyed on `time`, joinable 1:1 to the
Meridian national file.

THE BOUNDARY: this script never writes to data/raw/. Google's columns stay
exactly as shipped. Everything produced here is ours and is listed in
PROVENANCE below, so the seam is always recoverable.

Three groups:
  A. holiday_*            REAL public data (US federal calendar). No invention.
  B. brand_interest_index SIMULATED. Trends-style index. A MEDIATOR, not a control.
  C. *_reach/_frequency   SIMULATED diagnostics, generated at weekly grain
                          because reach is not additive across days.

Deliberately NOT built: a simulated paid-search channel. It would carry zero
true effect on Google's conversions, so any estimated ROI for it would be noise.
See DECISIONS.md.
"""
from pathlib import Path
import importlib.util
import numpy as np
import pandas as pd
import holidays

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "simulated" / "augmented_weekly.csv"
SEED = 20260818

spec = importlib.util.spec_from_file_location("mmm", ROOT / "src" / "01_load.py")
mmm = importlib.util.module_from_spec(spec); spec.loader.exec_module(mmm)

PROVENANCE = {}   # column -> "real" | "simulated"


# --------------------------------------------------------------------------- A
def add_holidays(df: pd.DataFrame) -> pd.DataFrame:
    """REAL data. US federal calendar, aggregated to the Monday-start week.

    Country assumption: US. The source data names no market; USD-scale CPMs and
    the Q4 spend skew are consistent with a US advertiser. Documented, not inferred.
    """
    years = sorted({d.year for d in df.time} | {df.time.max().year + 1})
    cal = holidays.country_holidays("US", years=years)

    # EXACT names after stripping "(observed)". Substring matching is a trap here:
    # "Juneteenth National Independence Day" contains "Independence Day", which
    # silently doubled the July 4 flag from 4 weeks to 8.
    named = {
        "holiday_newyear":      {"New Year's Day"},
        "holiday_memorial":     {"Memorial Day"},
        "holiday_july4":        {"Independence Day"},
        "holiday_juneteenth":   {"Juneteenth National Independence Day"},
        "holiday_labor":        {"Labor Day"},
        "holiday_thanksgiving": {"Thanksgiving Day"},
        "holiday_christmas":    {"Christmas Day"},
    }
    norm = lambda v: v.replace(" (observed)", "").strip()

    rows = []
    for wk in df.time:
        days = pd.date_range(wk, wk + pd.Timedelta(days=6))
        hits = {d.date(): cal.get(d.date()) for d in days if d.date() in cal}
        row = {"time": wk, "holiday_count": len(hits)}
        seen = {norm(v) for v in hits.values()}
        for col, names in named.items():
            row[col] = int(bool(seen & names))
        # Retail-relevant derived timings
        xmas = pd.Timestamp(year=wk.year, month=12, day=25)
        if wk > xmas:
            xmas = pd.Timestamp(year=wk.year + 1, month=12, day=25)
        row["weeks_to_christmas"] = int((xmas - wk).days // 7)
        rows.append(row)

    h = pd.DataFrame(rows)
    # No separate Black Friday flag: it always falls in the Thanksgiving week,
    # so it would be a perfectly collinear duplicate.
    for c in h.columns:
        if c != "time":
            PROVENANCE[c] = "real"
    return df.merge(h, on="time", how="left")


# --------------------------------------------------------------------------- B
def adstock(x: np.ndarray, decay: float) -> np.ndarray:
    out = np.zeros_like(x, dtype=float)
    carry = 0.0
    for i, v in enumerate(x):
        carry = v + decay * carry
        out[i] = carry
    return out


def add_brand_index(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """SIMULATED. Google-Trends-shaped branded interest index.

    Constructed as: adstocked upper-funnel media (Channel3 TV + Channel1 video)
    + annual seasonality + noise. That construction makes it a MEDIATOR — media
    drives it — so controlling for it in the MMM would delete part of the media
    effect being measured. That is deliberate and is the honest shape for a
    brand-search series. It must never be used as an innocent control.

    Trends constraints enforced: integer, bounded [0, 100], exactly one period
    equals 100, low values floor to 0, privacy noise injected.
    """
    # Blend contemporaneous and carried-over exposure. Pure adstock on an
    # always-on series is dominated by its slow-moving level and ends up almost
    # uncorrelated with the raw weekly series, which would break the mediator story.
    raw = (df.Channel3_impression.to_numpy(dtype=float) / df.Channel3_impression.max()
           + df.Channel1_impression.to_numpy(dtype=float) / df.Channel1_impression.max())
    ads = (adstock(df.Channel3_impression.to_numpy(dtype=float), 0.6) / df.Channel3_impression.max()
           + adstock(df.Channel1_impression.to_numpy(dtype=float), 0.5) / df.Channel1_impression.max())
    upper = 0.65 * (raw / raw.max()) + 0.35 * (ads / ads.max())
    upper = (upper - upper.min()) / (upper.max() - upper.min())

    woy = df.time.dt.isocalendar().week.to_numpy(dtype=float)
    seasonal = 0.5 + 0.5 * np.sin(2 * np.pi * (woy - 8) / 52.0)

    latent = 0.80 * upper + 0.20 * seasonal
    latent = latent + rng.normal(0, 0.035, len(latent))     # privacy noise

    idx = 100.0 * (latent - latent.min()) / (latent.max() - latent.min())
    idx = np.rint(idx).astype(int)
    idx[idx < 3] = 0                                        # sub-threshold -> 0
    idx[int(np.argmax(idx))] = 100                          # exactly one 100

    df = df.copy()
    df["brand_interest_index"] = idx
    PROVENANCE["brand_interest_index"] = "simulated"
    return df


# --------------------------------------------------------------------------- C
def add_reach_frequency(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """SIMULATED diagnostics, generated directly at weekly grain.

    Reach is set cardinality and is NOT additive across days, so this is built
    per week rather than summed — see reference/platform-data-specs.md.

    Reach curve: R = U * (1 - exp(-k * I / U)), the standard saturating form.
    U is the addressable universe. Frequency falls out as I / R and is never
    averaged.
    """
    df = df.copy()
    specs = {                       # channel: (universe, k, target freq band)
        "Channel1": (58_000_000, 0.62, "video"),    # named YouTube / premium video
        "Channel4": (44_000_000, 0.70, "social"),   # named paid social
    }
    for ch, (universe, k, _) in specs.items():
        impr = df[f"{ch}_impression"].to_numpy(dtype=float)
        reach = universe * (1.0 - np.exp(-k * impr / universe))
        reach = reach * (1.0 + rng.normal(0, 0.012, len(reach)))   # measurement wobble
        reach = np.minimum(reach, impr * 0.92)      # reach <= impressions, strictly
        reach = np.rint(reach).astype(np.int64)
        freq = impr / np.maximum(reach, 1)
        df[f"{ch}_reach"] = reach
        df[f"{ch}_frequency"] = np.round(freq, 6)
        PROVENANCE[f"{ch}_reach"] = "simulated"
        PROVENANCE[f"{ch}_frequency"] = "simulated"
    return df


# --------------------------------------------------------------------------- validate
def validate(df: pd.DataFrame) -> None:
    assert len(df) == 156 and df.time.is_unique
    assert not df.isna().any().any(), "augmentation produced missing values"

    b = df.brand_interest_index
    assert b.dtype.kind in "iu", "Trends index must be integer"
    assert b.between(0, 100).all(), "Trends index out of [0,100]"
    assert (b == 100).sum() == 1, "exactly one period must equal 100"

    for ch in ("Channel1", "Channel4"):
        impr, r, f = df[f"{ch}_impression"], df[f"{ch}_reach"], df[f"{ch}_frequency"]
        assert (r <= impr).all(), f"{ch}: reach exceeds impressions"
        assert (r > 0).all(), f"{ch}: non-positive reach"
        assert (f >= 1.0).all(), f"{ch}: frequency below 1"
        assert np.allclose(f, impr / r, rtol=1e-5), f"{ch}: frequency != impressions/reach"

    assert df.holiday_count.between(0, 3).all()
    for c, lo, hi in [("holiday_christmas", 3, 4), ("holiday_july4", 3, 4),
                      ("holiday_thanksgiving", 3, 3), ("holiday_juneteenth", 3, 4)]:
        assert lo <= df[c].sum() <= hi, f"{c}: {df[c].sum()} weeks, expected {lo}-{hi}"
    assert df.filter(like="holiday_").T.duplicated().sum() == 0, "duplicate holiday flags"


def main() -> None:
    rng = np.random.default_rng(SEED)
    n = mmm.national()
    aug = add_holidays(n)
    aug = add_brand_index(aug, rng)
    aug = add_reach_frequency(aug, rng)
    validate(aug)

    new_cols = ["time"] + list(PROVENANCE)
    out = aug[new_cols]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)

    real = [c for c, v in PROVENANCE.items() if v == "real"]
    sim = [c for c, v in PROVENANCE.items() if v == "simulated"]
    print(f"wrote {OUT.relative_to(ROOT)} — {len(out)} rows x {len(out.columns)} cols")
    print(f"  REAL      ({len(real)}): {', '.join(real)}")
    print(f"  SIMULATED ({len(sim)}): {', '.join(sim)}")
    print()
    for ch in ("Channel1", "Channel4"):
        f = aug[f"{ch}_frequency"]
        rr = (aug[f"{ch}_reach"] / aug[f"{ch}_impression"])
        print(f"  {ch}: frequency {f.min():.2f}–{f.max():.2f} (mean {f.mean():.2f}) | "
              f"reach/impr {rr.min():.2f}–{rr.max():.2f}")
    b = aug.brand_interest_index
    print(f"  brand_interest_index: min {b.min()} max {b.max()} mean {b.mean():.1f} "
          f"| zeros {(b == 0).sum()} | corr with conversions {b.corr(aug.conversions):+.3f}")
    print("all assertions passed")


if __name__ == "__main__":
    main()
