# Parking lot

Ideas that are good but NOT now. Nothing here gets built until a project is DONE.

| Date | Project | Idea |
|------|---------|------|
| 2026-08-17 | mmm | MMM vs. last-click attribution: simulate known ground truth, show how far each lands from it. Strong — covers attribution too. Considered and deferred at Phase 1. |
| 2026-08-17 | mmm | MMM calibrated with a geo incrementality experiment as a prior (Meridian supports this). Very current. |
| 2026-08-17 | mmm | "Where does MMM break" stress-test: recovery under collinearity, short history, omitted channel. Possibly Track B. |
| 2026-08-17 | mmm | `mutinex/mmm-eval` — evaluation framework for MMMs, 29 stars, actively maintained. Possible input to Phase 5 evaluation. Not now. |
| 2026-08-17 | portfolio | `shakostats/Awesome-Marketing-Science` — curated marketing-science resource list, incl. geo incrementality. Reading, not building. |
| 2026-08-17 | mmm | Meridian's `Meridian_MLflow_Demo` — experiment tracking. Only if the project ever needs run management. |
| 2026-08-18 | mmm | Branded/non-branded paid search channel. Blocked structurally: Google's `conversions` was generated with no search channel, so a simulated one has zero recoverable effect. Revisit **only** when real data replaces the Meridian simulation. Option (a) — injecting an effect into a `conversions_augmented` column — was considered and rejected at D7. |
| 2026-08-18 | mmm | Meridian `_rf` files carry real `Channel3_reach` / `Channel3_frequency`. If reach ever becomes more than a diagnostic, borrow that schema rather than extending our simulation. |
| 2026-08-18 | mmm v2 | **`case_study_data.csv`** — real US retailer, 209 wks, **13 named channels**, $491M media / $22.6B sales, 2014-2018. Ships in [sibylhe/mmm_stan](https://github.com/sibylhe/mmm_stan) (MIT) and pymc-marketing `data/`. Fixes Robyn's two worst problems: seasonality only 43.7% of variance (vs 80.7%), worst control correlation 0.221 (vs 0.92), media incremental R² +4.4pp (vs +2.6pp). **Costs:** no flighting (0-3.3% dark weeks), no ground truth, and `mdip_sem` is clicks not impressions. Rejected at D12 on scope, not merit. |
| 2026-08-18 | separate project | **AMSS** ([google/amss](https://github.com/google/amss), Apache-2.0, Zhang & Vaver 2017) — population-state simulator giving **true incremental ROAS via counterfactual re-simulation** (budget zeroed), not contribution/spend. Adstock and saturation are *emergent* from consumer state migration, so fitting Hill is genuinely misspecified — the honest recovery test. **R only.** Pair with Chan & Perry §5.6's difficulty ladder: sweep carryover length and channel correlation, report where recovery degrades. This is the parked "where does MMM break" project, now with a concrete method. |
| 2026-08-18 | mmm | [`mmm-eval`](https://github.com/mutinex/mmm-eval) placebo + perturbation tests — shuffle a channel's rows (ROI should go to ~zero), add noise to spend (ROI should move <5%). **Need no ground truth, work on real data.** Cheap addition to `07-evaluation.md` if wanted later. |
| 2026-08-18 | settled negative | No real advertiser has ever released MMM data. Zenodo, OSF, Harvard Dataverse and journal replication policies all checked. IRI/Circana needs NDA + $1,000 and covers ads for 2 of 30 categories; Dominick's has zero media channels; Kaggle sets have no licence or provenance. Do not re-research this. |
