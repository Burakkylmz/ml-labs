# LAB12 — Stage 13 Artifact Design

## 1. Purpose

Stage 11'de kabul edilen, Stage 12'de aciklanan frozen ExtraTrees modelini
(M04-T003), versioned, checksummed, prototype-ready bir inference artifact'ina
donusturmek.

## 2. Frozen Model Identity

M04-T003 -- ExtraTrees: `{n_estimators=200, min_samples_split=10,
min_samples_leaf=2, max_features=0.8, max_depth=12, bootstrap=False,
random_state=42}`. Stage 10/11 ile birebir aynidir, **degistirilmemistir**.

## 3. Full Development Refit

Full eligible development population (2006-2013, n=4987) uzerinde yeniden
fit edildi. **Numerical identity check:** refit, Stage 11'in 2014 external
predictions'i ile **0.000000 USD** farkla eslesti (n=819,
`stage13_training_parity.csv`).

## 4. Artifact Structure

```text
stage13_model_bundle/v1/
  model.joblib              -- fitted Pipeline (preprocessing + ExtraTrees)
  manifest.json             -- identity, lineage, SHA-256, risk governance
  feature_schema.json       -- Stage 07 Minimal Core
  preprocessing_schema.json -- imputation/encoding policy, fitted categories
  model_config.json         -- frozen hyperparameters, random_state
  environment.json          -- python/sklearn/numpy/joblib/shap versions
  reference_predictions.json -- deterministic parity-check fixtures
```

## 5. Pipeline Persistence

Tek bir `sklearn.pipeline.Pipeline` (preprocessing + estimator BIRLIKTE)
`joblib.dump()` ile persist edildi -- preprocessing ve model ayri/uyumsuz
artifact'lara BOLUNMEMISTIR.

## 6. Manifest Design

Model identity, data lineage (dataset SHA-256, Stage 05 fingerprint,
eligible sample count), feature lineage (schema version, feature order),
preprocessing lineage, runtime versions, ve risk governance (D-006/D-007
acik, business SLA yok, production interval disabled) alanlarini icerir.

## 7. Artifact Versioning

`artifact_version="v1"` immutable'dir. `write_bundle()` mevcut, bos olmayan
bir version directory'sinin UZERINE YAZMAYI REFUSE eder (test edildi,
`stage13_artifact_integrity.csv`'ye bakin).

## 8. SHA-256

`model.joblib`'in SHA-256'si manifest icinde `model_artifact_sha256` olarak
saklanir. **Circular dependency yoktur** -- manifest kendi hash'ini icermez,
sadece model dosyasinin hash'ini icerir.

## 9. Dependency Metadata

`environment.json`: python_version, sklearn_version, numpy_version,
joblib_version, shap_version. Bu degerler `TrustedBundleLoader` tarafindan
yukleme ONCESI kontrol edilir (bkz `stage13_serialization_security.md`).

## 10. Reproducibility

Serialization parity (in-memory vs reloaded): max diff=0.00000000 USD.
Cross-environment (local Python 3.11.15 vs Docker Python 3.11.18) parity:
max diff=7.28e-12 USD (ayni bundle SHA-256, refit YOK -- sadece yukleme) --
bkz `stage13_reproducibility_report.json`.

## 11. Limitations

(1) Bu bir prototype bundle'dir -- signed release/trusted distribution
mekanizmasi YOKTUR. (2) ExtraTrees `n_jobs=2` ile predict() sirasinda
thread-order'a bagli ~1e-11 USD seviyesinde floating-point gurultu
gozlemlenebilir -- bu nedenle tum parity kontrolleri tolerance-based'dir
(exact `==` degil).
