# LAB12 — Stage 14 (Phase A) Validation Results

## 1. Test Suite Ozeti

| Katman | Dosya Sayisi | Test Sayisi |
|---|---|---|
| Stage 13 regresyon (degismedi, yeniden calistirildi) | 9 | 48 |
| Stage 14 contract-based API tests (`TestClient`, in-process ASGI) | 8 | 37 |
| Stage 14 Docker/live-server integration tests (gercek `uvicorn` subprocess, gercek HTTP) | 1 | 5 |
| **Toplam** | **17** | **90** |

## 2. Calistirma Sonuclari

| Ortam | Python | Sonuc |
|---|---|---|
| Local | 3.11.15 | **90/90 PASSED** |
| Docker (`ml-lab` container, ayni bundle, ayni kod) | 3.11.18 | **90/90 PASSED** |

Komut (her iki ortamda da ayni): `pytest labs/lab12/tests/stage13 labs/lab12/tests/stage14`.

## 3. Gercek Bulgu: D-162 (Floating-Point Noise, API Katmaninda)

Ilk calistirmada local'de 1, Docker'da 2 test basarisiz oldu --
`prediction_usd` alaninda ~1e-13 - ~3e-13 USD farkla (`==` ile). Kok
neden Stage 13'un D-154'u ile AYNI: ExtraTrees `n_jobs=2` ile
predict() sirasinda farkli batch sekilleri (batch-of-N vs N x
batch-of-1, veya iki ayri yuklenen instance) thread-order'a bagli
summation farkliligi uretiyor. Duzeltme: ilgili 3 assertion, projenin
geri kalaniyla TUTARLI bicimde 1e-6 USD tolerance'a cevrildi
(`test_predict_batch.py`, `test_model_parity.py`). Diger TUM alanlar
(model_id, risk_flags, prediction_validity, vb.) hala TAM esitlik ile
kontrol ediliyor -- sadece float deger tolerance aldi.

## 4. Cross-Environment Prediction Parity

`lab12_stage14_api_deployment.ipynb`, AYNI canary shipment icin, hem
local hem Docker calistirmasinda `TestClient` uzerinden prediction
uretir ve sonucu `artifacts/stage14_cross_environment_parity.json`'a
yazar (her calistirma kendi ortamini overwrite etmeden birikir):

| Ortam | `prediction_usd` |
|---|---|
| Local (Python 3.11.15) | 3727.5129395800723 |
| Docker (Python 3.11.18) | 3727.512939580072 |

Fark = 3e-13 USD, tolerance (1e-6 USD) icinde. Ayni bundle (refit YOK,
SHA-256 ayni) -- D-155'in Stage 14 API katmanindaki dogrulamasi. Ayrica
host'tan container icindeki gercek `uvicorn` surecine dogrudan `curl` ile
atilan ad-hoc bir dogrulama da (manuel validasyon sirasinda) ayni sonucu
(3e-13 USD fark) verdi.

## 5. Model Bundle Integrity

`model.joblib` SHA-256 = `71a451344f8b88a8d440d90325b88668cd3a8c16379425f5a4e95061bed77782`
Phase A'nin BASINDA ve SONUNDA dogrulandi -- degismedi (bkz.
`stage14_pretest_freeze_manifest.json`).

## 6. Kapsanan Contract Gereksinimleri

| Contract Section | Test Dosyasi |
|---|---|
| §4 Input Schema (strict, required fields) | `test_predict_single.py`, `test_predict_batch.py` |
| §6 Single Prediction (200/422/invalid-as-200) | `test_predict_single.py` |
| §7 Batch (atomic validation, max_batch_size) | `test_predict_batch.py` |
| §8 Explainability batch limit | `test_predict_batch.py`, `test_explainability_endpoint.py` |
| §9 Interval policy (never returns bounds) | `test_interval_policy_endpoint.py` |
| §10/§11 Error codes + HTTP status mapping | `test_error_contract.py` |
| §12 Health & Readiness | `test_health_readiness.py` |
| §15 Security (no arbitrary path) | `test_security.py` |
| §16 Docker integration | `test_docker_live_server.py` |
| §17 Model parity | `test_model_parity.py` |
