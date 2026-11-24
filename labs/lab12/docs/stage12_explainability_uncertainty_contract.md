# LAB12 — Stage 12 Explainability & Uncertainty Contract

**Bu belge Stage 12 implementasyonu DEGILDIR -- yalnizca bir sonraki asamanin
sozlesmesidir.**

## 1. Dataset Fingerprint

SHA-256: `9cffdb4ab8c6135b0f999c91b3a5c6e88a3c3dfc28c7c85feb9e97f986e3578a`.
Stage 05 protocol fingerprint recompute: matches frozen value.

## 2. Selected Candidate

**Primary:** M04-T003 (ExtraTrees) -- Accepted for Stage 12, External MAE=6485.63
USD (2014). **Alternative:** M05-T000 (XGBoost) -- retained as secondary comparison,
External MAE=6591.33 USD.

## 3. Frozen Configuration

M04-T003: `{n_estimators=200, min_samples_split=10, min_samples_leaf=2,
max_features=0.8, max_depth=12, bootstrap=False, random_state=42, n_jobs=2}`.
M05-T000: `{n_estimators=200, max_depth=5, learning_rate=0.05, subsample=0.8,
colsample_bytree=0.8, reg_lambda=1.0, tree_method="hist", random_state=42,
n_jobs=2}`. Both refit on the full eligible development population (N=4987,
2006-2013) -- not fold-level fits.

## 4. Approved Feature Set

Stage 07 Minimal Core: numeric=`[Line_Item_Qty_Sum, Line_Item_Value_Sum]`,
categorical=`[Shipment_Mode, INCO_Term, Country, Product_Group]`. Preprocessing:
median imputation (numeric), constant-fill + rare-category OneHot (categorical,
`min_frequency=10`), no scaling.

## 5. Explainability Requirements

- Stage 12 should prioritize **M04-T003 (ExtraTrees)** for global and local
  explainability (e.g., feature importance, SHAP) as the accepted Primary
  candidate.
- M05-T000 (XGBoost) should be included as a **secondary comparison** given its
  external MAE is close to M04-T003's and within the latter's bootstrap resampling
  variability band -- explainability differences between the two may themselves be
  informative.
- Explainability analysis is explicitly **out of scope for Stage 11** and was not
  performed here (no SHAP, no permutation importance beyond what Stage 07 already
  established on the feature-selection question).

## 6. Uncertainty Evaluation Requirements

- Stage 12 uncertainty/calibration work must **not** use 2014 external validation
  labels as a calibration-fitting set -- doing so would retroactively compromise
  their role as an independent evaluation period for Stage 11.
- Use training-period (2006-2013) OOF residuals, or a properly time-isolated
  development subset, for any calibration fitting.
- Any prediction interval / conformal prediction method introduced in Stage 12
  should be validated against the already-observed error distributions in
  `stage11_external_predictions.csv` and `stage11_segment_error_analysis.csv`
  (diagnostic use only, not refitting those distributions into new training
  targets).

## 7. Calibration Data Policy

2014 labels: diagnostic/evaluation use only in Stage 12 (e.g., checking whether a
new calibration method's predicted intervals contain the already-known 2014
actuals), **never** as calibration-fitting input. 2015 Protected Test remains fully
unopened.

## 8. Protected Test Isolation

2015 records must remain unopened until Stage 14 -- no target parsing, aggregation,
analysis, predictions, or metrics of any kind.

## 9. Reproducibility Carryforward

M05-T000 (XGBoost) shows thread-dependent, cross-environment prediction variation
of up to $9,338 per shipment (aggregate MAE nearly unaffected, ~0.10%). Stage 12
explainability outputs for M05-T000 (e.g., SHAP values) should be expected to carry
a similar cross-environment instability and should be computed/reported from a
single, clearly-identified environment rather than averaged across environments.

## 10. Known Risks Passed Forward

1. High-cost shipment underprediction (~89.9%, both candidates) -- Stage 12
   uncertainty estimates should be checked for whether they appropriately widen for
   this segment.
2. ~10% label coverage gap of unknown mechanism (missing-not-at-random risk).
3. Single external validation year -- M05-T000's MAE is statistically close to
   M04-T003's under bootstrap resampling; Stage 12 should not treat the Primary
   candidate's superiority as definitively proven.
4. Observed covariate shift (2014 shipments trend larger/higher-value than
   development).

## 11. Stage 12 Entry Criteria

**GO.** Primary candidate accepted with documented external validation evidence;
Alternative retained; no business-SLA claim made; 2015 Protected Test untouched;
reproducibility and risk findings documented for explainability/uncertainty design.
