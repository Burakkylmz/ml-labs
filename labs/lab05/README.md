# LAB 05 — Supervised Learning: Regression

## Overview

- **Module:** Supervised Learning — Regression
- **Session:** 05
- **Duration:** 150 minutes (including a 10-minute break)
- **Audience:** Participants who have completed LAB02, LAB03, and LAB04

This lab builds on LAB02 (Python/Pandas fundamentals), LAB03 (Statistics & EDA), and LAB04
(preprocessing pipelines with `SimpleImputer`, `OneHotEncoder`, `StandardScaler`,
`ColumnTransformer`, and leakage-free train/validation/test splitting). It introduces supervised
regression modeling on a new dataset and a new business problem.

## Learning Objectives

By the end of this lab, participants will be able to:

1. Define a regression problem and distinguish it from classification.
2. Build a baseline regression model.
3. Train a Linear Regression model.
4. Apply Multiple Linear Regression.
5. Explain Ridge and Lasso regularization.
6. Build a Decision Tree Regression model.
7. Compute MAE, MSE, RMSE, and R².
8. Perform residual analysis.
9. Evaluate underfitting and overfitting.
10. Compare regression models under the same conditions.
11. Build a reliable preprocessing + model training pipeline.

## Dataset

This lab uses the **Northwind Orders** dataset — specifically `data/northwind/orders.csv`
(830 rows, 14 columns). No other LAB02 Northwind table is required.

| Dataset | Path |
|---|---|
| Northwind Orders | `data/northwind/orders.csv` |

The dataset must already be present from LAB02; it is not downloaded automatically. If the file is
missing, the notebook raises a clear `FileNotFoundError`.

## Regression Problem

**Target variable:** `Freight` (continuous, numerical; verified in the notebook to contain no
missing or negative values; range ≈ 0.02–1007.64).

**Business problem — Freight Charge Prediction:** predict a shipment's freight charge from order
and shipment information that is reasonably assumed to be known before the charge itself.

**Selected features:**

| Feature | Type |
|---|---|
| `ShipCountry`, `ShipRegion`, `ShipVia` | Categorical |
| `Order_Month`, `Order_Weekday`, `Planned_Lead_Time_Days` (derived from `OrderDate`/`RequiredDate`) | Numerical |

**Excluded by design:** `Freight` (target), `OrderID` (identifier), `ShippedDate` (post-shipment,
leakage risk), `CustomerID` and address fields (`ShipName`/`ShipAddress`/`ShipCity`/
`ShipPostalCode`, high cardinality, not justified for this scope), `EmployeeID` (out of scope).

> **Dataset limitation:** Northwind is a historical, educational dataset. It cannot be determined
> from this data alone exactly when `Freight` is computed in a real operational system. The
> notebook states this assumption explicitly and does not present its model outputs as validated
> real-world freight pricing or operational cost estimates.

## Lab Sections

1. **Regression Fundamentals & Dataset** — what regression is, dataset loading, target
   distribution.
2. **Data Splitting & Baseline Models** — feature selection rationale, chronological
   train/validation/test split (70/15/15), `DummyRegressor` baselines.
3. **Linear & Multiple Linear Regression** — a clearly labeled synthetic example for the simple
   regression math, then a real Multiple Linear Regression pipeline with coefficient
   interpretation.
4. **Ridge & Lasso Regularization** — L2 vs. L1 shrinkage, `alpha` comparison, coefficient
   zeroing behavior.
5. **Decision Tree Regression** — `max_depth` comparison illustrating underfitting vs.
   overfitting.
6. **Regression Evaluation Metrics** — MAE, MSE, RMSE, R², and a full model comparison table.
7. **Residual Analysis & Model Comparison** — actual-vs-predicted, residual plots, error
   segmentation by `ShipCountry`.
8. **Final Workshop & Evaluation** — model selection, a single final test-set evaluation, and a
   Model Evaluation Summary.

Three optional **Advanced Challenges** (regularization path, target transformation, error
segmentation by `ShipVia`) are included but are not part of the core 150-minute timing.

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
navigate to `labs/lab05/lab05_supervised_regression.ipynb` in the JupyterLab file browser.

## Expected Learning Outcomes

Participants leave this lab having trained and compared a `DummyRegressor` baseline,
`LinearRegression`, `Ridge`, `Lasso` (at multiple `alpha` values), and `DecisionTreeRegressor`
models — each wrapped with the same preprocessing `ColumnTransformer`/`Pipeline`, fit exclusively
on training data. They select one model on validation performance, evaluate it exactly once on the
held-out test set, and can explain the model's residual behavior and limitations.

## Dataset Limitations

- `Freight`'s true cost drivers (e.g., shipment weight/volume, found in `order_details.csv`) are
  not part of `orders.csv` and are not used here — this caps achievable model performance
  (validation/test R² ≈ 0.15–0.18 in this lab).
- `ShipRegion` is missing for most non-US/Canada/Brazil/Venezuela orders; this is a structural
  pattern tied to `ShipCountry`, not random missingness, and is handled accordingly
  (`SimpleImputer(strategy="constant", fill_value="Unknown")`).
- Country-level error segmentation groups are small (5–16 orders) and are presented with an
  explicit small-sample caveat, not as statistically robust conclusions.
- `ShipVia` is used as a feature under the explicit assumption that the carrier is already known
  at prediction time; this assumption is not independently verified against a real operational
  system.
