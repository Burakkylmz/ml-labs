# LAB12 — Stage 14 API & Deployment Contract

**Bu belge Stage 14 implementasyonu DEGILDIR -- yalnizca bir sonraki
asamanin tasarim sozlesmesidir. Stage 13'te HTTP API, FastAPI endpoint,
authentication veya deployment OLUSTURULMAMISTIR.**

## 1. Objective

Stage 13'un `FreightCostPredictor` inference component'ini, Stage 14'un
HTTP API katmaninin nasil tuketecegini tanimlamak.

## 2. Stage 13 Model Bundle

`labs/lab12/artifacts/stage13_model_bundle/v1/`, SHA-256=
`71a451344f8b88a8d440d90325b88668cd3a8c16379425f5a4e95061bed77782`.

## 3. Artifact Loading

Stage 14, servis baslangicinda **BIR KEZ**
`FreightCostPredictor.load(bundle_dir, allowed_root, expected_model_id="M04",
expected_trial_id="M04-T003")` cagirmali ve instance'i memory'de tutmalidir.
Her request'te yeniden yuklenmemelidir.

## 4. Input Schema

`dict` (single) veya `list[dict]` (batch). Required fields:
`Line_Item_Qty_Sum`, `Line_Item_Value_Sum`, `Shipment_Mode`, `INCO_Term`,
`Country`, `Product_Group`. Strict schema -- taninmayan alanlar REJECTED.

## 5. Output Schema

`PredictionResult.to_dict()`: `model_id`, `trial_id`, `model_version`,
`prediction_usd`, `prediction_validity`, `uncertainty_status`,
`explanation_status`, `explanation`, `risk_flags`, `invalid_reason`.

## 6. Single Prediction Endpoint Requirements

`POST /predict` -> `predictor.predict_one(shipment, explain=query_param)`.
Response 200 (valid) veya 422 (schema error) veya 200-with-invalid-flag
(negative/non-finite prediction, `prediction_validity="invalid"`).

## 7. Batch Endpoint Requirements

`POST /predict/batch` -> `predictor.predict_batch(shipments)`. Max batch
size = `predictor.max_batch_size` (100). Atomic validation -- tek bir
satir hatasi tum batch'i 422 ile reddeder.

## 8. Explainability Endpoint Policy

`explain=true` query parametresi, `max_batch_explanations` (10) ile
sinirlanmalidir -- bu limiti asan bir batch + explain=true istegi 422
dondurmelidir.

## 9. Unsupported Interval Policy

`request_interval=true` **hicbir zaman** lower/upper bound dondurmemelidir
-- sadece `INTERVAL_NOT_APPROVED` risk flag'i eklenir. Stage 14, bu
davranisi degistirmemeli veya bypass etmemelidir.

## 10. Validation Errors

`MISSING_REQUIRED_FIELD`, `UNKNOWN_FIELD`, `INVALID_FIELD_TYPE`,
`INVALID_NUMERIC_VALUE`, `INVALID_SHIPMENT_STRUCTURE`,
`BATCH_SIZE_EXCEEDED`, `EXPLANATION_BATCH_LIMIT_EXCEEDED` -- her biri HTTP
422 + acik error message'a eslenmelidir.

## 11. Service Error Codes

| Exception | Suggested HTTP Status |
|---|---|
| `FeatureSchemaError` | 422 Unprocessable Entity |
| `PredictionValidationError` | 500 (model produced invalid output -- internal) |
| `ArtifactIntegrityError` | 503 (service misconfigured -- should only occur at startup) |
| `ModelCompatibilityError` | 503 (service misconfigured -- should only occur at startup) |

## 12. Health & Readiness

**Health check:** servis process calisiyor mu. **Readiness check:**
`TrustedBundleLoader.load()` basariyla TAMAMLANDI mi -- tamamlanmadan
trafik kabul edilmemelidir.

## 13. Logging

Her request icin `model_id`/`trial_id`/`artifact_version`/`risk_flags`
loglanmalidir. Minimal Core schema'da PII YOKTUR (shipment mode, incoterm,
country, product group, miktarlar) -- raw shipment PII loglama riski
beklenmemektedir.

## 14. Docker Requirements

Mevcut `ml-lab` Docker servisi reuse edilmelidir -- **yeni bir Docker
service olusturulmamalidir**. Bundle, mevcut volume mount uzerinden
erisilebilir olmalidir (zaten `labs/lab12/artifacts/` icinde).

## 15. Security

API, kullanicidan **arbitrary bir model path kabul ETMEMELIDIR** --
bundle path'i sabit/trusted olmalidir. `allowed_root` degeri konfigurasyon
ile degil, kod icinde sabit tutulmalidir.

## 16. API Testing

Stage 14, contract-based API test'leri (HTTP status/response schema) ve
Docker service integration test'leri YAZMALIDIR -- bunlar Stage 13'un
component/integration test'lerinden (pytest, notebook) **AYRI bir
katmandir**.

## 17. Model Parity

Stage 14 API'nin dondurdugu `prediction_usd`, `FreightCostPredictor.predict_one()`'in
dogrudan ciktisi olmalidir -- API katmaninda EK bir transformasyon/rounding
(display-layer disi) YAPILMAMALIDIR.

## 18. Protected Test Policy

2015 Protected Test, Stage 14 API'sinde de **ACILMAMALIDIR** -- Stage 14
dahi 2015 verisini kullanmamalidir (bu, Stage 14'un API/Deployment
kapsaminda oldugu icin kendisi de Protected Test'e erisim GEREKTIRMEZ).

## 19. Operational Limitations

Production-approved monetary SLA YOK. Production Interval Not Approved
(disabled by default, degistirilmemeli). High-cost shipment riski (hem
point hem interval seviyesinde) devam ediyor -- Stage 14 bunu
"production-ready" olarak SUNMAMALIDIR.

## 20. Stage 14 Entry Criteria

**CONDITIONAL GO.** `FreightCostPredictor` prototype-ready; explainability
Approved; uncertainty Research Only/Disabled by Default. Stage 14, HTTP
API/Docker/automated testing katmanini bu sozlesme uzerine insa edebilir.
