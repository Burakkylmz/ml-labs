# LAB 07 — Advanced Machine Learning & Ensemble Methods

## Overview

- **Module:** Advanced Machine Learning & Ensemble Methods
- **Session:** 07
- **Duration:** 150 minutes, plus optional Advanced Challenges
- **Audience:** Participants who have completed LAB02–LAB06

This lab builds directly on LAB06's classification methodology (same dataset, same feature
selection rationale, same stratified split) and extends it with Ensemble Learning: Bagging,
Boosting, Random Forest, AdaBoost, Gradient Boosting, XGBoost, and LightGBM, culminating in a
systematic, same-protocol comparison of 8 classifiers.

The goal of this lab is **not** to maximize predictive accuracy. The goal is to teach systematic
model comparison, experiment design, generalization analysis, and computational cost analysis.

## Learning Objectives

By the end of this lab, participants will be able to:

1. Explain the Ensemble Learning concept and how it differs from a single learner.
2. Apply Bootstrap Sampling (sampling with replacement).
3. Explain the differences between Bagging and Boosting.
4. Build and tune a Random Forest model.
5. Explain AdaBoost's adaptive sample-weighting mechanism.
6. Build a Gradient Boosting model and interpret its additive-model formulation.
7. Use XGBoost and LightGBM.
8. Interpret the Bias–Variance Trade-off through observed model behavior.
9. Evaluate the effect of core hyperparameters (`n_estimators`, `max_depth`, `learning_rate`,
   `num_leaves`, …).
10. Compare different models under identical experimental conditions.
11. Measure Training Time and Inference Latency.
12. Recognize signs of overfitting via the Generalization Gap.
13. Justify a model choice in terms of accuracy, speed, complexity, and business value.

## Dataset

This lab reuses the **same E-Commerce Shipping Data** dataset as LAB02–LAB06 —
`data/ecommerce_shipping/Train.csv` (10999 rows, 12 columns). No new dataset is introduced and
the original CSV is never modified.

**Business problem (same as LAB06): Shipment Delay Classification.** Target column:
`Reached.on.Time_Y.N` (`1` = Late Delivery, positive class; `0` = On Time).

**Selected features** (identical to LAB06, for a fair, consistent comparison):

| Feature | Type |
|---|---|
| `Warehouse_block`, `Mode_of_Shipment`, `Product_importance` | Categorical |
| `Cost_of_the_Product`, `Prior_purchases`, `Discount_offered`, `Weight_in_gms` | Numerical |

**Excluded by design** (same rationale as LAB06): `ID`, the target itself, `Customer_rating` /
`Customer_care_calls` (unverified prediction-time availability / leakage risk), `Gender` (no
operational justification, fairness risk).

### Test Set Integrity Notice

This lab's stratified `%70/%15/%15` split uses the **exact same** mechanism as LAB06
(`random_state=42`, same `stratify`), which reproduces LAB06's row assignment index-for-index.
LAB06 already evaluated its test split once (Section 8). Because of this, **all model-selection
decisions in this lab are made on the validation set only** — the benchmark in Section 6-7 is
reported as a development/validation benchmark, not an independent final test evaluation.

## Ensemble Learning Concepts

- **Bagging** (Bootstrap Aggregating): independent base learners trained on different bootstrap
  samples; predictions are averaged/voted. Tends to reduce variance. Example: Random Forest.
- **Boosting**: base learners trained sequentially, each correcting the previous one's errors.
  Tends to reduce bias (effect on variance/overfitting is configuration-dependent). Examples:
  AdaBoost, Gradient Boosting, XGBoost, LightGBM.
- **Random Forest** adds random feature selection at each split on top of Bagging, reducing
  correlation between trees.
- **AdaBoost** adaptively reweights misclassified observations between iterations.
- **Gradient Boosting** fits each new learner to the negative gradient of a loss function
  (residuals, in the regression/squared-error case).
- **XGBoost** and **LightGBM** are both Gradient Boosting implementations with different
  engineering choices (second-order gradient information + regularization for XGBoost;
  leaf-wise growth + histogram-based learning for LightGBM).

## Compared Models

`DummyClassifier`, `LogisticRegression`, `DecisionTreeClassifier`, `RandomForestClassifier`,
`AdaBoostClassifier`, `GradientBoostingClassifier`, `XGBClassifier`, `LGBMClassifier` — all built
as `Pipeline(preprocessing + model)` with the same `ColumnTransformer` (median/most-frequent
imputation, `StandardScaler`, `OneHotEncoder`).

## Benchmark Methodology

All 8 models are compared under an identical protocol: same dataset, feature set, train/validation
split, target definition, positive class, decision threshold (`0.5`, common to all models),
fixed CPU thread policy (`n_jobs=2`, no uncontrolled `n_jobs=-1`), and documented, pre-declared
hyperparameters (`config/settings.yaml`, `lab07` section).

- **Evaluation metrics:** Accuracy, Precision, Recall, F1, ROC-AUC, Average Precision,
  Generalization Gap (`Train_Accuracy - Validation_Accuracy`).
- **Ranking metric:** Validation ROC-AUC, declared *before* running the benchmark.
- **Training Time:** end-to-end Pipeline fit, median of 3 fresh/unfitted repeats.
- **Inference Latency:** `predict_proba()` on the full validation batch, with warm-up and median
  of 10 repeats; per-sample time is derived from the batch time, not a real single-request
  latency.

### Key Results (Real, Verified — metric columns are deterministic across runs)

| Model | Validation ROC-AUC |
|---|---|
| RandomForestClassifier | 0.7406 |
| GradientBoostingClassifier | 0.7338 |
| XGBClassifier | 0.7314 |
| DecisionTreeClassifier | 0.7290 |
| LogisticRegression | 0.7254 |
| LGBMClassifier | 0.7168 |
| AdaBoostClassifier | 0.6919 |
| DummyClassifier | 0.5000 |

**Critical finding:** `DummyClassifier` has the **highest** Validation F1 (≈0.748) of all 8 models
— a direct re-manifestation of LAB06's "F1 can be misleading when the positive class is the
majority" lesson, now shown across model families. This is why the ranking metric (ROC-AUC) was
declared before seeing the results. A Soft `VotingClassifier` combining LogisticRegression +
RandomForest + XGBoost reaches ROC-AUC≈0.7464, outperforming all three of its base models
(Advanced Challenge 4) — a genuine, non-generalizable result for this dataset.

Training Time and Inference Latency values are reported qualitatively in the notebook rather than
as fixed numbers, since (unlike the metric columns above) they are measurably noisy across runs on
the same hardware — `GradientBoostingClassifier` is consistently the slowest to train by a wide
margin; `RandomForestClassifier`/`AdaBoostClassifier` consistently have the highest inference
latency.

## Required Dependencies

This lab adds `xgboost` and `lightgbm` to the project's dependencies (`pyproject.toml`/`uv.lock`).
No other lab is affected. The Docker image additionally installs the `libgomp1` system package
(required for LightGBM's OpenMP-linked wheel on `python:3.11-slim`).

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
`labs/lab07/lab07_advanced_ml_ensemble_methods.ipynb`.

## Expected Learning Outcomes

Participants leave this lab able to build Bagging- and Boosting-family ensemble models, run a
disciplined, same-protocol benchmark across 8 classifiers, recognize when a single metric (e.g.
F1 under class imbalance) is misleading, and justify a model choice against multiple, sometimes
conflicting, business priorities (latency vs. predictive performance vs. explainability).

## Limitations

- Not a production-ready evaluation — no independent, previously-unseen test set exists for this
  dataset/target combination (LAB06 already used it once); all results here are a
  development/validation benchmark.
- Hyperparameters are documented starting points, not the result of systematic optimization
  (`GridSearchCV`/`RandomizedSearchCV`/Optuna are explicitly out of scope — see LAB09).
- Feature Engineering and Explainability (SHAP) are explicitly out of scope — see LAB08.
- Training Time/Inference Latency figures are specific to this hardware, dataset size (~11K rows),
  and `n_jobs=2` policy; they are not universal performance claims.

## Advanced Challenges

Four optional challenges, outside the 150-minute core session:

1. **Ensemble Size & Diminishing Returns** — a wider Random Forest `n_estimators` sweep
   (10–400) with marginal-AUC-per-100-trees.
2. **Equal Computational Budget** — a dynamic search matching XGBoost/LightGBM `n_estimators` to
   Random Forest's measured training time, with an explicit caveat that exact equality is not
   achievable.
3. **Early Stopping (Expanded)** — XGBoost and LightGBM early stopping examples, reported
   separately from the main benchmark since they use validation data to decide when to stop.
4. **Voting Classifier** — a Soft `VotingClassifier` combining three model families, with a
   probability-calibration caveat.
