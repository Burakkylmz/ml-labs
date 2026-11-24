# LAB12 — Stage 11 External Validation Results

**Tum sayilar `stage11_external_metrics.csv`'den alinmistir (N_Eligible=819,
2014).**

## 1. Headline Results

| Model | External MAE (USD) | RMSE | Median AE | WAPE (%) | Bias (USD) |
|---|---|---|---|---|---|
| **M04-T003 (ExtraTrees, Primary)** | **6485.63** | 11654.35 | 3192.11 | 49.88 | -1600.06 |
| M05-T000 (XGBoost, Alternative) | 6591.33 | 11946.75 | 3180.06 | 50.69 | -1440.82 |
| B4 (Hierarchical Median) | 9770.79 | 17294.61 | 4438.12 | 75.14 | -6451.63 |
| B1 (Global Mean) | 11111.03 | 16884.42 | 8024.83 | 85.45 | -2547.35 |

**M04-T003 remains the best model** on genuinely unseen 2014 data, consistent with
its development-CV ranking (5686.34 USD). Both ML candidates beat both baselines by
a wide margin (M04: +33.6% vs B4, M05: +32.5% vs B4).

## 2. Development-CV vs External Comparison

| Model | Dev-CV MAE | External MAE | Gap (USD) | Gap (%) |
|---|---|---|---|---|
| M04-T003 | 5686.34 | 6485.63 | +799.29 | +14.1% |
| M05-T000 | 5818.29 | 6591.33 | +773.04 | +13.3% |

Both candidates show a comparable, modest generalization gap (see
`stage11_generalization_diagnostics.md` for the caveats on attributing this gap
solely to overfitting).

## 3. Paired Error Analysis

`d_i = |Actual - Pred_Primary| - |Actual - Pred_Alternative|` (negative = M04-T003
better). Mean paired diff = **-105.69 USD** (M04-T003 slightly better on average
error magnitude). **Shipment-level win rate: M05-T000 wins on 51.3% of individual
shipments, M04-T003 wins on 48.7%** -- despite this, M04-T003 has the lower
*aggregate* MAE because a handful of very large disagreements (up to ~21,490 USD on
a single shipment) are dominated by M05-T000 over-predicting more severely in those
specific cases. Win-rate and MAE must be read together, not in isolation.

## 4. Negative Prediction Audit

0/819 negative predictions for **both** M04-T003 and M05-T000 on 2014 (0.0% rate).
Minimum raw prediction: M04-T003=1429.39 USD, M05-T000=593.47 USD. This is a
sample-dependent observation (Stage09/10 dev-CV runs showed 0-8 negative
predictions for M05 depending on fold/environment) -- not a guarantee the
underlying risk is eliminated.

## 5. High-Cost Segment (>= 23,897.32 USD, 149 shipments)

| Model | High-Cost MAE | High-Cost Underprediction Rate |
|---|---|---|
| M04-T003 | 17852.87 | 89.93% |
| M05-T000 | 18245.32 | 89.93% |
| B4 | 32907.30 | 100.00% |
| B1 | 31276.09 | 100.00% |

The Stage 08-10 finding (baselines underpredict high-cost shipments 100% of the
time) **independently replicates on 2014**. Both ML candidates reduce -- but do not
eliminate -- this risk.

## 6. Segment-Level MAE (Shipment Mode)

| Mode | B4 | M04-T003 | M05-T000 |
|---|---|---|---|
| Air | 9283.84 | 4931.10 | 5010.98 |
| Air Charter | 19320.84 | 16927.32 | 15952.57 |
| Ocean | 11585.23 | 10722.49 | 11410.47 |
| Truck | 8411.75 | 6686.06 | 7032.66 |

Both ML models beat B4 in every mode. M05-T000 is slightly better than M04-T003 for
"Air Charter" and "Ocean"; M04-T003 is better for "Air" and "Truck" -- a real,
non-uniform segment pattern, not used for model selection.

## 7. Fair Comparison Confirmation

All 4 predictors were scored on the identical 819-shipment eligible set
(programmatically asserted).
