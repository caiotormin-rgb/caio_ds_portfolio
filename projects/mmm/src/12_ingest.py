"""Phase 3 — reconcile six platform exports into one weekly modelling table.

Each source arrives in its own shape: different units, grains, week definitions,
and two with no API at all. This is the phase, and per industry practice it is
roughly 60% of a real MMM engagement.

Every defect found is logged with what was detected and what was done about it.
Detection is reported honestly, including anything missed.

Writes:
  data/simulated/modelling_table.csv
  data/simulated/ingest_report.json
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "data" / "simulated" / "exports"
TRUTH = ROOT / "data" / "simulated" / "truth"
OUT = ROOT / "data" / "simulated"

log = []


def found(defect_id, source, detected, action):
    log.append(dict(defect=defect_id, source=source, detected=detected, action=action))
    print(f"  [{defect_id:>2}] {source:<12} {detected}")


def to_monday(dates):
    """Week start, Monday. Derived in ONE place.

    Never pandas.resample("W") — it defaults to Sunday-ending, which would
    misalign every daily source against Google Ads' Monday weeks by one day.
    That is defect 14, and it is introduced by the analyst, not the source.
    """
    dates = pd.to_datetime(dates)
    return dates - pd.to_timedelta(dates.dt.weekday, unit="D")


def main():
    print("INGEST — detection log\n")
    weeks = pd.to_datetime(pd.read_csv(TRUTH / "weekly_truth.csv").week)
    grid = pd.DataFrame({"week": weeks})

    # ---------------------------------------------------------------- Google Ads: search
    g = pd.read_csv(EXPORTS / "google_ads_search_brand.csv")
    g["week"] = pd.to_datetime(g["segments.week"])
    assert (g.week.dt.weekday == 0).all(), "Google Ads weeks should already be Monday"
    found(2, "google/search", f"cost in micros (max {g['metrics.cost_micros'].max():,})",
          "divided by 1e6")
    g["search_brand_spend"] = g["metrics.cost_micros"] / 1e6
    if (g["metrics.ctr"] <= 1).all():
        found(1, "google/search", f"ctr is a ratio (max {g['metrics.ctr'].max():.4f})",
              "kept as ratio; this is the reference scale")
    n_sent = int((g["metrics.search_impression_share"] == 0.0999).sum())
    found(6, "google/search", f"{n_sent} weeks at the 0.0999 impression-share sentinel",
          "treated as left-censored (<0.1), not as a value")
    g["search_is_censored"] = g["metrics.search_impression_share"] == 0.0999
    g["search_impression_share"] = g["metrics.search_impression_share"].mask(g.search_is_censored)
    n_frac = int((g["metrics.conversions"] % 1 != 0).sum())
    found(7, "google/search", f"{n_frac}/{len(g)} conversions are fractional",
          "kept as float — integer casting would be the bug")

    # ---------------------------------------------------------------- Google Ads: YouTube
    y = pd.read_csv(EXPORTS / "google_ads_youtube.csv")
    y["week"] = pd.to_datetime(y["segments.week"])
    y["youtube_spend"] = y["metrics.cost_micros"] / 1e6
    q = ["metrics.video_quartile_p25_rate", "metrics.video_quartile_p50_rate",
         "metrics.video_quartile_p75_rate", "metrics.video_quartile_p100_rate"]
    assert (y[q].diff(axis=1).iloc[:, 1:] <= 0).all().all(), "quartile rates must be non-increasing"

    # ---------------------------------------------------------------- Meta
    # Inspect the RAW text, not the parsed frame. pandas.read_json silently
    # coerces quoted numerics, so a dtype check on the DataFrame reports nothing
    # and the defect passes unnoticed. This one has to be caught at the file.
    raw_meta = json.loads((EXPORTS / "meta_ads_insights.json").read_text())
    quoted = [k for k, val in raw_meta[0].items()
              if isinstance(val, str) and k not in ("date_start", "date_stop", "publisher_platform")]
    found(3, "meta", f"{len(quoted)} numeric fields quoted as strings in the file "
                     f"({', '.join(quoted[:4])}...) — pandas coerces these silently on read",
          "detected at the file, then cast explicitly")
    m = pd.read_json(EXPORTS / "meta_ads_insights.json", dtype=False)
    for c in ["spend", "impressions", "reach", "frequency", "clicks", "ctr", "cpm"]:
        m[c] = pd.to_numeric(m[c])
    found(4, "meta", f"{len(m)} DAILY rows, no weekly increment exists",
          "rolled up to Monday weeks")
    if m.ctr.max() > 1:
        found(1, "meta", f"ctr on a 0-100 percent scale (max {m.ctr.max():.2f}) "
                         f"vs Google's ratio", "divided by 100 to match")
        m["ctr"] = m.ctr / 100
    m["week"] = to_monday(m.date_start)
    mw = m.groupby("week").agg(meta_social_spend=("spend", "sum"),
                               meta_impressions=("impressions", "sum"),
                               meta_clicks=("clicks", "sum"),
                               meta_reach_daily_sum=("reach", "sum")).reset_index()
    mw["meta_ctr"] = mw.meta_clicks / mw.meta_impressions          # recomputed, not averaged
    found(5, "meta", "reach is set cardinality — summing daily overstates weekly",
          "daily sum retained ONLY as a diagnostic, never used as a model input")
    tail = mw.week > (mw.week.max() - pd.Timedelta(days=28))
    found(11, "meta", f"last {int(tail.sum())} weeks understated (28-day settling)",
          "flagged via `settled` column; rows kept, decision deferred to modelling")

    # ---------------------------------------------------------------- DV360
    raw = (EXPORTS / "dv360_ctv_standard.csv").read_text().splitlines()
    cut = next(i for i, l in enumerate(raw) if l.strip() == "")
    found(12, "dv360", f"data ends at line {cut}; a misaligned 'Grand Total' row and "
                       f"metadata footer follow", "truncated at the first blank line")
    from io import StringIO
    v = pd.read_csv(StringIO("\n".join(raw[:cut])))
    v["week"] = pd.to_datetime(v["Date"], format="%Y/%m/%d")
    n_dup = int(v.duplicated(subset=["week"]).sum())
    found(10, "dv360", f"{n_dup} duplicated week row(s)", "dropped, keeping first")
    v = v.drop_duplicates(subset=["week"], keep="first")
    assert (v["Complete Views (Video)"] <= v["Starts (Video)"]).all()
    found(13, "dv360", "reach absent — STANDARD reports cannot carry it",
          "read from the separate REACH export and joined")
    vr = pd.read_csv(EXPORTS / "dv360_ctv_reach.csv")
    vr["week"] = pd.to_datetime(vr["Date"], format="%Y/%m/%d")
    v = v.merge(vr[["week", "Unique Reach: Impression Reach"]], on="week", how="left")
    v = v.rename(columns={"Revenue (Advertiser Currency)": "ctv_spend",
                          "Impressions": "ctv_impressions",
                          "Unique Reach: Impression Reach": "ctv_reach"})

    # ---------------------------------------------------------------- Amazon
    a = pd.read_json(EXPORTS / "amazon_ads_sp.json", dtype=False)
    a["week"] = to_monday(a.date)
    found(10, "amazon", f"{len(a)} daily rows against {len(weeks)*7} possible — "
                        f"zero-activity rows omitted entirely",
          "reindexed to the full week grid and filled with 0; absence != missing")
    aw = a.groupby("week").agg(amazon_retail_spend=("cost", "sum"),
                               amazon_impressions=("impressions", "sum"),
                               amazon_sales14d=("sales14d", "sum")).reset_index()
    found(11, "amazon", "conversions restate for 42 days after the interaction",
          "final 6 weeks flagged unsettled via `settled` column")

    # ---------------------------------------------------------------- TV agency
    tv = pd.read_csv(EXPORTS / "tv_agency_airings.csv")
    tv["week"] = pd.to_datetime(tv.air_week, format="%d/%m/%Y")
    med = tv.gross_cost.median()
    odd = tv.gross_cost < med / 100
    found(9, "tv/sheet", f"{int(odd.sum())} rows with cost ~1000x below the median "
                         f"({tv.loc[odd,'gross_cost'].max():.1f} vs median {med:,.0f})",
          "rescaled by 1000; detected by magnitude break, not by trust")
    tv.loc[odd, "gross_cost"] = tv.loc[odd, "gross_cost"] * 1000
    tvw = tv.groupby("week").agg(linear_tv_spend=("gross_cost", "sum"),
                                 tv_grps=("grps", "sum")).reset_index()
    inv = pd.read_csv(EXPORTS / "tv_agency_invoices.csv")
    inv_total, air_total = inv.invoiced.sum(), tvw.linear_tv_spend.sum()
    found(8, "tv/sheet", f"invoice total {inv_total:,.0f} vs airings {air_total:,.0f} "
                         f"({(inv_total/air_total-1):+.1%})",
          "airings used as the spend series; residual reported, not absorbed")

    # ---------------------------------------------------------------- assemble
    out = grid.copy()
    for frame, cols in [(g, ["search_brand_spend", "search_impression_share", "search_is_censored"]),
                        (y, ["youtube_spend"]),
                        (mw, ["meta_social_spend", "meta_impressions", "meta_ctr", "meta_reach_daily_sum"]),
                        (v, ["ctv_spend", "ctv_impressions", "ctv_reach"]),
                        (aw, ["amazon_retail_spend", "amazon_impressions", "amazon_sales14d"]),
                        (tvw, ["linear_tv_spend", "tv_grps"])]:
        out = out.merge(frame[["week"] + cols], on="week", how="left")

    spend_cols = [c for c in out.columns if c.endswith("_spend")]
    n_filled = int(out[spend_cols].isna().sum().sum())
    out[spend_cols] = out[spend_cols].fillna(0.0)
    found(10, "all", f"{n_filled} missing spend cells after the join (dark weeks + omitted rows)",
          "filled with 0 explicitly — a dark week is zero spend, not missing data")

    # defect 14: prove every source landed on the same Monday grid
    assert (out.week.dt.weekday == 0).all()
    assert out.week.is_unique and len(out) == len(weeks)
    found(14, "pipeline", "all six sources reconciled onto one Monday week index",
          "week derived in a single function; pandas.resample('W') never used")

    truth = pd.read_csv(TRUTH / "weekly_truth.csv", parse_dates=["week"])
    out["revenue"] = truth.revenue.values
    out["settled"] = out.week <= (out.week.max() - pd.Timedelta(days=42))

    # ---------------------------------------------------------------- reconcile
    print("\nRECONCILIATION vs generating truth")
    recon = []
    for ch in ["linear_tv", "meta_social", "youtube", "ctv", "search_brand", "amazon_retail"]:
        got, exp = out[f"{ch}_spend"].sum(), truth[f"{ch}_spend"].sum()
        d = (got - exp) / exp
        recon.append(dict(channel=ch, ingested=float(got), truth=float(exp), rel_diff=float(d)))
        flag = "OK" if abs(d) < 0.005 else "CHECK"
        print(f"  {ch:15s} {got:>14,.0f} vs {exp:>14,.0f}  {d:+7.3%}  {flag}")

    OUT.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT / "modelling_table.csv", index=False)
    (OUT / "ingest_report.json").write_text(json.dumps(
        dict(detections=log, reconciliation=recon,
             rows=len(out), columns=list(out.columns)), indent=2))
    print(f"\nwrote modelling_table.csv — {len(out)} rows x {len(out.columns)} cols")
    print(f"detections logged: {len(log)}")


if __name__ == "__main__":
    main()
