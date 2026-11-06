# LAB 04 — Data Preparation & Preprocessing Pipelines

## Overview

- **Module:** Data Preparation & Preprocessing Pipelines
- **Session:** 04
- **Duration:** 150 minutes (including a 10-minute break)
- **Audience:** Participants who have completed LAB02 and LAB03

This lab builds directly on LAB02 (Python/Pandas fundamentals) and LAB03 (Statistics & EDA). The data
quality and distribution issues identified in LAB03 are not re-analyzed here — they are used as the
starting point for building a reproducible, leakage-free preprocessing workflow suitable for Machine
Learning modeling. No model is trained in this lab.

## Learning Objectives

By the end of this lab, participants will be able to:

1. Perform data quality checks.
2. Choose appropriate methods for handling missing values.
3. Evaluate duplicate and outlier records.
4. Apply categorical encoding.
5. Use feature scaling methods.
6. Create train, validation, and test splits.
7. Identify data leakage risks.
8. Use scikit-learn `Pipeline` and `ColumnTransformer`.
9. Build a reusable preprocessing workflow.
10. Verify that preprocessing parameters are learned from training data only.

## Dataset

This lab reuses the same **E-Commerce Shipping Data** dataset from LAB02/LAB03 — no new dataset is
introduced.

| Dataset | Path |
|---|---|
| E-Commerce Shipping Data | `data/ecommerce_shipping/Train.csv` |

The dataset must already be present from LAB02; it is not downloaded automatically. If the file is
missing, the notebook raises a clear `FileNotFoundError`.

> **Scope note:** Some features used in this lab for preprocessing practice (e.g. `Customer_rating`,
> `Customer_care_calls`, `Discount_offered`) have not been verified as genuinely available at real
> prediction time in an operational system. This dataset is used purely to teach preprocessing
> techniques, not as a validated real-time prediction feature set.

## Prerequisites

- Docker Desktop (or an organization-approved Docker environment) and Docker Compose V2
- LAB02 and LAB03 completed (`data/ecommerce_shipping/Train.csv` already in place)
- No local Python/uv/scikit-learn installation is required — everything runs inside the existing
  Docker image, which already includes scikit-learn.

## Lab Sections

1. **LAB03 Review & Preprocessing Workflow** — EDA vs Data Preparation, why fixing issues on the full
   dataset risks leakage.
2. **Data Quality & Validation** — completeness, validity, and a Data Quality Summary table.
3. **Missing Values & Duplicate Handling** — `SimpleImputer` strategies, `fit`/`transform` leakage rule,
   duplicate detection (demonstrated on in-memory copies with clearly labeled synthetic data).
4. **Outlier Detection & Treatment** — IQR method, clipping demonstration, rationale for excluding it
   from the main pipeline.
5. **Categorical Encoding & Feature Scaling** — `OneHotEncoder`, `handle_unknown="ignore"`,
   `StandardScaler` vs `MinMaxScaler`.
6. **Train/Validation/Test Split & Data Leakage** — stratified 70/15/15 split, leakage demonstration.
7. **Scikit-learn Pipeline & ColumnTransformer** — the core of this lab: a single, reusable,
   leakage-free preprocessing pipeline fit only on training data.
8. **Preprocessing Validation & Workshop** — a student-led end-to-end rebuild of the pipeline, plus a
   discussion of unknown categories and inconsistent scaler fitting.

Three optional **Advanced Challenges** (custom transformer, scaler comparison, leakage investigation)
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

Open `http://localhost:8888` in your browser (use the token from the logs if prompted), then navigate to
`labs/lab04/lab04_data_preparation.ipynb` in the JupyterLab file browser.

## Expected Outcomes

Participants leave this lab with a single, reusable scikit-learn `Pipeline` (numerical imputation +
scaling, categorical imputation + one-hot encoding, combined via `ColumnTransformer`) that is fit
exclusively on training data and applied consistently to validation and test data — along with concrete
checks proving no leakage occurred. This pipeline is the direct input to **LAB05/LAB06**, where a model
will be appended to it and trained.
