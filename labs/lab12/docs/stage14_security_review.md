# LAB12 — Stage 14 (Phase A) API Security Review

## 1. Threat Model Kapsami

Bu inceleme, Stage 13'un `TrustedBundleLoader` guvenlik modelini
DEGISTIRMEZ (D-144, D-156) -- sadece HTTP katmaninin bu modeli
zayiflatip zayiflatmadigini degerlendirir.

## 2. Arbitrary Model Path Kabul Edilmiyor (Contract Section 15)

| Yuzey | Sonuc |
|---|---|
| Request body alani (`model_path`, `bundle_path` vb.) | `UNKNOWN_FIELD` ile 422 REJECTED -- strict schema her alani kapsar |
| Query parametresi (`?bundle_path=...`) | FastAPI tarafindan hicbir handler argumanina baglanmaz, YOK SAYILIR |
| Environment variable | `api/config.py` icinde `os.environ`/`getenv` KULLANILMAZ (test: `test_bundle_path_is_a_fixed_constant_not_environment_derived`) |
| Path parameter | Hicbir route'ta path parametresi YOK (test: `test_no_endpoint_exposes_a_path_parameter`) |

`BUNDLE_ROOT`/`BUNDLE_VERSION_DIR`, modul import zamaninda `Path(__file__)`'dan
turetilen SABIT degerlerdir -- hicbir request bu degerleri degistiremez.

## 3. Tek, Uniform Error Sekli

Tum validasyon hatalari `{error_code, detail}` sekli ile doner (bkz.
`test_error_response_shape_is_uniform`). Bu, hata mesajlarinin dolayli
olarak ic sistem detaylarini (stack trace, dosya yolu) sizdirmasini
onler -- `detail` alani sadece `inference` paketinin kendi, onceden
tanimlanmis hata mesajini tasir.

## 4. Fail-Closed Startup

Bundle yuklenemezse (checksum/identity/dependency hatasi) servis
**traffic KABUL ETMEZ** -- `/predict*` 503 doner, `/health` process'in
ayakta oldugunu bildirir ama bu "hazir" anlamina gelmez. Bu, Stage 13'un
"integrity verified BEFORE joblib.load()" ilkesinin HTTP katmanindaki
dogal uzantisidir.

## 5. DoS Yuzeyi (Bilinen Sinirlama, Production-Onaylanmamis)

- `max_batch_size=100` ve `max_batch_explanations=10` tek bir request'in
  isleyebilecegi is yukunu sinirlar.
- **Rate limiting, authentication, ve request-per-second throttling bu
  Phase A kapsaminda IMPLEMENT EDILMEDI** -- bu prototype, egitim/dahili
  kullanim icindir, internet'e acik bir production deployment degildir.
  `stage14_phase_a_final_report.md`'de acikca bir sinirlama olarak
  belgelendi, GIZLENMEDI.

## 6. Dependency Supply Chain

`fastapi`, `uvicorn[standard]`, `httpx` `pyproject.toml`'a eklendi ve
`uv.lock` ile pinlendi (`uv lock` + `uv sync --locked`); surum secimi
rastgele degil, `uv`'nin kendi resolver'i uzerinden gecti, lockfile
commit'e hazir.

## 7. Known Risks (Degismeden Tasindi)

`stage13_stage14_handoff.json`'daki `Known_Risks` listesi (high-cost
underprediction, D-006/D-007, XGBoost instability, SLA yoklugu) Stage 14
API'sinde de GECERLIDIR -- bu liste API tarafindan degistirilmedi veya
gizlenmedi; her prediction'da `risk_flags` alani ayni bilgiyi tasir.
