# LAB 11 — Machine Learning for Time Series Forecasting

## Overview

- **Module:** Machine Learning for Time Series Forecasting
- **Session:** 11
- **Duration:** 150 minutes (10-minute break included), plus optional Advanced Challenges
- **Audience:** Participants who have completed LAB02–LAB10

This lab continues directly from LAB10: the same dataset, the same chronological split, and the
same 4-origin Rolling-Origin evaluation protocol are reused (recovered from LAB10's real
config/artifacts, not reassumed). It converts the forecasting problem into a Supervised
Learning problem via lag/rolling/calendar features, trains four regression models (Ridge,
Random Forest, XGBoost, LightGBM), and evaluates them with Recursive Multi-Step Forecasting
against LAB10's baselines. No new dependency was added.

## Learning Objectives

By the end of this lab, participants will be able to:

1. Convert a Time Series Forecasting problem into a Supervised Learning problem.
2. Build Lag Features.
3. Use Rolling Statistics (correctly, with `shift(1)` before `rolling()`).
4. Build Calendar Features (including cyclical encoding).
5. Check Feature Availability at forecast time.
6. Identify Temporal Leakage risks.
7. Explain the difference between Direct and Recursive Forecasting.
8. Implement Recursive Multi-Step Forecasting.
9. Use Ridge, Random Forest, XGBoost, and LightGBM regression for forecasting.
10. Manage feature engineering and estimator components in a consistent pipeline.
11. Perform Rolling-Origin Backtesting.
12. Compare ML models against LAB10's real baseline results.
13. Compute MAE, RMSE, WAPE, MASE, and Forecast Bias.
14. Perform Horizon-Based Error Analysis.
15. Explain Recursive Error Accumulation.
16. Evaluate the relationship between model complexity and forecasting performance.
17. Select a model candidate for LAB12 — honestly, even when no ML model wins.

## Dataset

Same as LAB10: Bike Sharing `day.csv` (`data/bike_sharing/day.csv`). No new dataset, no
modification to the original CSV. Dataset identity is re-verified by SHA-256 against LAB10's
real `forecasting_metadata.json`.

## Previous LAB10 Requirements

This lab **recovers LAB10's real protocol from its actual artifacts and config**, not from
assumption:

- **Dataset fingerprint:** SHA-256 hash re-verified to match LAB10's `forecasting_metadata.json`.
- **Chronological split:** Training 609 / Validation 61 / Protected Test 61 days, read from
  `config/settings.yaml`'s shared `lab10.split` block.
- **Forecast origins:** the same 4 origins (`2012-08-31`, `2012-09-14`, `2012-09-28`,
  `2012-10-12`), regenerated with LAB10's own `create_rolling_origins()` logic and asserted
  equal to LAB10's real `split_metadata.json`.
- **MASE denominator:** recomputed identically from the initial Training Period and asserted
  equal to LAB10's real `forecasting_metadata.json` value (≈854.08).

## Business Problem

**Daily Bike Rental Demand Forecasting** — same as LAB10: predict the next 14 days of total
daily rentals (`cnt`) from historical observations plus deterministic calendar information.
`cnt` remains observed, not unconstrained, demand.

## Forecast Horizon

14 days, seasonal period 7 days — both read from config and asserted consistent with LAB10.

## Lag Features

`lag_1`, `lag_7`, `lag_14`, `lag_28` (`target.shift(k)`). The first 28 rows of the training
period are dropped from the supervised matrix (insufficient history for `lag_28`), never
backfilled with future values.

## Rolling Features

`rolling_mean_7`, `rolling_mean_14`, `rolling_std_7`, `rolling_min_7`, `rolling_max_7` — each
computed as `target.shift(1).rolling(window=...)`. The notebook explicitly demonstrates, with a
real plot, why omitting the `shift(1)` leaks the current day's own value into its own feature.

## Calendar Features

`day_of_week`, `month`, `quarter`, `is_weekend`, plus cyclical sin/cos encodings for
`day_of_week` and `month`. These are deterministic for any future date and require no
historical observation.

## Recursive Forecasting

One model is trained per forecast origin; `recursive_forecast()` then predicts 14 steps
sequentially, appending each (non-negative-clipped) prediction to a working history copy before
computing the next step's lag/rolling features — exactly the same feature definitions used in
training (`build_feature_row()` vs `build_supervised_features()`, verified equal on real
training dates: **Training-Inference Parity**). An explicit test confirms forecast outputs are
unchanged even when all post-origin actual values are corrupted in a separate copy of the
series — the function is structurally unable to see the future.

## Regression Models

Ridge (`alpha=10.0`, scaled), Random Forest (`n_estimators=100, max_depth=8`), XGBoost
(`n_estimators=100, max_depth=3, learning_rate=0.05`), LightGBM (`n_estimators=100,
max_depth=4, num_leaves=15`) — untuned starting configurations (hyperparameter optimization is
LAB09's topic, not this lab's).

## Rolling-Origin Evaluation

Same 4 origins and 14-day non-overlapping windows as LAB10, for all 7 experiments
(E01–E07 below), each model retrained at every origin using only history available at that
origin.

## Forecasting Metrics

MAE, RMSE, WAPE, MASE (fixed denominator from LAB10), and Forecast Bias — identical function
definitions to LAB10, re-verified against LAB10's real MASE denominator.

## Benchmarking Methodology

| ID | Model | Kind |
|---|---|---|
| E01 | Naive | baseline (from LAB10) |
| E02 | Seasonal Naive | baseline (from LAB10) |
| E03 | Moving Average | baseline (from LAB10) |
| E04 | Ridge | ML |
| E05 | Random Forest | ML |
| E06 | XGBoost | ML |
| E07 | LightGBM | ML |

Primary ranking metric: **Pooled MAE**. Training time is `NaN` ("Not Applicable") for
baselines, since they require no model fitting — never treated as equivalent to ML training
time.

### Key, Honest Finding (real result, not assumed)

**No ML model outperformed any of the 3 baselines** on Pooled MAE in this lab:

| Experiment | Model | Pooled MAE | Pooled Bias |
|---|---|---|---|
| E01 | Naive | **750.23** | -399.4 |
| E03 | Moving Average | 815.15 | -60.7 |
| E02 | Seasonal Naive | 894.38 | -60.7 |
| E05 | Random Forest | 1081.09 | +649.8 |
| E07 | LightGBM | 1110.64 | +687.6 |
| E04 | Ridge | 1167.05 | +778.1 |
| E06 | XGBoost | 1306.78 | +957.1 |

All four ML models show strong **positive Forecast Bias** (systematic overforecasting). The
likely cause: the Training Period (2011–mid-2012) carries a generally rising trend; the ML
models' lag/rolling features let them learn and extrapolate that rising pattern, overshooting
into the Validation Period's actual *declining* trend (also the root cause behind LAB10's own
Naive-beats-Seasonal-Naive finding). This is reported exactly as measured — the lab's own
stated principle is that ML must never be assumed to win.

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
`labs/lab11/lab11_ml_time_series_forecasting.ipynb`.

## Experiment Artifacts

Written to `labs/lab11/artifacts/` (gitignored — not committed) on every full run:

- `feature_metadata.json` — feature names/definitions, excluded features and why.
- `experiment_metadata.json` — dataset identity, protocol, model configs, environment/package
  versions.
- `ml_validation_forecasts.csv` — forecast-level rows (392 rows: 4 origins × 14 steps × 7
  experiments).
- `ml_model_results.csv` — fold-level rows (28 rows: 4 origins × 7 experiments).
- `model_comparison.csv` — aggregate Pooled/Mean-Fold metrics, ranked by Pooled MAE, plus
  baseline-improvement columns.
- `horizon_error_analysis.csv` — MAE by horizon step (1–14) per model.
- `selected_model_config.json` — two LAB12 candidates (best overall, best ML model) with an
  explicit honest note about the baseline-vs-ML result above.

No Protected Test Period date or value appears in any artifact (asserted in the notebook
itself). None contain PII — this dataset has none.

## Expected Learning Outcomes

Participants leave this lab able to build a leakage-safe supervised time series dataset,
implement and verify recursive forecasting with Training-Inference Parity and an explicit
leakage test, and benchmark ML regressors against simple baselines honestly — including
accepting and explaining a result where the baselines win.

## Limitations

- Only 4 forecast origins were evaluated (same as LAB10).
- Hyperparameters are untuned starting values, not optimized (LAB09's topic).
- Only univariate lag/rolling/calendar features were used — no exogenous (weather) inputs.
- Recursive forecasting compounds its own prediction errors into subsequent lag features; this
  lab measures but does not correct for that.
- Training history is small (609 days, 581 after dropping NaN-lag rows).

## Advanced Challenges

Four optional challenges, outside the 150-minute core, none using the test set:

1. **Direct vs Recursive Forecasting** — trains 14 separate horizon-specific Random Forest
   models and compares their MAE against the Section 6 recursive Random Forest, at the same 4
   origins.
2. **Lag Feature Ablation** — compares `lag_1`, `lag_1+lag_7`, `lag_1+lag_7+lag_14`, and all 4
   lags with a fixed Ridge model, to measure real marginal value of adding lags.
3. **Rolling Window Sensitivity** — compares rolling-mean windows [3, 7, 14, 28] with a fixed
   Random Forest, preserving the `shift(1)`-before-`rolling()` rule throughout.
4. **Exogenous Forecasting Design** — a conceptual-only architecture discussion (no real future
   weather forecast dataset exists in this project, so none is added to the benchmark).
