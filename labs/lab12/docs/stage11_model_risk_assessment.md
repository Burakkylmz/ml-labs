# LAB12 — Stage 11 Model Risk Assessment

## 1. Reproducibility Risk (Cross-Environment)

Both candidates were refit and scored identically in two environments: local
Windows (uv/venv) and Docker (Linux container, `ml-lab` service), using the exact
same frozen config, dataset, and code.

| Model | Max Abs Prediction Diff (USD) | Median Abs Prediction Diff (USD) | Pooled MAE Diff |
|---|---|---|---|
| M04-T003 (ExtraTrees) | 2.91e-11 | 0.0 | ~0 (effectively identical) |
| M05-T000 (XGBoost) | **9,338.69** | **308.28** | 6591.33 (local) vs 6598.21 (Docker), ~0.10% |

**Key risk finding:** M05-T000's *aggregate* MAE is nearly identical across
environments (~0.10% difference), but **individual shipment predictions can differ
by up to $9,338** -- a materially large single-prediction discrepancy hidden by
aggregate-level cancellation of over/under-predictions. This confirms and
quantifies, with real Stage 11 data, the thread-dependent non-determinism in
XGBoost's `hist` tree_method first documented in Stage 10. M04-T003 shows no such
risk (floating-point-only noise, ~1e-11 USD). **Candidate ranking (M04 < M05 by
MAE) was stable across both environments** -- not an "Inconclusive" ranking
situation, but the individual-prediction risk is flagged as a real, unresolved
model-level concern for any downstream per-shipment use of M05-T000.

## 2. Tail / High-Cost Risk

Both candidates underpredict ~89.9% of high-cost (>= P90) shipments on 2014 --
reduced from baselines' 100%, but **not eliminated**. High-Cost Bias is strongly
negative for both models (M04: -16,722.52 USD, M05: -16,638.31 USD) -- this is the
single largest practical risk for any downstream use involving large/expensive
shipments: both models are systematically expected to undershoot true freight cost
for this segment.

## 3. Label Coverage / Missing-Not-At-Random Risk

~10% of shipments in both development and 2014 lack a usable numeric target. The
generating mechanism for this missingness remains unknown (open since Stage 05-06).
Coverage is stable over time (89.8% -> 90.0%), which reduces concern that this
mechanism is drifting, but does not resolve whether the missing 10% differ
systematically (in true cost) from the eligible 90%.

## 4. Single-Year External Validation Risk

2014 is a single, non-independent-and-identically-distributed sample of shipments
(temporal/operational correlation across shipments within the same year is
plausible but not modeled). The bootstrap exercise in Advanced Challenge 4
(shipment-level resampling, n=500) gives M04-T003 a mean bootstrap MAE of 6472.71
USD with a rough [P2.5, P97.5] range of [5843.21, 7175.73] USD. **Notably,
M05-T000's point MAE (6591.33 USD) falls inside this range** -- under simple
resampling variability alone, the two candidates are not clearly separable. This is
explicitly **not** a formal confidence interval (the i.i.d. assumption is
questionable for a single year of shipments) and is not used to overturn the
acceptance decision below -- it is reported as an honest caution against
overstating M04-T003's superiority as definitive rather than directionally likely.

## 5. Covariate Shift Risk

2014 shipments trend toward higher quantity/value (median Qty +75%, median Value
+17% vs development) and a narrower category mix (fewer distinct Country/INCO_Term/
Product_Group values observed). This is a plausible partial contributor to the
observed ~14% generalization gap, documented for monitoring design, not acted on.

## 6. Negative Prediction Risk

0/819 negative predictions for both candidates on 2014 -- a favorable outcome, but
sample-dependent (Stage 09/10 dev-CV saw up to several negative M05 predictions
depending on fold/environment). Raw, unclipped scoring was used throughout; this
risk is not proven eliminated, only not observed in this specific sample.

## 7. Selection Optimism Risk

Both M04-T003 and M05-T000 were chosen via development-CV performance before being
scored on 2014 -- the "winner" (M04-T003) is not from a fully independent test. The
true independent test remains the as-yet-unopened 2015 Protected Test (Stage 14).

## 8. Business SLA Risk

No business-approved monetary tolerance exists for this project. Stage 08's 5%
improvement criterion is a **provisional engineering target only**. This document
makes **no claim of production readiness or SLA satisfaction**.
