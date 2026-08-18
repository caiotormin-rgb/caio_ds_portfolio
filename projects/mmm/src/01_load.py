"""Phase 2 — ingest and validate the Meridian simulated datasets.

Run directly to assert every integrity property this project relies on:
    python src/01_load.py

Import the loaders from a notebook:
    import importlib.util
    spec = importlib.util.spec_from_file_location("mmm", "../src/01_load.py")
    mmm = importlib.util.module_from_spec(spec); spec.loader.exec_module(mmm)
    df = mmm.national()
"""
from pathlib import Path
import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
NATIONAL = RAW / "meridian_national_all_channels.csv"
GEO      = RAW / "meridian_geo_all_channels.csv"

CHANNELS = [f"Channel{i}" for i in range(5)]
SPEND    = [f"{c}_spend" for c in CHANNELS]
IMPR     = [f"{c}_impression" for c in CHANNELS]
CONTROLS = ["competitor_sales_control", "sentiment_score_control", "Promo"]
OUTCOME  = "conversions"


def national() -> pd.DataFrame:
    df = pd.read_csv(NATIONAL, parse_dates=["time"]).sort_values("time")
    return df.reset_index(drop=True)


def geo() -> pd.DataFrame:
    df = pd.read_csv(GEO, parse_dates=["time"])
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed") or c == ""])
    return df.sort_values(["geo", "time"]).reset_index(drop=True)


def validate() -> None:
    n, g = national(), geo()

    # --- shape and regularity -------------------------------------------------
    assert len(n) == 156, f"national: expected 156 weeks, got {len(n)}"
    assert n.time.is_unique, "national: duplicate weeks"
    assert (n.time.diff().dropna().dt.days == 7).all(), "national: irregular weekly spacing"
    assert not n.isna().any().any(), "national: missing values"

    assert g.geo.nunique() == 40, f"geo: expected 40 geos, got {g.geo.nunique()}"
    assert g.time.nunique() == 156, "geo: expected 156 weeks"
    assert len(g) == 40 * 156, "geo: panel is not balanced"
    assert not g.isna().any().any(), "geo: missing values"

    # --- expected columns -----------------------------------------------------
    for col in SPEND + IMPR + CONTROLS + [OUTCOME, "revenue_per_conversion"]:
        assert col in n.columns, f"national: missing column {col}"

    # --- value sanity ---------------------------------------------------------
    assert (n[SPEND] >= 0).all().all(), "national: negative spend"
    assert (n[OUTCOME] > 0).all(), "national: non-positive conversions"

    # --- the load-bearing property: national IS geo, aggregated ---------------
    # Documented in DECISIONS.md and relied on by the Phase 5 geo robustness step.
    # If this ever fails, the two files are no longer the same simulation.
    agg = g.groupby("time")[[OUTCOME] + SPEND].sum().sort_index()
    ref = n.set_index("time")[[OUTCOME] + SPEND].sort_index()
    rel = ((agg - ref).abs() / ref.abs()).max().max()
    assert rel < 1e-9, f"national != geo aggregated (max relative diff {rel:.2e})"

    print(f"national : {len(n)} weeks, {n.time.min():%Y-%m-%d} to {n.time.max():%Y-%m-%d}")
    print(f"geo      : {g.geo.nunique()} geos x {g.time.nunique()} weeks = {len(g)} rows")
    print(f"aggregation identity holds (max relative diff {rel:.1e})")
    print(f"paid spend {n[SPEND].sum().sum():,.0f} | "
          f"revenue {(n[OUTCOME] * n.revenue_per_conversion).sum():,.0f}")
    print("all assertions passed")


if __name__ == "__main__":
    validate()
