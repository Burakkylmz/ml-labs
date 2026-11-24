# LAB12 — Stage 13 Inference Architecture

## 1. Architecture Overview

```text
labs/lab12/inference/
  contracts.py       -- exceptions, FeatureSchema, PredictionResult, risk flag vocabulary
  schemas.py          -- FeatureSchemaValidator (required/nullable/numeric/categorical)
  artifact_store.py   -- write_bundle(), compute_sha256() (versioned, atomic)
  model_loader.py      -- TrustedBundleLoader (security-checked loading)
  predictor.py          -- FreightCostPredictor (the single public interface)
  explainability.py     -- ShapExplainer (optional, bounded SHAP)
  risk_flags.py         -- deterministic flag functions
```

Notebook bu modulleri **import eder ve calistirir** -- kod notebook icinde
TEKRAR YAZILMAMISTIR.

## 2. Artifact Loader

`TrustedBundleLoader(allowed_root, expected_model_id, expected_trial_id)` --
path/manifest/identity/SHA-256/dependency kontrolleri, SONRA `joblib.load()`.

## 3. Schema Validator

`FeatureSchemaValidator(schema, fitted_categories, strict=True)` -- field
presence, numeric/categorical type/value kurallari, unknown-category
flag'i (reject degil).

## 4. Feature Adapter

Ayri bir `feature_adapter.py` **olusturulmadi** -- canonical input zaten
shipment-seviyesinde oldugu icin raw-line-item-to-shipment ETL gerekmedi
(bkz `stage13_feature_inference_contract.md` Section 7).

## 5. Predictor

`FreightCostPredictor` -- tek public interface. `load()` (classmethod),
`predict_one()`, `predict_batch()`.

## 6. Single Inference

`predict_one(shipment, explain=False, request_interval=False)` ->
`predict_batch([shipment], ...)[0]` cagirir (kod duplikasyonu yok).

## 7. Batch Inference

`predict_batch(shipments, explain=False, request_interval=False)` --
atomic validation (tek bir satir schema hatasi TUM batch'i reddeder),
vectorized `ColumnTransformer.transform()` + `model.predict()`.

## 8. Result Contract

`PredictionResult` dataclass: `model_id`, `trial_id`, `model_version`,
`prediction_usd`, `prediction_validity`, `uncertainty_status`,
`explanation_status`, `explanation`, `risk_flags`, `invalid_reason`.
`.to_dict()` JSON-uyumlu cikti uretir.

## 9. Exception Handling

`ArtifactIntegrityError`, `ModelCompatibilityError`, `FeatureSchemaError`,
`PredictionValidationError` -- her biri ACIK bir nedenle raise edilir,
genel bir `except: return 0.0` fallback **hicbir yerde YOKTUR**.

## 10. Model Lifecycle

```text
Historical Data -> Frozen Recipe -> Full-Dev Refit -> Fitted Pipeline ->
Serialization -> Versioned Bundle -> Secure Loading -> Input Validation ->
Feature Transformation -> Prediction -> Output Validation & Metadata
```

## 11. Performance

Model dosya boyutu ~6.8 MB. Artifact load ~48ms. Tekil prediction latency
P90~41ms (ilk cagri icluding lazy SHAP explainer init degil). Batch
(100 satir) per-item ~1ms (vectorization avantaji). SHAP overhead ~14-15ms/item
(bu nedenle `max_batch_explanations=10` siniri konuldu).

## 12. Stage 14 Integration

Stage 14 API katmani, `FreightCostPredictor`'i **baslangicta BIR KEZ**
`TrustedBundleLoader` ile yuklemeli ve memory'de tutmalidir -- her
request'te yeniden yuklememelidir. Bkz `stage14_api_deployment_contract.md`.
