# LAB12 — Stage 14 (Phase A) API Implementation

**Kapsam:** REST API, Docker reuse, otomatik test. Phase B (2015 Protected
Test final evaluation) bu dokumanin ve Stage 14 Phase A'nin kapsaminda
DEGILDIR -- `stage14_phase_a_final_report.md`'ye bakiniz.

## 1. Paket Yapisi

`labs/lab12/api/` (`labs/lab12/inference/` ile ayni konvansiyon -- paket
kok dizini icin `__init__.py` yok, `--app-dir`/`sys.path` ile adreslenir):

| Dosya | Sorumluluk |
|---|---|
| `config.py` | Sabit bundle yolu, model identity, batch limitleri, canary shipment |
| `schemas.py` | Yalnizca OpenAPI dokumantasyonu icin Pydantic response modelleri |
| `errors.py` | Exception -> HTTP status mapping (bkz. Section 11 asagida) |
| `app.py` | FastAPI app, lifespan, endpoint'ler |

## 2. Tasarim Karari: Request Body Validasyonu Duplike EDILMEDI (D-158)

`FeatureSchemaValidator` zaten field presence/type/value kontrolunu
yapiyor (Stage 13, D-145). API katmani request body'yi sabit-alanli bir
Pydantic model olarak TANIMLAMADI -- cunku bu, iki paralel validasyon
kaynagi yaratir ve zamanla contract drift riski tasir (D-146'nin ayni
mantigi). Bunun yerine:

- Request body `await request.json()` ile ham JSON olarak okunur.
- `predictor.predict_one(payload, ...)` / `predict_batch(payload, ...)`
  dogrudan cagrilir; schema ihlalleri `FeatureSchemaError` olarak
  `inference` paketinden gelir.
- Bu sayede FastAPI'nin kendi otomatik 422 formati (farkli bir JSON sekli)
  devreye girmez -- TEK bir error response sekli (`{error_code, detail}`)
  garanti edilir.

## 3. Startup / Readiness (Fail-Closed)

`lifespan` context manager, servis basladiginda **tam olarak bir kez**
`FreightCostPredictor.load()` cagirir, ardindan sabit bir canary shipment
ile bir prediction calistirir (`prediction_validity == "valid"` ve finite
olmali). Basarisizlik durumunda:

- `app.state.predictor = None`, `app.state.ready = False`
- Hata loglanir, **process crash ETMEZ** (health endpoint hala "alive"
  doner)
- `GET /ready` -> 503, `POST /predict*` -> 503 (`get_predictor` dependency)

Bu, `stage13_stage14_handoff.json`'daki "Readiness check: TrustedBundleLoader.load()
basariyla TAMAMLANDI mi" gereksinimini karsilar.

## 4. Endpoint'ler

| Endpoint | Davranis |
|---|---|
| `GET /health` | Her zaman 200 -- process calisiyor mu |
| `GET /ready` | 200 (model_id/trial_id/artifact_version ile) veya 503 |
| `POST /predict?explain=&request_interval=` | `predict_one()`, her zaman 200 (invalid prediction da 200 + `prediction_validity="invalid"`) |
| `POST /predict/batch?explain=&request_interval=` | `predict_batch()`, atomic validation, max_batch_size=100 |

## 5. Exception -> HTTP Mapping (Contract Section 11, dogrulandi)

| Exception | Status | Test |
|---|---|---|
| `FeatureSchemaError` | 422 | `test_error_contract.py` (7 error code) |
| `PredictionValidationError` | 500 | `test_prediction_validation_error_maps_to_500` |
| `ArtifactIntegrityError` | 503 | `test_artifact_integrity_error_maps_to_503` |
| `ModelCompatibilityError` | 503 | `test_model_compatibility_error_maps_to_503` |

500/503 durumlari pratikte sadece startup'ta beklenir (contract Section
11); testler bunlari `app.dependency_overrides` ile simule ederek mapping'in
kendisini DOGRULAR -- gercek bir production tetiklenmesi beklenmez.

## 6. Logging

Her prediction icin INFO seviyesinde `model_id`/`trial_id`/`artifact_version`/
`prediction_validity`/`risk_flags` loglanir (`app.py: _log_result`).
Minimal Core schema'da PII yoktur (Stage 14 contract Section 13) --
raw shipment PII loglama riski beklenmemektedir.

## 7. Docker Topolojisi Karari (D-157 — Dedicated Service Degerlendirmesi)

Docker topolojisini belirlemek icin mevcut servisler ve ayri bir API
servisine duyulan ihtiyac incelendi. Inceleme (`compose.yaml`, `Dockerfile`): tek bir `ml-lab`
servisi var, `jupyter lab` calistiriyor, tum repo'yu bind-mount ediyor.

**Karar: Ayri bir Docker servisi OLUSTURULMADI.** Gerekce:
- Contract Section 14 acikca "mevcut ml-lab servisi reuse edilmeli" diyor.
- API kodu zaten bind-mount uzerinden container icinde erisilebilir;
  ayri bir image/servis sadece bakim yuku ekler, gercek bir izolasyon
  faydasi saglamaz (egitim/prototip baglaminda).
- Degisiklik: `compose.yaml`'a `127.0.0.1:8000:8000` port mapping'i ve
  `Dockerfile`'a `EXPOSE 8000` eklendi (additive, CMD degismedi -- jupyter
  hala birincil workflow).
- API, container icinde manuel olarak `uv run uvicorn api.app:app --app-dir
  labs/lab12 --host 0.0.0.0 --port 8000` ile baslatilabilir; test suite'i
  kendi subprocess'ini kendi (gecici) portunda baslatir (bkz.
  `tests/stage14/conftest.py: live_server`), boylece surekli calisan bir
  API process'ine bagimlilik yoktur.

## 8. Phase B Non-Access (Kod Seviyesinde)

`grep -rin "2015" labs/lab12/api/*.py` sadece `app.py`/`__init__.py`
docstring'lerindeki acik "bu modul 2015'e erismez" aciklamalarini
bulur -- kod icinde (endpoint, config, dosya yolu, env var) 2015 verisine
veya Protected Test'e giden HICBIR mekanizma yoktur. API yapisal olarak
sadece `BUNDLE_VERSION_DIR` (Stage 13 bundle'i) ve sabit canary shipment'i
bilir; 2006-2013 development-period disinda hicbir veri kaynagina referans
vermez.
