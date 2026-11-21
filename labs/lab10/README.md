# LAB 10 — Time Series Fundamentals & Forecasting Baselines

## Overview

- **Module:** Time Series Fundamentals & Forecasting Baselines
- **Session:** 10
- **Duration:** 150 minutes (10-minute break included), plus optional Advanced Challenges
- **Audience:** Participants who have completed LAB02–LAB09

This lab is the transition point from classic tabular Machine Learning (LAB02–LAB09) to **Time
Series Forecasting**. It builds a leakage-safe chronological evaluation protocol and three
baseline forecasting methods (Naive, Seasonal Naive, Moving Average), evaluated with
Rolling-Origin backtesting — producing a reference benchmark and a reusable split/evaluation
protocol for LAB11 (Machine Learning for Time Series Forecasting) and LAB12 (End-to-End ML PoC).
No new dependency was added; no XGBoost/LightGBM/SHAP/ARIMA/Prophet/deep learning model is
trained in this lab.

## Learning Objectives

By the end of this lab, participants will be able to:

1. Explain the difference between Time Series and classic tabular data.
2. Explain the relationship between Forecasting and Regression.
3. Explain Frequency, Granularity, and Temporal Dependency.
4. Interpret Trend, Seasonality, Noise, and Autocorrelation.
5. Build a date-indexed Pandas Series.
6. Check for Missing Dates and Duplicate Timestamps.
7. Define Forecast Origin and Forecast Horizon.
8. Apply a chronological Train/Validation/Test split.
9. Identify Temporal Leakage risks.
10. Build Naive, Seasonal Naive, and Moving Average forecasting functions.
11. Compute MAE, RMSE, WAPE, and MASE.
12. Apply Rolling-Origin Evaluation.
13. Compare baseline models and interpret results in business terms.
14. Hand off a reliable evaluation protocol for LAB11.

## Dataset

**Bike Sharing in Washington D.C.** — daily bike rental records with calendar and weather
context, January 2011 through December 2012 (731 daily observations). Only `day.csv` is used
in the main lab; `hour.csv` is used solely in Advanced Challenge 4.

## Dataset Source & Attribution

- Kaggle: [marklvl/bike-sharing-dataset](https://www.kaggle.com/datasets/marklvl/bike-sharing-dataset)
- Original source — UCI Machine Learning Repository: [Bike Sharing Dataset](https://archive.ics.uci.edu/dataset/275/bike-sharing-dataset)
- DOI: [10.24432/C5W894](https://doi.org/10.24432/C5W894)
- Authors: Hadi Fanaee-T and João Gama
- License: CC BY 4.0

The dataset is placed manually by the user; this lab never auto-downloads it and never modifies
the original CSV files.

## Dataset Files & Placement

```text
data/
└── bike_sharing/
    ├── day.csv    (used — main dataset for this lab)
    └── hour.csv   (used only in Advanced Challenge 4)
```

Verified real schema (16 columns): `instant, dteday, season, yr, mnth, holiday, weekday,
workingday, weathersit, temp, atemp, hum, windspeed, casual, registered, cnt`. Verified: 0
missing values, 0 duplicate dates, 0 missing calendar dates, 0 negative/zero `cnt` values, and
`cnt == casual + registered` holds for every row in the training period.

## Forecasting Business Problem

**Daily Bike Rental Demand Forecasting:** predict the next 14 days of total daily rentals
(`cnt`) from historical daily rentals. Relevant to Fleet Capacity Planning, Resource Allocation,
Maintenance Planning, Staffing Decisions, and Service Capacity Planning. **Limitation:** `cnt`
is *observed* usage, not unconstrained demand — the dataset carries no information about unmet
demand or bike-availability constraints.

## Target Variable

**`cnt`** — total daily bike rental count. Note the exact relationship `cnt = casual +
registered` (verified on the training period). `casual` and `registered` are **never** used as
forecast inputs — they are same-day realized outcome components of the target itself (Target
Leakage). `instant` (a row index) and any realized weather observations (`weathersit`, `temp`,
`atemp`, `hum`, `windspeed`) are also excluded from baseline forecasting inputs, since real
future weather observations are not available at forecast time for a 14-day horizon.

## Forecast Horizon

- **Forecast Horizon:** 14 days (`forecast_horizon` in `config/settings.yaml`'s `lab10`
  namespace).
- **Seasonal Period:** 7 days (weekly), chosen over an annual period because only ~2 years of
  history are available — not enough to reliably confirm year-over-year seasonality.
- **Moving Average Window:** 7 days.

## Chronological Splitting

Managed in `config/settings.yaml` (`lab10.split`), verified against the real dataset:

| Period | Range | Observations |
|---|---|---|
| Training | 2011-01-01 → 2012-08-31 | **609** |
| Validation | 2012-09-01 → 2012-10-31 | **61** |
| Protected Test | 2012-11-01 → 2012-12-31 | **61** |

609+61+61 = 731 (full coverage, no overlap). The Protected Test period's `cnt` values are never
read, plotted, or used in any analysis in this lab — it is reserved for LAB12.

## Baseline Forecasting Methods

- **Naive:** repeats the last observed value for the full horizon.
- **Seasonal Naive (m=7):** repeats the last 7 observed days, tiled across the horizon.
- **Moving Average (window=7):** repeats the mean of the last 7 observed days across the
  horizon.

All three are deterministic, use only historical observations available at the forecast origin,
and are implemented in `labs/lab10/lab10_time_series_fundamentals.ipynb` (`naive_forecast`,
`seasonal_naive_forecast`, `moving_average_forecast`).

## Evaluation Metrics

MAE, RMSE, WAPE (0 when the denominator is zero, never NaN/inf), and MASE — the MASE
denominator is computed **once**, from the initial Training Period's seasonal (m=7) naive
absolute differences, and reused for every baseline, every origin, and every aggregate result
(fixed-scaling policy, also required to carry over into LAB11). Forecast Bias (mean signed
error) is reported alongside as a directional diagnostic.

## Rolling-Origin Evaluation

Expanding-history backtesting over 4 fixed, non-overlapping 14-day windows:

```text
Origin 2012-08-31 -> 2012-09-01..09-14
Origin 2012-09-14 -> 2012-09-15..09-28
Origin 2012-09-28 -> 2012-09-29..10-12
Origin 2012-10-12 -> 2012-10-13..10-26
```

The last 5 days of the Validation period (2012-10-27 → 2012-10-31) fall outside this fixed
14-day/4-origin protocol and are explicitly reported as excluded, not silently folded into the
last window.

### Key, Honest Finding

Despite strong weekly autocorrelation (Lag-7 ≈ 0.79 on the training period), the **Naive**
baseline achieved the lowest Mean Fold MAE (≈750) overall — ahead of Moving Average (≈815) and
Seasonal Naive (≈894). The validation period sits in a strong seasonal *decline* (summer→autumn);
Seasonal Naive repeats a now-outdated, higher weekly pattern and systematically overforecasts,
while Naive's single most-recent value tracks the decline better over a 14-day horizon. This is
reported as the real, measured result — not assumed in advance — consistent with this lab's own
principle that no baseline is declared best before validation evidence.

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
`labs/lab10/lab10_time_series_fundamentals.ipynb`.

## Generated Artifacts

Written to `labs/lab10/artifacts/` (gitignored — not committed) on every full run:

- `forecasting_metadata.json` — dataset identity/hash, forecast frequency/horizon/seasonal
  period, evaluation metrics, MASE scaling policy, environment/package versions.
- `split_metadata.json` — chronological split boundaries, backtesting configuration, the 4
  forecast origins, and the 5 excluded validation dates.
- `baseline_results.csv` — fold-level rows (`Row_Type=FOLD`, 12 rows: 4 origins × 3 models) plus
  aggregate rows (`Row_Type=AGGREGATE`, 6 rows: 3 models × {mean_fold, pooled}, distinguished by
  an `Aggregation_Method` column).
- `validation_forecasts.csv` — forecast-level rows (168 rows: 4 origins × 14 horizon steps × 3
  models) with `Actual`/`Prediction`/`Error`/`Absolute_Error`.

No Protected Test Period date or value appears in any artifact (asserted in the notebook itself).
None contain PII — this dataset has none.

## Expected Learning Outcomes

Participants leave this lab able to distinguish forecasting from regression, build a
leakage-safe chronological evaluation protocol, implement and evaluate baseline forecasters
honestly (including when the theoretically-favored method does not win), and hand over a
reusable split/backtesting protocol and reference benchmark to LAB11.

## Dataset Limitations

- Only ~2 years of history — insufficient to confirm a stable year-over-year annual
  seasonality; the 7-day weekly period is used instead, supported by the measured autocorrelation.
- `cnt` is observed, not unconstrained, demand.
- The fixed 14-day/4-origin backtesting protocol leaves 5 validation days unevaluated by design
  (documented, not hidden).
- Weather features are excluded from baselines because future weather is not known at a 14-day
  forecast origin in a real deployment; LAB11 may revisit exogenous-feature availability.

## Advanced Challenges

Four optional challenges, outside the 150-minute core:

1. **Forecast Horizon Sensitivity** — compares baseline MAE across horizons 7/14/28 using the
   same 4 origins.
2. **Seasonal Period Sensitivity** — compares Seasonal Naive across periods 1/7/14; period=1 is
   verified to reduce mathematically to the Naive baseline's own result.
3. **Rolling vs Expanding Window** — compares a fixed 60-day lookback window against the full
   expanding history for Moving Average; results are expected to coincide here since the window
   size (7) is far shorter than either history length.
4. **Hourly Demand Exploration** — an exploratory-only look at `hour.csv`'s intraday profile;
   does not alter the daily `day.csv` baseline benchmark.
