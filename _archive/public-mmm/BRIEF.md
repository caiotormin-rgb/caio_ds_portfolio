# Diminishing Returns on Public Money
*(the flagship — the one that gets you the interview)*

**ONE MESSAGE (locked):**
> Public budgets behave like media budgets: spending has carryover and
> saturation. Modeled that way, municipal [health] spending shows diminishing
> returns past roughly R$X per capita — and a reallocation of the same total
> budget predicts a better outcome.

**Sells:** MMM, budget allocation, carryover/adstock, saturation curves,
multi-source data joining. This is the unique angle: nobody applies MMM to
public spending. That is the whole point of the project.

## AUDIENCE + DECISION  *(draft — Caio's call)*
**Who acts on this:** a state health secretariat or a municipal budget office
allocating next year's envelope across categories.
**What they do differently:** shift marginal spend away from saturated
categories toward ones still on the steep part of the curve. Same total budget.
**Layer 1 sentence they must leave with:** "Moving R$X from A to B predicts
[outcome improvement], at no extra cost."

## Data
- SICONFI / FINBRA municipal spending by function. Free REST API, no auth:
  http://apidatalake.tesouro.gov.br/docs/siconfi/
- Outcome: DATASUS (health) or IDEB (education). **Pick ONE at step 0.**
- IBGE: population, GDP per capita — controls and normalizers.

## Method (do not exceed)
- Panel of municipalities x years.
- Geometric adstock on spending (carryover — public money pays off with a lag).
- Hill / log saturation transform.
- Regression with municipality + year fixed effects. Controls: GDP pc, population.
- Response curve per spending category -> reallocation scenario.

## Honesty requirement
Richer municipalities both spend more and have better outcomes. State this
limitation plainly in the writeup. Frame the output as a **budget-allocation
model with diminishing returns**, not a causal claim. Owning this limitation is
a hiring signal, not a weakness.

## Chart budget: 5
1. Saturation curve — spend per capita vs outcome, with the knee marked.
2. Carryover — how many years spending keeps paying off.
3. Where each municipality sits on the curve (over/under-invested).
4. Reallocation scenario — same money, modeled outcome.
5. Model fit / limitation chart.

## OUT OF SCOPE — do not build
- Bayesian MMM (PyMC-Marketing, LightweightMMM). Frequentist panel is enough.
  If it truly needs to be Bayesian, that's version 2, after v1 ships.
- All 5,570 municipalities if a clean subset works. Start with one state.
- More than one outcome variable.
- A dashboard.

## DONE WHEN
- [ ] Outcome variable chosen and defended in one paragraph
- [ ] Adstock + saturation params reported in a small table
- [ ] 5 charts
- [ ] Writeup with the reallocation number in the first paragraph
- [ ] Limitations section written before the charts are polished
