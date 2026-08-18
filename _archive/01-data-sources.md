# 01 — Data sources
*Phase 2: Data Understanding. Cap 500w.*

## Why not real advertiser data
Commercial media spend is not public. Meta's Ad Library exposes spend and
impression ranges **only for political and issue ads**; commercial ads carry no
spend field in either the API or the web UI. Third-party tools sell *estimates*,
not actuals. So a credible open MMM must use a recognized demo dataset or
simulated data. This is a genuine constraint of the domain, not a shortcut —
and it is stated up front rather than glossed over.

## Primary source

| | |
|---|---|
| **Dataset** | `dt_simulated_weekly` |
| **Owner** | Meta Marketing Science, shipped in the open-source Robyn package |
| **Obtained** | `raw.githubusercontent.com/facebookexperimental/Robyn/main/R/data/dt_simulated_weekly.RData` |
| **Licence** | MIT (Robyn repository) |
| **Grain** | One row per week, Monday-dated |
| **Coverage** | 2015-11-23 → 2019-11-11, **208 consecutive weeks, zero gaps** |
| **Refresh** | Static. It is a fixed demo asset, never updated |
| **Provenance caveat** | Simulated by Meta. True parameters are **not published**, so the real ROIs cannot be checked against an answer key |

**Note on secondary sources:** published write-ups describe this dataset as ~205
weeks beginning 2015-12-14. Direct inspection gives **208 weeks from
2015-11-23**. The primary file was trusted over the write-ups.

## Supporting source

| | |
|---|---|
| **Dataset** | `dt_prophet_holidays` |
| **Owner** | Same repository, derived from Prophet's holiday tables |
| **Grain** | One row per holiday per country per year |
| **Size** | 87,651 rows across 123 countries |
| **Use** | Holiday controls. Requires choosing a market — the demo convention is DE, which yields 37 holiday dates inside the modelling window |

## Ground-truth source (recovery check only)
A self-generated dataset with adstock, saturation and channel ROIs **set by us**,
used solely to confirm the pipeline recovers known parameters. Documented in
`06-model-card.md`. It never touches the reallocation recommendation.

## Access reproducibility
`src/01_load.R` downloads nothing at runtime — it reads `data/raw/` and writes
flat CSVs to `data/cached/`, asserting 208 rows, no missing values, and a
strictly 7-day date step. Raw files are committed because they total under 150KB.
