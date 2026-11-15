# LAB 09 — Model Selection, Hyperparameter Optimization & Reproducibility

## Overview

- **Module:** Model Selection, Hyperparameter Optimization & Reproducibility
- **Session:** 09
- **Duration:** 150 minutes (10-minute break included), plus optional Advanced Challenges
- **Audience:** Participants who have completed LAB02–LAB08

This lab moves from "which features and model family" (LAB08) to "how do we reliably tune and
evaluate a chosen model family": Cross-Validation design (including a custom group-aware
temporal CV), `GridSearchCV`/`RandomizedSearchCV`, Experiment Tracking without MLflow, and a
gated, one-time Final Test Evaluation.

## Learning Objectives

By the end of this lab, participants will be able to:

1. Distinguish Model Parameters from Hyperparameters.
2. Explain Hyperparameter Optimization and what it does/doesn't fix.
3. Explain and compare Cross-Validation strategies (KFold, Stratified, Group, TimeSeries).
4. Build a custom CV splitter that respects both group and temporal integrity.
5. Use `GridSearchCV` and `RandomizedSearchCV` with a Scikit-learn `Pipeline`.
6. Design a hyperparameter search space and compute its computational budget.
7. Analyze CV results (`cv_results_`, fold variability, train/CV generalization gap).
8. Evaluate whether hyperparameter optimization improved generalization — honestly, even when
   it didn't.
9. Build an Experiment Registry, dataset/split fingerprinting, and environment metadata with
   plain Python/Pandas/JSON (no MLflow).
10. Run a reproducibility check and state its real limits.
11. Evaluate a final, frozen model on a protected test set exactly once, behind an explicit gate.

## Dataset

Same as LAB08: DataCo SMART Supply Chain (`data/dataco_supply_chain/DataCoSupplyChainDataset.csv`).
No new dataset, no modification to the original CSV.

## Previous Lab Dependencies

This lab **reconstructs LAB08's split and feature strategy from its actual code**, not from
assumption:

- **Split:** group-aware chronological cutoffs, re-derived deterministically (verified to
  reproduce LAB08's exact row counts: train=126,364 / validation=27,079 / test=27,076).
- **Feature strategy:** LAB08's "E03 — Selected" pipeline (`VarianceThreshold` +
  `SelectKBest(f_classif, k=20)` on top of the baseline + engineered feature set).
- **Reference model configuration:** LAB08's XGBoost config (`max_depth=4, learning_rate=0.1,
  n_estimators=100`), used as the E04 baseline.

## Cross-Validation Strategy

`KFold`/`StratifiedKFold`/`GroupKFold`/`TimeSeriesSplit` are each demonstrated on a small
synthetic example, then shown to be individually insufficient for this dataset (which needs
**both** group and temporal integrity). A custom `create_group_temporal_folds()` builds a
3-fold expanding-window split **within the training set only**, verified (not assumed) to have:
zero row overlap, zero `Order Id` overlap across train/validation within every fold, correct
temporal ordering, and both classes present in every fold.

## Hyperparameter Optimization

A controlled search space and computational budget were defined **before** results were seen —
3 CV folds, 8 Grid Search candidates, 8 Randomized Search candidates (see Computational Resource
Policy below).

## Grid Search

8 candidates (`max_depth` × `learning_rate` × `n_estimators`, 2 values each), 3 CV folds → 24
fits + 1 refit. Best: `max_depth=5, learning_rate=0.1, n_estimators=100`, Mean CV ROC-AUC≈0.7625.

## Randomized Search

8 candidates sampled from a 4,800-combination space (6 hyperparameters). Best Mean CV
ROC-AUC≈0.7636 — a negligible improvement over Grid Search, using a different search space.

### Key, Honest Finding

Neither search produced a **measurable** improvement on the independent development validation
set versus the untouched LAB08 baseline (absolute change ≈ -0.0004 ROC-AUC). This is reported
explicitly as the expected, legitimate outcome when a feature set's signal ceiling is already
close to being reached — not as a lab failure.

## Experiment Tracking

Built with plain Python/Pandas/JSON/CSV — **no MLflow, W&B, or DVC** (introduced only
conceptually): an Experiment Registry (`experiment_registry.csv`), chunk-based SHA-256 dataset
fingerprinting, a privacy-safe split-membership fingerprint (no raw ID lists persisted),
environment/dependency metadata (including an honest "not available" report for git info, since
this machine has a pre-existing git ownership issue — no commit SHA was fabricated), and
JSON-safe serialization of NumPy/NaN/datetime values.

## Reproducibility

Two independent fits with the same seed/config/data produced bit-identical predictions
(`np.allclose`), with an explicit caveat that this does not generalize across different
hardware, library versions, or parallel execution.

## Computational Resource Policy

`3 CV folds`, `8` Grid Search candidates, `8` Randomized Search candidates, `search_jobs=1`,
`estimator_threads=2` — deliberately avoiding nested unbounded parallelism
(`GridSearchCV(n_jobs=-1)` + `XGBClassifier(n_jobs=-1)` together). Total search time for both
searches combined: well under 1% of the 150-minute session.

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
`labs/lab09/lab09_model_selection_optimization.ipynb`.

## Experiment Artifacts

Written to `labs/lab09/artifacts/` (gitignored — not committed) on every full run:
`experiment_registry.csv`, `experiment_metadata.json`, `grid_search_results.csv`,
`randomized_search_results.csv`, `model_comparison.csv`, `fold_summary.csv`,
`selected_model_config.json`, and — only once the final-evaluation gate is deliberately opened —
`final_evaluation.json`. None contain PII or raw customer records.

## Final Test Evaluation

Gated behind `RUN_FINAL_TEST_EVALUATION` (sourced from `config/settings.yaml`'s
`lab09.evaluation.run_final_test`, default `false`) — a normal "Run All" never touches the
protected test set. This is an educational execution guard, not a real data-security mechanism.

With explicit approval, the gate was opened once for this build: the selected model
(`XGBClassifier`, RandomizedSearchCV's best configuration) was evaluated on the untouched test
set exactly one time. Real results: **Test ROC-AUC≈0.7577, Test F1≈0.7003, Test AP≈0.8157** —
between the CV estimate (≈0.7636) and the development validation estimate (≈0.7506), consistent
with a reasonably generalizing model rather than overfitting to any one split. The gate was then
reverted to `false` for the shipped notebook.

## Limitations

- LAB08's `validation_df` was already used for feature-strategy and explainability model
  selection — it is development evidence, not a second independent holdout.
- Non-nested CV search results may be mildly optimistic (Advanced Challenge 3's small Nested CV
  experiment suggests this optimism is modest for this dataset, not large).
- Search budgets (8 candidates) are intentionally small for the 150-minute session; Advanced
  Challenge 5 shows that even a much larger budget (20 candidates) did not improve on this.
- Training Time/Inference Latency figures are hardware-specific.

## Advanced Challenges

Five optional challenges, outside the 150-minute core, none using the test set:

1. **Random Forest Optimization** — comparable Mean CV ROC-AUC to optimized XGBoost.
2. **LightGBM Optimization** — search converged to a low-complexity configuration
   (`num_leaves=15`), consistent with LAB08's small-dataset overfitting caution.
3. **Nested Cross-Validation** — on a 40,000-row development subset; outer-fold scores closely
   tracked the non-nested `best_score_`, suggesting modest optimism in this specific case.
4. **Successive Halving** — a real resource-allocation issue was found and fixed: the default
   heuristic produced a first round with only 12 training rows per fold (triggering NaN scores
   from single-class folds); explicit `min_resources=2000` resolved it cleanly.
5. **Search Budget Sensitivity** — `n_iter` of 5, 10, and 20 all converged to the identical
   `best_score_` (0.7636), showing no marginal benefit from the larger budgets here.
