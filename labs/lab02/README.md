# LAB 02 — Python for Machine Learning & Data Manipulation

## Overview

- **Module:** Python for Machine Learning & Data Manipulation
- **Session:** 02
- **Duration:** 150 minutes (including a 10-minute break)
- **Audience:** Beginner-level Python / Machine Learning participants

## Learning Objectives

By the end of this lab, participants will be able to:

1. Identify the core components of the Python data science ecosystem.
2. Perform NumPy array operations.
3. Use Pandas `Series` and `DataFrame` structures.
4. Read and inspect CSV files.
5. Apply filtering, selection, and sorting.
6. Use `groupby` and aggregation.
7. Combine multiple relational tables with merge and join.
8. Create basic data visualizations with Matplotlib.
9. Explain the difference between notebook code and a reusable Python module.

## Datasets

This lab uses two independent datasets — they are **not** merged with each other.

| Dataset | Path | Used for |
|---|---|---|
| **A — E-Commerce Shipping** | `data/ecommerce_shipping/Train.csv` | NumPy, Pandas EDA, Filtering, Sorting, GroupBy, Aggregation, Matplotlib |
| **B — Northwind** | `data/northwind/customers.csv`, `data/northwind/orders.csv`, `data/northwind/shippers.csv` | Relational data, merge, join, join validation |

Both datasets must be placed manually under `data/` before running the notebook — they are **not**
downloaded automatically. If a file is missing, the notebook raises a clear `FileNotFoundError` instead
of silently continuing.

## Files

- `lab02_python_data_manipulation.ipynb` — the main lab notebook, meant to be run cell by cell.
- `README.md` — this file.

The notebook relies on a small reusable helper module at `../../src/data_loading.py` for config loading
and dataset path resolution (see Section 8 of the notebook for details).

## Running the Lab

From the project root, start JupyterLab with Docker Compose:

```powershell
docker compose up --build -d
```

Open the URL printed in the logs (`docker compose logs ml-lab`), then open
`labs/lab02/lab02_python_data_manipulation.ipynb` from the JupyterLab file browser and run the cells
from top to bottom.
