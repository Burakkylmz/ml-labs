# LAB12 — Stage 13 Validation Results

## 1. Environment

Local: Python 3.11.15, scikit-learn 1.9.1, numpy 2.4.6, pandas 3.1.0,
joblib 1.6.0, shap 0.51.0. Docker: Python 3.11.18 (same minor series),
identical sklearn/numpy/joblib/shap versions.

## 2. Artifact Integrity

Bundle contains all 7 required files. Manifest's `model_artifact_sha256`
matches `compute_sha256(model.joblib)` exactly. `write_bundle()` refuses to
overwrite an existing non-empty version directory (tested).

## 3. Serialization Parity

In-memory vs reloaded-and-predicted (n=50, development 2014 sample): max
abs diff = 0.00000000 USD -- PASS. Training-refit vs Stage 11 reference
predictions (n=819): max abs diff = 0.00000000 USD (then 7.28e-12 USD on a
later rerun -- see Section 8, `n_jobs=2` note) -- PASS within tolerance.

## 4. Feature Schema Tests

11 schema tests run (`stage13_schema_validation_results.csv`): valid
input, missing required feature, allowed null categorical, invalid
numeric type, NaN-as-missing, infinite value, unknown category, extra
field, reordered keys, negative numeric, non-dict structure. All REJECTED
or ACCEPTED exactly as designed.

## 5. Single Inference

1,785.11 USD for the sample shipment (real 2014 record structure),
`prediction_validity="valid"`.

## 6. Batch Inference

n=30: single/batch max diff = 0.00000000 USD -- PASS, order and count
preserved. Challenge 2 extended this to batch sizes 1/5/20/50, all with
max diff <= 1.46e-11 USD vs single-call results.

## 7. Explainability

10 SHAP explanations computed (tree_path_dependent, model_output=raw).
All passed additivity (max diff = 5.09e-11 USD, well under the 1.0 USD
tolerance). Explainability overhead: ~14-15 ms/item, consistent across
batch sizes 1/5/10 (Challenge 3) -- this is why `max_batch_explanations=10`
was set.

## 8. Risk Flags

7 deterministic risk-flag tests, all PASSED. **Real finding:**
`PREDICTION_OUTSIDE_REFERENCE_RANGE` almost never fires in practice for
this tree ensemble -- even an absurd input (qty=1,000,000,
value=50,000,000) produced a prediction (39,119.23 USD) within the
training-observed range [0.75, 289,653.20] USD, because tree ensembles
cannot extrapolate beyond training leaf values. The flag's underlying
logic was separately verified correct against a synthetic case.

## 9. Security Tests

6/6 failure-mode tests PASSED (`stage13_artifact_security_tests.csv`):
corrupted model file (SHA-256 mismatch), wrong model_id, wrong trial_id,
untrusted path outside allowed_root, missing manifest, dependency version
mismatch -- every scenario correctly rejected. Challenge 1 extended tamper
detection to 3 additional corruption patterns (truncate last byte, flip
first byte, truncate half) on an isolated copy -- 3/3 detected; the
original accepted artifact was never touched.

## 10. Dependency Compatibility

**Real, self-caught issue during this stage's own Docker validation:**
local (Python 3.11.15) and this project's Docker image (Python 3.11.18)
differ at the patch level. The initial exact-match `ModelCompatibilityError`
check correctly rejected this (fail-closed behavior working as designed),
which led to a deliberate policy fix: `python_version` is now compared by
major.minor only; `sklearn_version` remains an exact-match requirement.
After the fix, loading succeeded in both environments.

## 11. Local/Docker Parity

Same bundle (`model_artifact_sha256` identical across both runs, confirmed
-- Docker loaded, did not refit). Predictions on 25 real 2014 shipments
agreed to within 7.28e-12 USD -- consistent with Stage 11's documented
ExtraTrees `n_jobs=2` thread-order floating-point noise, not a real
discrepancy.

## 12. Runtime Measurements

Model file size: 6,783.10 KB. Artifact load time: 46.00 ms. First
prediction latency: 40.88 ms. Repeated single-prediction mean: 47.59 ms
(P90: 62.26 ms). Batch of 100: 54.00 ms total (0.54 ms/item).

## 13. Failures and Resolutions

1. **Permutation-importance-style sign bug did NOT recur here**, but a
   related bug WAS found and fixed: two notebook assertions used strict
   `==` to compare ExtraTrees predictions across calls/environments. Under
   `n_jobs=2`, thread-completion-order-dependent floating-point summation
   can introduce ~1e-11 to 1e-12 USD noise even for a deterministic
   (`bootstrap=False`) estimator -- both assertions were corrected to use
   a 1e-6 USD tolerance, consistent with every other parity check in this
   notebook.
2. The initial `PREDICTION_OUTSIDE_REFERENCE_RANGE` integration test
   assumed an extreme input would produce an out-of-range prediction; this
   assumption was wrong for a tree ensemble (see Section 8) and the test
   was corrected to verify the flag's logic directly instead.
3. The Docker-vs-local Python patch-version mismatch (Section 10) was
   caught by the security policy working exactly as designed, and resolved
   via a documented, deliberate policy refinement (not a workaround).

## 14. Remaining Risks

D-006/D-007 unresolved; no business-approved SLA; Production Interval
remains Not Approved (Stage 12, unchanged); no signed/authenticated
artifact distribution mechanism; XGBoost (secondary model, not part of
this bundle) cross-environment instability inherited from Stage 11 if
ever packaged separately.
