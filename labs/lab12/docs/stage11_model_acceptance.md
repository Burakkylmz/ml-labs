# LAB12 — Stage 11 Model Acceptance

## 1. Decision

**Accepted for Stage 12 (Primary: M04-T003).** M05-T000 is retained as the
Alternative/secondary comparison candidate, not discarded.

## 2. Decision Basis (from `stage11_model_acceptance.json`)

- M04-T003 External MAE = 6485.63 USD, +33.6% vs B4 (9770.79 USD).
- M05-T000 External MAE = 6591.33 USD, +32.5% vs B4.
- M04-T003 is the lower-MAE candidate and its dev-CV ranking (M04 < M05) held on
  genuinely unseen 2014 data.
- Both candidates decisively outperform both baselines (B1, B4) on 2014 -- this is
  an independent confirmation of the Stage 09-10 model-vs-baseline finding, not a
  re-derivation from the same evidence.

## 3. Explicit Non-Claims

- **No "production-ready" or "SLA satisfied" claim is made.** No business-approved
  monetary tolerance exists for this project.
- Stage 08's 5% improvement criterion remains a **provisional engineering target
  only**, not a business acceptance threshold.
- The acceptance decision is **not** a fully independent test result: both
  candidates were development-CV-selected *and* scored on this same 2014 set.
  Selection optimism is not fully removed. Stage 14's Protected Test (2015,
  currently unopened) remains the final, truly independent evaluation.

## 4. Known, Documented Risks Carried Forward (see `stage11_model_risk_assessment.md`)

1. XGBoost (M05-T000) individual predictions vary up to $9,338 across environments
   despite near-identical aggregate MAE.
2. High-cost shipment underprediction reduced to ~89.9% but not eliminated for
   both candidates.
3. ~10% label coverage gap, stable over time but of unknown mechanism.
4. Single external validation year -- bootstrap resampling shows M05-T000's MAE
   falls within M04-T003's resampling variability band.
5. Covariate shift observed (2014 shipments trend larger/higher-value, narrower
   category mix).

## 5. Acceptance Criteria Checklist

| Criterion | Status |
|---|---|
| Full development refit performed (not fold-reuse) | PASSED |
| 2014 scored exactly once, no re-scoring | PASSED |
| 2015 Protected Test never opened | PASSED |
| Both frozen candidates scored (no cherry-picking) | PASSED |
| High-cost threshold frozen before reading 2014 targets | PASSED |
| Fair comparison (identical eligible population for all 4 predictors) | PASSED |
| Cross-environment reproducibility checked, not cherry-picked | PASSED |
| No new hyperparameter search / feature selection / target transform | PASSED |
| No business SLA / production-readiness claim made | PASSED |

## 6. Stage 12 Handoff

See `stage12_explainability_uncertainty_contract.md` and
`stage11_stage12_handoff.json` for the frozen configuration, known risks, and
explainability/uncertainty requirements passed to Stage 12.
