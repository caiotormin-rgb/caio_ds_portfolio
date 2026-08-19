"""Phase 3 — project the generated truth into six platform-shaped exports.

Each export mimics what a practitioner actually receives from that platform:
real field names, units, grains and week definitions, per
reference/platform-data-specs.md. Fourteen defects are planted deliberately;
they are documented in reference/dgp-spec.md and reviewed in notebooks/01_eda.ipynb.

Nothing here invents a field name. Where a spec was unverifiable (The Trade Desk,
Xandr) the platform was not used.

Writes data/simulated/exports/*
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TRUTH = ROOT / "data" / "simulated" / "truth"
OUT = ROOT / "data" / "simulated" / "exports"
SEED = 20260818

# unit economics per channel, from the researched benchmark ranges
CPM = {"linear_tv": 22.0, "meta_social": 19.5, "youtube": 12.0,
       "ctv": 32.0, "amazon_retail": 8.5}
CPC_SEARCH = 1.85


def daily_split(weekly_spend, weeks, rng):
    """Spread weekly spend over 7 days with realistic within-week variation."""
    rows = []
    for w, amt in zip(weeks, weekly_spend):
        if amt <= 0:
            continue                       # dark weeks produce no rows
        w7 = rng.dirichlet(np.ones(7) * 6)
        for i, frac in enumerate(w7):
            rows.append((w + pd.Timedelta(days=i), amt * frac))
    return pd.DataFrame(rows, columns=["date", "spend"])


def main():
    rng = np.random.default_rng(SEED + 7)
    OUT.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(TRUTH / "weekly_truth.csv", parse_dates=["week"])
    weeks = d.week
    planted = []

    # ---------------------------------------------------------------- 1. Google Ads: branded search
    # ratio ctr 0-1, cost in MICROS, fractional conversions, IS clipped at 0.0999
    sp = d.search_brand_spend.to_numpy()
    impr = np.where(sp > 0, (sp / CPC_SEARCH / 0.042).round(), 0).astype(int)
    clicks = np.where(sp > 0, (sp / CPC_SEARCH).round(), 0).astype(int)
    ctr = np.divide(clicks, impr, out=np.zeros_like(sp), where=impr > 0)
    # ~8% of weeks genuinely fall below the 0.1 reporting floor
    is_raw = np.where(rng.random(len(sp)) < 0.08,
                      rng.uniform(0.01, 0.099, len(sp)),
                      np.clip(rng.beta(7, 3, len(sp)), 0.10, 0.99))
    is_clipped = np.where(is_raw < 0.1, 0.0999, is_raw)            # DEFECT 6
    g = pd.DataFrame({
        "segments.week": weeks.dt.strftime("%Y-%m-%d"),
        "campaign.name": "BR | Brand | Exact",
        "metrics.impressions": impr,
        "metrics.clicks": clicks,
        "metrics.ctr": ctr.round(6),
        "metrics.cost_micros": (sp * 1e6).round().astype("int64"),  # DEFECT 2
        "metrics.conversions": (clicks * 0.081 * rng.uniform(.8, 1.2, len(sp))).round(4),  # DEFECT 7
        "metrics.search_impression_share": is_clipped.round(4),
    })
    g.to_csv(OUT / "google_ads_search_brand.csv", index=False)
    planted += [(2, "cost_micros unconverted", "google_ads_search_brand"),
                (6, "impression share clipped to 0.0999", "google_ads_search_brand"),
                (7, "fractional conversions", "google_ads_search_brand")]

    # ---------------------------------------------------------------- 2. Google Ads: YouTube video
    sp = d.youtube_spend.to_numpy()
    impr = np.where(sp > 0, (sp / CPM["youtube"] * 1000).round(), 0).astype(int)
    views = (impr * rng.uniform(.28, .36, len(sp))).round().astype(int)
    y = pd.DataFrame({
        "segments.week": weeks.dt.strftime("%Y-%m-%d"),
        "campaign.name": "US | YouTube | Video",
        "metrics.impressions": impr,
        "metrics.video_views": views,
        "metrics.video_view_rate": np.divide(views, impr, out=np.zeros_like(sp), where=impr > 0).round(6),
        "metrics.video_quartile_p25_rate": rng.uniform(.60, .70, len(sp)).round(4),
        "metrics.video_quartile_p50_rate": rng.uniform(.45, .55, len(sp)).round(4),
        "metrics.video_quartile_p75_rate": rng.uniform(.35, .45, len(sp)).round(4),
        "metrics.video_quartile_p100_rate": rng.uniform(.25, .35, len(sp)).round(4),
        "metrics.cost_micros": (sp * 1e6).round().astype("int64"),   # DEFECT 2
    })
    y.to_csv(OUT / "google_ads_youtube.csv", index=False)

    # ---------------------------------------------------------------- 3. Meta Ads Insights
    # DAILY rows, ctr as PERCENT 0-100, all numerics as STRINGS, reach non-additive,
    # last 2 weeks understated (28-day settling)
    sp = d.meta_social_spend.to_numpy()
    dd = daily_split(sp, weeks, rng)
    dd["impressions"] = (dd.spend / CPM["meta_social"] * 1000).round().astype(int)
    dd["reach"] = (dd.impressions / rng.uniform(1.15, 1.45, len(dd))).round().astype(int)
    dd["frequency"] = (dd.impressions / dd.reach).round(6)
    dd["clicks"] = (dd.impressions * rng.uniform(.008, .020, len(dd))).round().astype(int)
    dd["ctr"] = (dd.clicks / dd.impressions * 100).round(4)          # DEFECT 1: percent
    dd["cpm"] = (dd.spend / dd.impressions * 1000).round(4)
    last14 = dd.date > (weeks.max() - pd.Timedelta(days=14))
    dd.loc[last14, ["impressions", "reach", "clicks"]] = (
        dd.loc[last14, ["impressions", "reach", "clicks"]] * 0.72).round().astype(int)  # DEFECT 11
    meta = pd.DataFrame({
        "date_start": dd.date.dt.strftime("%Y-%m-%d"),
        "date_stop": dd.date.dt.strftime("%Y-%m-%d"),
        "publisher_platform": "instagram",
        "spend": dd.spend.round(2).astype(str),                       # DEFECT 3: strings
        "impressions": dd.impressions.astype(str),
        "reach": dd.reach.astype(str),
        "frequency": dd.frequency.astype(str),
        "clicks": dd.clicks.astype(str),
        "ctr": dd.ctr.astype(str),
        "cpm": dd.cpm.astype(str),
    })
    meta.to_json(OUT / "meta_ads_insights.json", orient="records", indent=1)
    planted += [(1, "ctr as percent 0-100", "meta"), (3, "numerics as JSON strings", "meta"),
                (4, "daily rows needing rollup", "meta"),
                (5, "reach non-additive across days", "meta"),
                (11, "last 2 weeks understated (settling)", "meta")]

    # ---------------------------------------------------------------- 4. DV360: CTV
    # display-name headers, decimal currency, blank line + misaligned Grand Total + footer,
    # reach in a SEPARATE file
    sp = d.ctv_spend.to_numpy()
    impr = np.where(sp > 0, (sp / CPM["ctv"] * 1000).round(), 0).astype(int)
    starts = (impr * rng.uniform(.97, .995, len(sp))).round().astype(int)
    comp = (starts * rng.uniform(.93, .98, len(sp))).round().astype(int)
    core = pd.DataFrame({
        "Date": weeks.dt.strftime("%Y/%m/%d"),
        "Insertion Order": "Q3 CTV Awareness",
        "Device Type": "Connected TV",
        "App/URL": "[Roku Channel - Roku (12)]",
        "Impressions": impr,
        "Clicks": (impr * rng.uniform(.0010, .0030, len(sp))).round().astype(int),
        "Revenue (Advertiser Currency)": sp.round(2),
        "Starts (Video)": starts,
        "Complete Views (Video)": comp,
        "Completion Rate (Video)": np.divide(comp, starts, out=np.zeros_like(sp), where=starts > 0).round(4),
    })
    core = core[impr > 0]
    dup = core.iloc[[37]]                                             # DEFECT 10
    core = pd.concat([core.iloc[:38], dup, core.iloc[38:]], ignore_index=True)
    lines = [",".join(core.columns)]
    lines += [",".join(str(v) for v in row) for row in core.itertuples(index=False)]
    lines += ["", ",,,,Grand Total," + ",".join(                      # DEFECT 12: misaligned
        str(core[c].sum()) for c in ["Impressions", "Clicks", "Revenue (Advertiser Currency)"])]
    lines += ["", "Report Date," + pd.Timestamp.now().strftime("%Y/%m/%d"),
              "Report Type,STANDARD", "Advertiser,Acme Inc"]
    (OUT / "dv360_ctv_standard.csv").write_text("\n".join(lines))
    # reach must be its own file — DV360 cannot return it in a STANDARD report
    rch = pd.DataFrame({
        "Date": weeks.dt.strftime("%Y/%m/%d")[impr > 0],
        "Unique Reach: Impression Reach": (impr[impr > 0] / rng.uniform(2.5, 4.5, (impr > 0).sum())).round().astype(int),
    })
    rch["Unique Reach: Average Impression Frequency"] = (
        impr[impr > 0] / rch["Unique Reach: Impression Reach"]).round(4)
    rch.to_csv(OUT / "dv360_ctv_reach.csv", index=False)
    planted += [(10, "duplicated row", "dv360"), (12, "misaligned Grand Total row", "dv360"),
                (13, "reach in a separate file", "dv360")]

    # ---------------------------------------------------------------- 5. Amazon Ads v3
    # DAILY, gzipped-JSON-shaped, v3 names, NO weekly grain, zero-activity rows OMITTED,
    # 42-day conversion restatement
    sp = d.amazon_retail_spend.to_numpy()
    ad = daily_split(sp, weeks, rng)
    ad["impressions"] = (ad.spend / CPM["amazon_retail"] * 1000).round().astype(int)
    ad["clicks"] = (ad.impressions * rng.uniform(.003, .006, len(ad))).round().astype(int)
    settle = np.where(ad.date > (weeks.max() - pd.Timedelta(days=42)), 0.63, 1.0)  # DEFECT 11b
    sales14 = ad.spend * rng.uniform(2.6, 4.2, len(ad)) * settle
    amz = pd.DataFrame({
        "date": ad.date.dt.strftime("%Y-%m-%d"),
        "campaignName": "SP | Brand Defense",
        "impressions": ad.impressions,
        "clicks": ad.clicks,
        "cost": ad.spend.round(2),
        "clickThroughRate": (ad.clicks / ad.impressions).round(6),
        "costPerClick": (ad.spend / ad.clicks.replace(0, np.nan)).round(4),
        "purchases14d": (sales14 / 48).round().astype(int),
        "sales14d": sales14.round(2),
        "unitsSoldClicks14d": (sales14 / 41).round().astype(int),
    })
    amz = amz[amz.impressions > 0]                                    # DEFECT 10b: rows omitted
    amz.to_json(OUT / "amazon_ads_sp.json", orient="records", indent=1)
    planted += [(4, "daily rows needing rollup", "amazon"),
                (10, "zero-activity rows omitted entirely", "amazon"),
                (11, "42-day conversion restatement", "amazon")]

    # ---------------------------------------------------------------- 6. Linear TV agency sheet
    # monthly invoice vs weekly airings, plus a currency-unit block
    sp = d.linear_tv_spend.to_numpy()
    tv = pd.DataFrame({"air_week": weeks.dt.strftime("%d/%m/%Y"),     # non-ISO, agency style
                       "daypart": rng.choice(["Prime", "Daytime", "Late"], len(sp)),
                       "grps": (sp / 4200).round(1),
                       "gross_cost": sp.round(2)})
    tv = tv[sp > 0].reset_index(drop=True)
    block = slice(60, 74)
    tv.loc[block, "gross_cost"] = (tv.loc[block, "gross_cost"] / 1000).round(4)  # DEFECT 9
    tv.to_csv(OUT / "tv_agency_airings.csv", index=False)
    inv = pd.DataFrame({"month": pd.to_datetime(weeks).dt.to_period("M").astype(str),
                        "invoiced": sp}).groupby("month", as_index=False).invoiced.sum()
    inv["invoiced"] = (inv.invoiced * rng.uniform(1.01, 1.04, len(inv))).round(2)  # DEFECT 8
    inv.to_csv(OUT / "tv_agency_invoices.csv", index=False)
    planted += [(8, "monthly invoice != sum of airings", "tv"),
                (9, "currency-unit block (14 rows /1000)", "tv")]

    (OUT / "_planted_defects.json").write_text(json.dumps(
        [{"id": i, "defect": t, "source": s} for i, t, s in planted], indent=2))

    print(f"wrote {len(list(OUT.glob('*')))} files to {OUT.relative_to(ROOT)}")
    for f in sorted(OUT.glob("*")):
        print(f"  {f.name:34s} {f.stat().st_size/1024:8.1f} KB")
    print(f"\nplanted defect instances: {len(planted)} across {len({s for _,_,s in planted})} sources")
    print("NOTE: defect 14 (week-boundary misalignment) is not planted in a file —")
    print("      it is introduced by the analyst if ingest uses pandas resample('W').")


if __name__ == "__main__":
    main()
