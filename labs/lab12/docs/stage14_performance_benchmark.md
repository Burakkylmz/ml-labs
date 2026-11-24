# LAB12 — Stage 14 (Phase A) Performance Benchmark

Ham veri: `artifacts/stage14_performance_benchmark.json` (notebook
tarafindan uretildi, `lab12_stage14_api_deployment.ipynb` Section 10).
Yontem: `TestClient` (in-process ASGI, network stack YOK) uzerinden
gercek Stage 13 bundle'ina karsi `time.perf_counter()` ile olculen
wall-clock latency, n=20-40 tekrar.

## 1. Sonuclar (Local, Python 3.11.15)

| Senaryo | p50 (ms) | p95 (ms) |
|---|---|---|
| single, explain=false | 41.5 | 44.3 |
| single, explain=true | 51.5 | 80.9 |
| batch=1, explain=false | 42.1 | 55.3 |
| batch=10, explain=false | 40.7 | 44.0 |
| batch=100, explain=false | 42.5 | 67.1 |
| batch=10, explain=true | 139.1 | 160.0 |

## 2. Gercek Bulgu (D-163): Latency Batch Size'tan BAGIMSIZ

`batch=1` ile `batch=100` arasinda p50 latency istatistiksel olarak
AYIRT EDILEMEZ (~40-43ms). Bu, beklenen "batch size arttikca latency
artar" sezgisine AYKIRI gorunuyor ama tutarli bir aciklamasi var:
`ExtraTreesRegressor.predict()`, `n_jobs=2` ile her cagrida sabit bir
thread-pool dispatch maliyeti odemektedir; bu maliyet, 1-100 satir
araliginda, gercek hesaplama suresine kiyasla DOMINANT'tir. Sonuc: bu
batch size araliginda, tek tek 100 request yerine 1 batch request
gondermek latency acisindan ANLAMLI bir kazanc SAGLAMAZ (ama network
round-trip sayisini azaltarak baska bir fayda saglar).

## 3. Explainability Maliyeti

`explain=true`, satir basina ~10ms ek maliyet getiriyor (`shap.TreeExplainer`).
`max_batch_explanations=10` siniri (Stage 13, D-150), bu maliyetin
`explain=true` + buyuk batch kombinasyonuyla kontrolsuz buyumesini
onlemek icin dogrudan gerekcelendirilmis durumda -- bu benchmark o
gerekceyi SAYISAL olarak dogruluyor.

## 4. Docker vs Local

| Senaryo | Local p50 (ms) | Docker p50 (ms) |
|---|---|---|
| single, explain=false | 41.5 | 72.2 |
| batch=100, explain=false | 42.5 | 64.4 |

Docker (Docker Desktop/WSL2, bu host'ta) ~1.5-2x daha yavas -- bu
virtualizasyon overhead'idir, kod veya model farki DEGILDIR. Prediction
degerleri arasindaki fark hala ~1e-13 USD seviyesinde (D-162), latency
farkindan BAGIMSIZ.

## 5. Sinirlama

Bu benchmark **tek kullanicili, sirali** cagrilari olcer.
Concurrency/throughput testi `test_live_server_handles_concurrent_requests`
(20 eszamanli request, tumunun 200 dondugu dogrulandi) ile sinirli
kapsamda yapildi -- gercek bir load-test (sustained RPS, saturation
point) Phase A kapsaminda DEGILDIR ve production-ready bir SLA iddiasi
YAPILMAMAKTADIR.
