"""Phase 3 — feature construction.

Deliberately small. In MMM the transforms that look like feature engineering —
adstock and saturation — are NOT features: their parameters are estimated jointly
with the coefficients in Phase 4. Baking them in here would silently pre-commit
to a decay rate the model is supposed to learn, which `03` established the data
cannot tell us on its own.

So this builds only what is genuinely exogenous and fixed: calendar structure,
the control, and flags.

Writes data/simulated/model_frame.csv
"""
from pathlib import Path
import numpy as np
import pandas as pd
import holidays as H

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "simulated"

CHANNELS = ["linear_tv", "meta_social", "youtube", "ctv", "search_brand", "amazon_retail"]
RETAIL_HOLIDAYS = {"Thanksgiving Day", "Christmas Day", "Independence Day",
                   "Memorial Day", "Labor Day", "New Year's Day"}


def main():
    d = pd.read_csv(D / "modelling_table.csv", parse_dates=["week"])
    truth = pd.read_csv(D / "truth" / "weekly_truth.csv", parse_dates=["week"])
    f = pd.DataFrame({"week": d.week})

    # --- calendar: 2 Fourier harmonics, pre-committed in the analysis plan on a df argument
    t = np.arange(len(d))
    for k in (1, 2):
        f[f"sin{k}"] = np.sin(2 * np.pi * k * t / 52.18).round(6)
        f[f"cos{k}"] = np.cos(2 * np.pi * k * t / 52.18).round(6)
    f["trend"] = (t / 52.18).round(4)

    # --- holidays: COUNT, not flags. Four weeks carry two holidays and a binary
    #     flag would discard that. Retail-relevant subset kept separately.
    cal = H.country_holidays("US", years=sorted(d.week.dt.year.unique()))
    counts, retail = [], []
    for w in d.week:
        names = {n.replace(" (observed)", "")
                 for dt, n in cal.items() if w.date() <= dt <= (w + pd.Timedelta(days=6)).date()}
        counts.append(len(names))
        retail.append(len(names & RETAIL_HOLIDAYS))
    f["holiday_count"] = counts
    f["holiday_retail_count"] = retail

    # --- control (D10: the model is fit both with and without this)
    f["category_demand"] = truth.category_demand.round(6)

    # --- media: RAW SPEND ONLY. Adstock and saturation are Phase 4 parameters.
    for c in CHANNELS:
        f[f"{c}_spend"] = d[f"{c}_spend"].round(2)

    # --- outcome and the settled flag
    f["revenue"] = d.revenue.round(2)
    f["settled"] = d.settled

    # exposure columns are diagnostics only (D11) and are NOT carried into the
    # model frame. They stay in modelling_table.csv for the readout.

    assert f.notna().all().all(), "model frame must have no missing values"
    assert (f.week.dt.weekday == 0).all() and f.week.is_unique
    f.to_csv(D / "model_frame.csv", index=False)

    print(f"model_frame.csv — {f.shape[0]} rows x {f.shape[1]} cols, no missing values\n")
    print("features built:")
    print(f"  calendar   : sin1 cos1 sin2 cos2 trend            (5)")
    print(f"  holidays   : holiday_count, holiday_retail_count  (2)  "
          f"— {int((f.holiday_count>1).sum())} weeks carry 2+, which a binary flag would lose")
    print(f"  control    : category_demand                      (1)  — D10 fits both ways")
    print(f"  media      : {len(CHANNELS)} raw spend columns              ({len(CHANNELS)})")
    print(f"  outcome    : revenue, settled                     (2)")
    print()
    print("NOT built, deliberately:")
    print("  adstock / saturation  -> Phase 4. Parameters are estimated, not assumed.")
    print("  exposure & CPM        -> diagnostics only (D11); undefined in dark weeks by nature.")
    print("  impression share      -> dropped. 13 censored weeks in a non-model variable.")
    print(f"  settled: {int((~f.settled).sum())} unsettled weeks flagged, rows retained.")


if __name__ == "__main__":
    main()
