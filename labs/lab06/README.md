# LAB 06 — Supervised Learning: Classification

## Overview

- **Module:** Supervised Learning — Classification
- **Session:** 06
- **Duration:** 150 minutes (including a 10-minute break)
- **Audience:** Participants who have completed LAB02, LAB03, LAB04, and LAB05

This lab builds on LAB02 (Python/Pandas fundamentals), LAB03 (Statistics & EDA), LAB04
(preprocessing pipelines with `SimpleImputer`, `OneHotEncoder`, `StandardScaler`,
`ColumnTransformer`), and LAB05 (regression modeling methodology: baseline → model → evaluation →
comparison → selection → one-time test). It applies the same end-to-end methodology to a binary
classification problem.

## Learning Objectives

By the end of this lab, participants will be able to:

1. Define classification problems.
2. Select an appropriate target for binary classification.
3. Build a baseline classification model.
4. Train a Logistic Regression model.
5. Build a Decision Tree Classifier.
6. Explain probability scores and decision thresholds.
7. Build and interpret a confusion matrix.
8. Compute Accuracy, Precision, Recall, and F1-Score.
9. Perform ROC-AUC and Precision–Recall analysis.
10. Evaluate class imbalance problems.
11. Compare different classification models.
12. Select a decision threshold on validation data.
13. Independently evaluate the final model on test data.
14. Combine preprocessing and a classification model in a single Scikit-learn `Pipeline`.

## Dataset

This lab reuses the same **E-Commerce Shipping Data** dataset from LAB02/LAB03/LAB04 —
`data/ecommerce_shipping/Train.csv` (10999 rows, 12 columns, verified to contain no missing
values and no duplicate `ID`s). No new dataset is introduced; the Northwind dataset is not used.

## Classification Problem

**Business problem — Shipment Delay Classification:** predict whether a shipment will reach the
customer on time, using information reasonably assumed to be known before shipment dispatch.

**Selected features:**

| Feature | Type |
|---|---|
| `Warehouse_block`, `Mode_of_Shipment`, `Product_importance` | Categorical |
| `Cost_of_the_Product`, `Prior_purchases`, `Discount_offered`, `Weight_in_gms` | Numerical |

**Excluded by design:** `ID` (identifier), `Reached.on.Time_Y.N` (target),
`Customer_rating`/`Customer_care_calls` (unverified prediction-time availability / target
leakage risk), `Gender` (no operational justification; demographic features add fairness risk
without a documented benefit here).

## Target Label Definition

**Target column:** `Reached.on.Time_Y.N`

| Value | Meaning | Role in this lab |
|---|---|---|
| `1` | Product did **NOT** reach on time | **Positive class** — Late Delivery |
| `0` | Product reached on time | Negative class — On Time |

Verified real distribution: `1` (Late) = 6563 orders (59.67%), `0` (On Time) = 4436 orders
(40.33%) — moderately imbalanced, not severely imbalanced.

> **Prediction-time assumption:** the notebook assumes the model predicts **before shipment
> dispatch**. Whether the selected features are genuinely available at that point in a real
> operational system is not verified from this dataset alone — it is an explicit educational
> assumption, documented in the notebook.

> **Dataset limitation:** this is not real logistics-company data. Model outputs in this lab are
> not presented as production-ready.

## Lab Sections

1. **Classification Fundamentals & Dataset** — classification vs. regression, target
   distribution, feature selection rationale.
2. **Data Splitting & Baseline Models** — stratified train/validation/test split (70/15/15),
   `DummyClassifier(most_frequent)` baseline.
3. **Logistic Regression** — sigmoid/log-odds math, a preprocessing `Pipeline` +
   `ColumnTransformer` built for this dataset's schema, `predict()` vs. `predict_proba()`,
   coefficient interpretation.
4. **Decision Tree Classification** — Gini impurity, `max_depth` comparison illustrating
   underfitting vs. overfitting, tree visualization.
5. **Confusion Matrix & Classification Metrics** — TP/TN/FP/FN, Accuracy/Precision/Recall/F1,
   business interpretation of false positives/negatives.
6. **ROC-AUC & Precision–Recall Analysis** — threshold-independent ranking metrics, Average
   Precision interpreted against class prevalence.
7. **Class Imbalance & Decision Threshold** — a clearly labeled synthetic example contrasting
   severe imbalance with this dataset's real (moderate) imbalance; threshold comparison and a
   documented, business-motivated threshold selection (maximize recall subject to a minimum
   precision constraint).
8. **Model Comparison & Final Workshop** — a full model comparison table, final model + threshold
   selection, a single final test-set evaluation, and a Classification Evaluation Summary.

Three optional **Advanced Challenges** (class weight comparison, automated threshold tuning via
`TunedThresholdClassifierCV`, error segmentation by warehouse/shipment mode/product importance)
are included but are not part of the core 150-minute timing.

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

Open `http://localhost:8888` in your browser (use the token from the logs if prompted), then
navigate to `labs/lab06/lab06_supervised_classification.ipynb` in the JupyterLab file browser.

## Model Evaluation

Three models are trained and compared on validation data under identical preprocessing:
`DummyClassifier(most_frequent)`, `LogisticRegression`, and `DecisionTreeClassifier(max_depth=2)`.
`LogisticRegression` is selected as the final model — not because it has the single best
validation Accuracy/F1 (`DecisionTree(max_depth=2)` is marginally ahead there), but because it has
materially higher Average Precision (ranking quality) and produces continuous probability scores
that support meaningful decision-threshold tuning, unlike the shallow tree's 3-valued output.

A decision threshold (≈0.53) is selected on validation data under an explicit business objective
("maximize Recall subject to Precision ≥ 0.75"), after first showing that naive F1-maximization
degenerates toward the trivial always-positive baseline on this dataset (because the positive
class is already the majority class). The selected model and threshold are then evaluated exactly
once on the held-out test set.

## Expected Learning Outcomes

Participants leave this lab having trained and compared classification models — each wrapped
with the same preprocessing `ColumnTransformer`/`Pipeline`, fit exclusively on training data —
and can explain confusion-matrix-based metrics, the difference between threshold-dependent and
threshold-independent evaluation, why class imbalance affects Accuracy's reliability, and how to
pick and validate a decision threshold without touching the test set.

## Dataset Limitations

- This is a Kaggle educational dataset, not real data from an actual logistics company; results
  must not be presented as validated operational performance.
- Several candidate features (`Customer_rating`, `Customer_care_calls`) were excluded because
  their prediction-time availability could not be verified from the data alone — not because they
  lack predictive value.
- The real class imbalance (59.67%/40.33%) is moderate; the severe-imbalance "Accuracy Paradox"
  shown in Section 7 uses a clearly labeled synthetic example, not this dataset.
- Model performance (validation/test Accuracy ≈ 0.64) is modest; the selected features explain
  only part of the variation in on-time delivery.
