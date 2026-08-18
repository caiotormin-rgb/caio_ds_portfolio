# How Pix Ate Brazil

**ONE MESSAGE (locked):**
> Pix adoption was not one S-curve. It was several, with different inflection
> points by age and region — and the last segments to adopt did it for a
> different reason than the first.

*(Refine the second clause once you see the data. The shape of the claim stays.)*

**Sells:** product adoption, user behavior metrics, cohort analysis, demographics.

## AUDIENCE + DECISION  *(draft — Caio's call)*
**Who acts on this:** a product/growth lead at a fintech or a bank deciding
which segment to build for next.
**What they do differently:** stop treating late-adopting segments as low-value.
If they adopted late but behave differently, they're an underserved product need,
not a lost cause.
**Layer 1 sentence they must leave with:** _(one sentence, one number — fill in
once the data is pulled)_

## Data
- BCB open data — Pix transaction statistics, monthly, by municipality, age band,
  payer type, initiation method. https://dadosabertos.bcb.gov.br/dataset/pix
- IBGE municipal population + income for per-capita normalization.

## Method (do not exceed)
- Adoption rate per segment = users or transactions / eligible population.
- Fit a logistic / Bass curve per segment. Extract inflection date + ceiling.
- Compare inflection dates across segments. That comparison IS the finding.

## Chart budget: 4
1. The headline: overlaid adoption curves by segment, inflections marked.
2. Map — inflection date by state or municipality.
3. Behavior shift — what late adopters do differently (ticket size, P2P vs merchant).
4. One "so what" chart for a decision maker.

## OUT OF SCOPE — do not build
- Forecasting future Pix volume.
- Any ML model. There is no prediction task here.
- Fraud, PIX keys, DICT data, other payment rails.
- More than 4 charts.

## DONE WHEN
- [ ] Data pull is one reproducible script
- [ ] 4 charts, consistent styling
- [ ] A 500-word writeup opening with the ONE MESSAGE
- [ ] Published as a page a recruiter can read in 3 minutes
