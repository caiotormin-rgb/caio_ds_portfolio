# 02 - Data Dictionary
*Step 02 of 09 | CRISP-DM Phase 2: Data Understanding | Audience: analyst and technical reviewer.*

This file defines the modeling table used by the MMM. The rejected Robyn
candidate data is discussed in `03-data-quality.md`; it is not the model input.

Status: work in progress. This dictionary documents the synthetic case-study
version of Caio's MMM project framework.

`data/simulated/model_frame.csv` has **208 rows x 17 columns**, one row per
Monday-starting week.

## Modeling Table

| Field | Type | Required | Definition | Example | Notes |
|---|---|---|---|---|---|
| `week` | date | yes | Week start, always Monday | `2021-01-04` | 208 consecutive weeks through `2024-12-23` |
| `revenue` | float | yes | Weekly revenue, USD | `3,165,277.96` | Outcome variable; total period revenue is 492,455,192 |
| `linear_tv_spend` | float | yes | Linear TV spend, USD | `95,372.58` | 12.6m total; 28% of spend; 45.7% of weeks dark |
| `meta_social_spend` | float | yes | Meta social spend, USD | `60,237.26` | 8.1m total; 18% of spend; 35.6% of weeks dark |
| `youtube_spend` | float | yes | YouTube spend, USD | `126,972.21` | 7.2m total; 16% of spend; 25.5% of weeks dark |
| `ctv_spend` | float | yes | CTV / streaming spend, USD | `30,989.70` | 6.3m total; 14% of spend; designed as under-funded |
| `search_brand_spend` | float | yes | Branded search spend, USD | `23,788.67` | 5.4m total; 12% of spend; designed with true effect of zero |
| `amazon_retail_spend` | float | yes | Amazon retail media spend, USD | `23,297.81` | 5.4m total; 12% of spend; Q4-loaded |
| `category_demand` | float | yes | External demand control | `0.076703` | Drives both revenue and media planning in the simulation |
| `holiday_count` | int | yes | Count of US federal holidays in the week | `1` | 46 weeks affected; maximum 2 |
| `holiday_retail_count` | int | yes | Count of retail-relevant holidays in the week | `0` | 25 weeks affected; maximum 2 |
| `sin1` | float | yes | First annual seasonality sine term | `0.0` | Smooth seasonal control |
| `cos1` | float | yes | First annual seasonality cosine term | `1.0` | Smooth seasonal control |
| `sin2` | float | yes | Second annual seasonality sine term | `0.0` | Smooth seasonal control |
| `cos2` | float | yes | Second annual seasonality cosine term | `1.0` | Smooth seasonal control |
| `trend` | float | yes | Linear time trend | `0.0` | Small positive trend over four years |
| `settled` | bool | yes | Whether late conversion reporting has settled | `True` | Final 6 weeks are excluded from model fitting |

## Paid Spend by Channel

| Channel | Field | Total | Share |
|---|---|---:|---:|
| Linear TV | `linear_tv_spend` | 12,600,000 | 28% |
| Meta social | `meta_social_spend` | 8,100,000 | 18% |
| YouTube | `youtube_spend` | 7,200,000 | 16% |
| CTV / streaming | `ctv_spend` | 6,300,000 | 14% |
| Branded search | `search_brand_spend` | 5,400,000 | 12% |
| Amazon retail media | `amazon_retail_spend` | 5,400,000 | 12% |
| **Total paid** | | **45,000,000** | **100%** |

## Fields Kept for Audit, Not Modeling

`data/simulated/modelling_table.csv` keeps platform diagnostics such as
impressions, reach, impression share, GRPs, and Amazon-reported sales. They are
useful for data-quality checks, but the model uses spend consistently across
all six paid channels.

## Next

Continue to `03-data-quality.md`.
