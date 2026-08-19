"""Phase 2 — ingest and validate the modelling dataset.

Run directly to assert every integrity property this project relies on:
    python src/01_load.py

Import the loaders from a notebook:
    import importlib.util
    spec = importlib.util.spec_from_file_location("mmm", "../src/01_load.py")
    mmm = importlib.util.module_from_spec(spec); spec.loader.exec_module(mmm)
    df = mmm.weekly()

SOURCE: Robyn's `dt_simulated_weekly`, converted once to CSV with `pyreadr`.
No R is involved anywhere — the RData was read in Python and the artefact
deleted. See 05-analysis-plan.md D8 for why this replaced the Meridian sample.

`data/audit/` holds the rejected Meridian candidates. They are evidence for the
data-readiness assessment in `01`/`03`, not modelling inputs.
"""
from pathlib import Path
import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
WEEKLY = RAW / "robyn_simulated_weekly.csv"
HOLIDAYS = RAW / "robyn_prophet_holidays.csv"

# Robyn's suffix convention: _S = spend, _I = impressions, _P = clicks,
# _B = baseline/context. Channels are NAMED here — no labelling convention needed.
SPEND = ["tv_S", "ooh_S", "print_S", "facebook_S", "search_S"]
EXPOSURE = {"facebook_S": "facebook_I", "search_S": "search_clicks_P"}
ORGANIC = ["newsletter"]
CONTROLS = ["competitor_sales_B", "events"]
OUTCOME = "revenue"

CHANNEL_LABEL = {
    "tv_S": "TV", "ooh_S": "Out-of-home", "print_S": "Print",
    "facebook_S": "Facebook", "search_S": "Paid search",
}


def weekly() -> pd.DataFrame:
    df = pd.read_csv(WEEKLY, parse_dates=["DATE"]).sort_values("DATE")
    return df.reset_index(drop=True)


def holidays(country: str | None = None) -> pd.DataFrame:
    df = pd.read_csv(HOLIDAYS, parse_dates=["ds"])
    return df[df.country == country].reset_index(drop=True) if country else df


def validate() -> None:
    d = weekly()

    # --- shape and regularity -------------------------------------------------
    assert len(d) == 208, f"expected 208 weeks, got {len(d)}"
    assert d.DATE.is_unique, "duplicate weeks"
    assert (d.DATE.diff().dropna().dt.days == 7).all(), "irregular weekly spacing"
    assert set(d.DATE.dt.day_name()) == {"Monday"}, "weeks are not Monday-dated"
    assert not d.isna().any().any(), "missing values"

    # --- expected columns -----------------------------------------------------
    for col in SPEND + list(EXPOSURE.values()) + ORGANIC + CONTROLS + [OUTCOME]:
        assert col in d.columns, f"missing column {col}"

    # --- value sanity ---------------------------------------------------------
    assert (d[SPEND] >= 0).all().all(), "negative spend"
    assert (d[OUTCOME] > 0).all(), "non-positive revenue"
    assert (d.newsletter > 0).all(), "non-positive newsletter volume"

    # --- the properties that made us choose this dataset ----------------------
    # If these ever stop holding, the identification argument in 01/03 is void.
    flighted = sum((d[c] == 0).mean() > 0.20 for c in SPEND)
    assert flighted >= 4, f"expected >=4 flighted channels, got {flighted}"
    mm = d.groupby(d.DATE.dt.month)[OUTCOME].mean()
    assert mm.max() / mm.min() > 3.0, "seasonality weaker than expected"

    h = holidays()
    assert len(h) == 87_651 and h.country.nunique() == 123

    print(f"weekly   : {len(d)} weeks, {d.DATE.min():%Y-%m-%d} to {d.DATE.max():%Y-%m-%d}")
    print(f"channels : {', '.join(CHANNEL_LABEL[c] for c in SPEND)}")
    print(f"flighted : {flighted}/5 channels dark >20% of weeks "
          f"({', '.join(f'{CHANNEL_LABEL[c]} {(d[c] == 0).mean():.0%}' for c in SPEND)})")
    print(f"season   : {mm.max() / mm.min():.2f}x month peak/trough")
    print(f"spend    : {d[SPEND].sum().sum():,.0f} | revenue {d[OUTCOME].sum():,.0f} "
          f"| ratio {d[SPEND].sum().sum() / d[OUTCOME].sum():.1%}")
    print(f"holidays : {len(h):,} rows, {h.country.nunique()} countries")
    print("all assertions passed")


if __name__ == "__main__":
    validate()
