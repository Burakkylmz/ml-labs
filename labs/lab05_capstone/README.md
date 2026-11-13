# LAB 05 Capstone Project — Multiple Linear Regression

## Overview

- **Project:** Historical Property Valuation — King County House Sales
- **Primary Method:** Ordinary Least Squares (OLS) Multiple Linear Regression (`statsmodels`)
- **Total Duration:** 6 sessions × 150 minutes ≈ 15 hours
- **Audience:** Participants who have completed LAB02–LAB06

**This capstone is independent of, and does not replace, `labs/lab05/lab05_supervised_regression.ipynb`**
(the existing LAB05 session, which uses `scikit-learn` and the Northwind dataset). This capstone
is a separate, deeper, statistics-focused treatment of multiple linear regression using
`statsmodels` and a new dataset.

## Learning Objectives

By the end of this capstone, participants will be able to:

1. Assess a dataset's quality, anomalies, and structural patterns without silently deleting data.
2. Build a leakage-free, chronologically split train/validation/test workflow.
3. Conduct systematic univariate, bivariate, and multivariate EDA.
4. Engineer domain-justified features and document their leakage risk.
5. Diagnose and remediate perfect and high multicollinearity (VIF, Condition Number, rank).
6. Fit and interpret an OLS model's full `statsmodels` summary output.
7. Run and interpret formal hypothesis tests (t-tests, joint F-tests, confidence intervals).
8. Run and interpret OLS assumption diagnostics (Breusch-Pagan, Jarque-Bera, Durbin-Watson,
   Ramsey RESET) — and recognize numerical-stability false alarms versus real violations.
9. Perform influence diagnostics (leverage, Cook's Distance) and a sensitivity analysis.
10. Compare classical and HC3 robust standard errors, and know what HC3 does *not* fix.
11. Compare alternative OLS specifications (including a log-target model with retransformation
    bias correction) using validation-only evidence.
12. Select a final model and evaluate it exactly once on held-out test data.

## Dataset

- **Source:** [Kaggle — House Sales in King County, USA](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction)
- **File:** `data/king_county_house_sales/kc_house_data.csv` (not committed to the repository —
  must be placed manually)
- **Target:** `price`
- **Verified real profile:** 21,613 rows, 21 columns, 21,436 unique property IDs (177 repeat
  sales), 0 missing values, 0 exact duplicate rows, date range 2014-05-02 to 2015-05-27.

## Business Scenario

**Historical Property Valuation**: learn from past King County sales to model sale price from
property characteristics. This is explicitly **not** a real-time production valuation system.

## Data Splitting

Chronological, day-boundary-aligned split (no sale date is split across two sets):

| Split | Rows | Date Range | Share |
|---|---|---|---|
| Train | 15,100 | 2014-05-02 → 2015-01-15 | 69.9% |
| Validation | 3,242 | 2015-01-16 → 2015-03-25 | 15.0% |
| Test | 3,271 | 2015-03-26 → 2015-05-27 | 15.1% |

134 properties (0.62%) appear in more than one split due to repeat sales; this is measured and
reported, not used to override the chronological split strategy.

## Curriculum

| Session | Content | Sections |
|---|---|---|
| 1 | Problem Definition & Data Quality | 01–05 |
| 2 | Univariate EDA & Distribution Analysis | 06–09 |
| 3 | Bivariate & Multivariate EDA | 10–14 |
| 4 | Feature Engineering & Multicollinearity | 15–19 |
| 5 | OLS Regression & Statistical Diagnostics | 20–24 |
| 6 | Model Refinement & Final Evaluation | 25–30 |

Each section follows: Learning Objective → Concept Explanation → (Engineering Motivation /
Statistical Foundations where applicable) → Hands-On Implementation → Expected Output → Output
Interpretation → Critical Engineering Notes → Student Exercise → Checkpoint.

## Key Results (Real, Verified)

- **Perfect multicollinearity** demonstrated via `sqft_above + sqft_basement = sqft_living`
  (rank-deficient design matrix, VIF ≈ 10¹⁵).
- **Final feature set** (full column rank, all numeric VIFs < 5 after centering `grade`/
  `house_age_at_sale` before squaring): `sqft_living`, `bedrooms`, `bathrooms`, `floors`,
  centered `grade`/`grade²`, `condition`, `view`, `waterfront`, centered `house_age`/`age²`,
  `lat`, `long`, `basement_ratio`, `is_renovated_at_sale`, `zipcode` (one-hot), `sale_quarter`
  (one-hot).
- **Initial OLS**: R² ≈ 0.836, Adj. R² ≈ 0.835, F ≈ 882.3 (p ≈ 0).
- **Assumption diagnostics**: homoscedasticity and residual normality **violated**
  (Breusch-Pagan, Jarque-Bera both p ≈ 0); error independence **OK** (Durbin-Watson ≈ 1.97);
  Ramsey RESET indicates incomplete specification.
- **Six alternative specifications compared** (Initial, Refined, Feature-Engineered,
  Interaction, Polynomial, Log-Target) on validation data only.
- **Final model: Log-Target OLS with Duan's smearing correction** — selected for a 16.5%
  validation MAE improvement over Initial OLS and substantially reduced (not eliminated)
  heteroscedasticity/non-normality.
- **Final test performance** (evaluated once): MAE ≈ 86,227, RMSE ≈ 149,573, R² ≈ 0.842 — close
  to validation performance, indicating no overfitting to the validation set.

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
`labs/lab05_capstone/lab05_capstone_multiple_linear_regression.ipynb`.

## Dependencies

This capstone adds `seaborn` and `statsmodels` to the project's dependencies (`pyproject.toml`/
`uv.lock`). No other LAB is affected.

## Limitations

- Not a production valuation system; specific to 2014–2015 King County sales.
- `sqft_living15`/`sqft_lot15` excluded due to unverified prediction-time availability (and
  empirically shown not to improve the model when added as a sensitivity check).
- Conditional exogeneity cannot be verified from residual plots alone — an inherent OLS
  limitation, not a notebook defect.
- Feature selection was performed on the training data; post-selection inference caveats apply.
- `sale_month`/`sale_quarter` extrapolate to months (February–April) not present in training
  data.
