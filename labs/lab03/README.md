# LAB 03 — Statistics & Exploratory Data Analysis

## Overview

- **Module:** Statistics & Exploratory Data Analysis
- **Session:** 03
- **Duration:** 150 minutes (including a 10-minute break)
- **Audience:** Participants who have completed LAB02

This lab builds directly on LAB02. NumPy, Pandas, data loading, filtering/sorting, and groupby/aggregation
are **not** re-taught here — they are used as tools to perform statistical analysis and exploratory data
analysis (EDA) on a dataset, as preparation for Machine Learning modeling in a later module.

## Learning Objectives

By the end of this lab, participants will be able to:

1. Explain what Exploratory Data Analysis (EDA) is and why it matters before model training.
2. Compute and interpret descriptive statistics (mean, median, mode).
3. Compute dispersion measures (variance, standard deviation, IQR).
4. Detect potential outliers using the IQR method.
5. Assess the shape of a distribution using histograms and skewness.
6. Perform a data quality assessment (missing values, duplicates, range/categorical checks).
7. Build and interpret a correlation matrix, respecting correlation-vs-causation limits.
8. Compare statistics across categorical groups.
9. Create EDA-specific Matplotlib visualizations (histogram, boxplot, bar chart, scatter plot).

## Dataset

This lab reuses the **E-Commerce Shipping Data** dataset from LAB02 — no new dataset is introduced, and
the Northwind dataset (LAB02's merge/join material) is **not** used here.

| Dataset | Path |
|---|---|
| E-Commerce Shipping Data | `data/ecommerce_shipping/Train.csv` |

The dataset must already be present from LAB02; it is not downloaded automatically. If the file is
missing, the notebook raises a clear `FileNotFoundError`.

## Lab Sections

1. **LAB02 Review & EDA Introduction** — what EDA is, dataset recap, target distribution.
2. **Descriptive Statistics** — mean, median, mode; NumPy vs Pandas.
3. **Dispersion, Quantiles & Outliers** — variance, standard deviation, IQR, outlier bounds.
4. **Data Distributions & Skewness** — histograms, skewness, a synthetic Normal Distribution demo.
5. **Data Quality Assessment** — missing values, duplicates, range/categorical checks, data quality report.
6. **Correlation & Group Comparisons** — Pearson correlation matrix, groupby-based comparisons.
7. **EDA Visualization with Matplotlib** — histogram, boxplot, bar chart, scatter plot.
8. **EDA Workshop & Findings** — a student-led mini EDA task, followed by an instructor findings summary.

Three optional **Advanced Challenges** (bootstrap confidence interval, multi-column group comparison,
statistical interpretation discussion) are included but are not part of the core 150-minute timing.

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
`labs/lab03/lab03_statistics_eda.ipynb` in the JupyterLab file browser.

## Expected Learning Outcomes

Participants leave this lab able to take a raw tabular dataset and, before any model is trained,
produce a structured statistical picture of it: central tendency and spread for key numerical features,
flagged data quality issues, an honest correlation/group-comparison read (with its limitations stated),
and a short written EDA findings summary — the direct input to **Module 4 — Data Preparation**.
