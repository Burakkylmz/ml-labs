# LAB 08 — Feature Engineering, Feature Selection & Explainability

## Overview

- **Module:** Feature Engineering, Feature Selection & Explainability
- **Session:** 08
- **Duration:** 150 minutes (10-minute break included), plus optional Advanced Challenges
- **Audience:** Participants who have completed LAB02–LAB07

This lab moves beyond "which algorithm to use" (LAB07) into "which inputs and explanations
actually matter": systematic feature engineering, feature selection, data leakage/privacy
auditing, and model explainability (SHAP) on a new, larger, real-world supply-chain dataset.

## Learning Objectives

By the end of this lab, participants will be able to:

1. Explain Feature Engineering vs. Feature Selection vs. Feature Extraction.
2. Assess prediction-time feature availability.
3. Identify Target Leakage and Temporal Leakage risks.
4. Build Date-Time features, including cyclical encoding.
5. Build and validate Interaction/numerical features.
6. Use domain knowledge to justify (or reject) engineered features.
7. Explain Filter vs. Wrapper vs. Embedded feature selection.
8. Apply feature selection inside a Scikit-learn `Pipeline`.
9. Compare Baseline, Engineered, and Selected feature sets under an identical protocol.
10. Interpret model-based (XGBoost gain/weight/cover) feature importance.
11. Apply and interpret Permutation Importance.
12. Perform Global and Local explainability with SHAP.
13. State the limitations of model explanations (not causality, not fairness, not correctness).
14. Justify feature-engineering decisions with real experimental evidence rather than assumption.

## Dataset

**DataCo SMART Supply Chain** — `data/dataco_supply_chain/DataCoSupplyChainDataset.csv`
(180,519 order-item rows, 53 raw columns; latin-1 encoded, **not** UTF-8). Not committed to the
repository (already excluded by the existing `data/*` `.gitignore` rule) and not auto-downloaded.

## Dataset Attribution & License

- **Kaggle:** [DataCo SMART Supply Chain for Big Data Analysis](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis)
- **Original source:** [Mendeley Data](https://data.mendeley.com/datasets/8gx2fvg2k6/5) — DOI `10.17632/8gx2fvg2k6.5`

Credit for the original dataset belongs to its Mendeley Data authors; this lab only reads and
analyzes a local copy.

## Business Problem

**Pre-Dispatch Late Delivery Risk Prediction**: predict, before a shipment is dispatched,
whether an order carries a late-delivery risk. Target: `Late_delivery_risk` (`1` = risk, the
positive class; `0` = no risk per the recorded label). Verified distribution: ~54.8% / 45.2%
(moderately imbalanced, not severe).

**Prediction-time assumption:** order information and the planned shipping method are known;
actual shipment/delivery outcomes are not. This assumption is not independently verified against
a live operational system — it is a training assumption only.

## Privacy & Leakage Considerations

- **PII**: 9 columns (`Customer Email`, `Customer Password`, `Customer Fname`, `Customer Lname`,
  `Customer Street`, `Customer Zipcode`, `Order Zipcode`, `Customer Id`, `Order Customer Id`) are
  excluded **at CSV-read time** via `usecols` in `src/data_loading.py`'s
  `load_dataco_supply_chain()` — they are never loaded into memory. `Latitude`/`Longitude` are
  additionally dropped as a near-exact-location privacy risk.
- **Target leakage, verified (not assumed):** `Delivery Status` is deterministically identical
  to the target (every "Late delivery" row has `risk=1`; every other category has `risk=0`). An
  isolated, clearly labeled `INVALID — TARGET LEAKAGE` demo model trained on `Delivery Status`
  scores a perfect 1.0 ROC-AUC — included only to demonstrate the failure mode, never used in the
  real benchmark.
- **Ambiguous-availability features:** `Order Status` categories `CANCELED`/`SUSPECTED_FRAUD`
  perfectly predict `risk=0` but their prediction-time availability is unverified — excluded from
  the default feature set (flagged "Review" in the Feature Audit).
- **Duplicate columns, verified by equality check:** `Benefit per order`≡`Order Profit Per Order`,
  `Category Id`≡`Product Category Id`, `Order Item Cardprod Id`≡`Product Card Id`,
  `Product Price`≡`Order Item Product Price`. `Product Status` is constant; `Product Description`
  is 100% missing.

## Feature Engineering Methods

- **Baseline (10 features):** `Days for shipment (scheduled)`, `Shipping Mode`, `Market`,
  `Order Region`, `Customer Segment`, `Department Name`, `Category Name`, `Order Item Quantity`,
  `Order Item Product Price`, `Order Item Discount Rate`.
- **Engineered (+10):** Date-Time (`order_month`, `order_day_of_week`, `order_quarter`,
  `is_weekend`), Cyclical (`order_hour_sin`/`order_hour_cos`), Interaction/numerical
  (`gross_item_value`, `estimated_discount_amount`, `quantity_x_scheduled_days`,
  `log_gross_item_value`). All deterministic, row-level transforms (no fitting required).
- A `Weekend × Shipping Mode` interaction candidate was tested and **rejected** — real data
  showed no meaningful added signal beyond `Shipping Mode` alone.

## Feature Selection Methods

Filter (`VarianceThreshold`, correlation analysis, ANOVA F-test via `SelectKBest`, Mutual
Information), and a brief Embedded demo (`SelectFromModel`). Wrapper methods (RFE) are
computationally expensive and moved to Advanced Challenge 1. All selection is fit on training
data only, inside a `Pipeline`.

## Experimental Design

Three controlled experiments (E01/E02/E03), same fixed XGBoost configuration, same split, same
decision threshold (`0.5`):

| Experiment | Feature Strategy | Input Features | Transformed | Selected | Val ROC-AUC | Val F1 |
|---|---|---|---|---|---|---|
| E01 | Baseline | 10 | 69 | 69 | 0.7195 | 0.6488 |
| E02 | Engineered | 20 | 79 | 79 | 0.7492 | 0.6825 |
| E03 | Selected (`VarianceThreshold`+`SelectKBest(k=20)`) | 20 | 79 | 20 | 0.7510 | 0.6831 |

Feature Engineering (E01→E02) produced a real, measured improvement (+0.0297 ROC-AUC). Feature
Selection (E02→E03) kept performance essentially unchanged while cutting the final feature count
by ~75%.

## Explainability Methods

Section 6 explains the **E03** pipeline (chosen explicitly for its smaller, cleaner feature set).
Model-Based Importance (weight/gain/cover — shown to genuinely disagree with each other),
Permutation Importance (on original, pre-encoding columns, through the fitted pipeline — avoids
unrealistic one-hot-dummy combinations), and SHAP (`TreeExplainer`, `model_output="raw"`, with a
verified additivity check and an explicit raw-margin-vs-probability `sigmoid()` demonstration).
Global (bar, beeswarm) and Local (3 waterfall examples: high-risk, low-risk, misclassified-near-
threshold) explanations are included.

## Required Dependencies

This lab adds `shap` (and `ipywidgets`, to eliminate a benign `tqdm` import warning) to the
project's dependencies (`pyproject.toml`/`uv.lock`). No Docker system packages were needed — SHAP's
dependencies (`numba`/`llvmlite`) run cleanly on the existing `python:3.11-slim` image.

## Running with Docker

From the project root:

```powershell
docker compose up --build -d
```

Check logs for the JupyterLab access URL and token:

```powershell
docker compose logs ml-lab
```

## Opening the Notebook

Open `http://localhost:8888`, then navigate to
`labs/lab08/lab08_feature_engineering_explainability.ipynb`.

## Expected Learning Outcomes

Participants leave this lab able to audit a new dataset for leakage and privacy risk before
touching a model, engineer and validate new features with real evidence (not assumption), run a
controlled feature-strategy benchmark, and produce SHAP-based global/local explanations while
correctly stating their limitations.

## Dataset & Experiment Limitations

- No independent test evaluation was performed in this lab — `test_df` is reserved, untouched,
  for LAB09's final evaluation (the same dataset and split are reused there).
- Hyperparameters are documented starting points, not the result of systematic optimization
  (out of scope — see LAB09).
- Financial fields (`Benefit per order`, `Order Item Profit Ratio`, etc.) have unverified
  profit-realization timing and were excluded from the default feature set.
- Training Time/Inference Latency figures are hardware-specific and shown to vary measurably
  between runs; the notebook reports qualitative, run-to-run-stable patterns rather than exact
  numbers for these two metrics.

## Advanced Challenges

Five optional challenges, outside the 150-minute core:

1. **Recursive Feature Elimination** — on a controlled 8,000-row sample; only 5/20 features
   overlap with Section 4's full-data `SelectKBest` selection.
2. **Embedded Feature Selection** — L1-regularized Logistic Regression (`l1_ratio=1.0`),
   compared against the Filter-based selection.
3. **Feature Ablation Study** — removing the Date-Time group hurts ROC-AUC by -0.028 despite
   those features' weak *individual* correlations — a real group-vs-individual-effect finding.
4. **Grouped Permutation Importance** — `order_hour_sin`/`order_hour_cos` permuted together show
   more importance than their individual sum, demonstrating correlated-feature attribution bias.
5. **SHAP Explanation Stability** — Top-5 global ranking proved identical across 3 random seeds
   for this dataset's dominant signal.
