# LAB12 — Stage 11 Generalization Diagnostics

## 1. Generalization Gap

`Gap = MAE_external - MAE_development_CV`. M04-T003: +799.29 USD (+14.1%).
M05-T000: +773.04 USD (+13.3%). Both candidates show a similar, moderate gap.

**Confounding factors (gap is NOT attributed solely to overfitting):**
- Different years (2006-2013 pooled/CV vs a single 2014 year) -- different
  seasonal/economic composition.
- Different training sample size per fit (CV fold training subsets vs the full
  4987-row development population used for the external-validation refit).
- Selection/tuning exposure: both candidates were chosen via development-CV
  performance, so part of the dev-CV number reflects selection optimism that an
  unseen year will not reproduce.
- Temporal shift: 2014 may differ structurally from 2006-2013 in ways unrelated to
  model fit quality.

## 2. Covariate Shift — Numerical Features

| Feature | Dev Median | 2014 Median | Dev P90 | 2014 P90 |
|---|---|---|---|---|
| Line_Item_Qty_Sum | 5,478.00 | 9,575.00 | 75,000.00 | 90,000.00 |
| Line_Item_Value_Sum | 74,200.00 | 86,481.72 | 587,767.75 | 723,799.72 |

**A real, non-trivial upward shift is present**: 2014's median shipment quantity is
~75% higher, and median shipment value ~17% higher, than the development period's.
P90 values are also higher on both features. This is consistent with 2014 shipments
trending toward larger/higher-value loads than the 2006-2013 pool, and is a
plausible partial explanation (among several, see Section 1) for the observed
generalization gap -- documented here as risk/monitoring information, not acted on
via retuning.

## 3. Missingness Drift

`Shipment_Mode` missingness: Development=4.23%, 2014=0.00% -- a real, measured
reduction in missingness for this one categorical feature. All other features show
0% missingness in both periods (see `stage11_missingness_drift.csv`).

## 4. Categorical / New-Category Drift

| Feature | Dev Cardinality | 2014 Cardinality | New Categories | New-Category Rate |
|---|---|---|---|---|
| Shipment_Mode | 4 | 4 | 0 | 0.0% |
| INCO_Term | 8 | 4 | 0 | 0.0% |
| Country | 37 | 22 | 0 | 0.0% |
| Product_Group | 5 | 3 | 0 | 0.0% |

**No new categories appeared in 2014 for any categorical feature** -- the
`OneHotEncoder(handle_unknown="ignore")` contract was never actually exercised for
an unseen category in this validation run. Notably, 2014's observed cardinality is
**narrower** than development's for INCO_Term (4 vs 8), Country (22 vs 37), and
Product_Group (3 vs 5) -- 2014 shipments concentrate on a subset of the categories
seen historically, rather than introducing new ones.

## 5. Label Coverage Shift

| Period | Total | Eligible | Coverage Rate |
|---|---|---|---|
| Development (2006-2013) | 5551 | 4987 | 89.8% |
| External Validation (2014) | 910 | 819 | 90.0% |

Label coverage is **stable** across time (89.8% vs 90.0%) -- this reduces, but does
not eliminate, the missing-not-at-random concern first raised in Stage 05-06 (the
mechanism generating missing/non-numeric `Freight Cost` values is still unknown).

## 6. Tail Risk / High-Cost Behavior

Both ML candidates reduce high-cost underprediction from the baselines' 100% to
89.93% on 2014 -- an **independent replication** of the Stage 08-10 finding, not a
re-derivation from the same data.

## 7. Error Concentration (Advanced Challenge 3)

See `stage11_error_concentration.csv` for top-1%/top-5% MAE and squared-error
contribution per model. Squared-error contribution from the top error percentiles
is consistently larger than MAE contribution, illustrating empirically why RMSE is
more outlier-sensitive than MAE on this data.

## 8. Interpretation Boundary

All findings in this document are **descriptive risk documentation and monitoring
design inputs**. None were used to retune hyperparameters, reselect features, alter
preprocessing, or change target transformation in Stage 11.
