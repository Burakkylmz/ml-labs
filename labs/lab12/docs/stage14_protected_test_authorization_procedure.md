# LAB12 — Stage 14 Phase B: Protected-Test Authorization Procedure

## 1. Normal Execution Mode (Her Zaman Gecerli)

`pytest`, Stage 14 notebook'u, veya FastAPI servisinin normal calismasi
**hicbir zaman** 2015 Protected Test'e erisemez. Bu, convention'dan degil
yapidan kaynaklanir (`evaluation/population.py:load_protected_population`,
`UnlockToken` parametresi zorunlu kilar -- bkz.
`tests/stage14_evaluation/test_structural_safety.py`).

## 2. Unlock Komutu

```
uv run python -m evaluation.cli unlock --confirm-phrase "I AUTHORIZE 2015 PROTECTED TEST EVALUATION"
```

**Bu komut, bu hazirlik asamasinda hicbir sekilde CALISTIRILMADI.**

## 3. Unlock-Oncesi Kontroller (`PreUnlockGate.run_checks`)

Sirayla, HEPSI gecmeli:

1. **Explicit authorization** -- `--confirm-phrase` TAM OLARAK
   `"I AUTHORIZE 2015 PROTECTED TEST EVALUATION"` metnine esit olmali.
2. **No silent rerun** -- `stage14_final_evaluation_report.json` zaten
   varsa, `--allow-rerun` OLMADAN REDDEDILIR.
3. **Frozen model identity** -- freeze manifest v2'deki `model_id`/`trial_id`/
   `model_artifact_sha256`, `evaluation/contracts.py`'nin sabitleriyle
   eslesmeli.
4. **Live bundle unchanged** -- `stage13_model_bundle/v1/manifest.json`'in
   KENDI sha256'si ayni sabitle eslesmeli (bundle'in freeze SONRASI
   degismedigini dogrular).
5. **Dataset fingerprint** -- freeze manifest v2'deki `dataset_sha256`,
   Stage 05'in sabit degeriyle eslesmeli.
6. **Stage 05 protocol fingerprint** -- ayni sekilde eslesmeli.
7. **Frozen evaluation code & protocol** -- `evaluation/` paketinin VE
   `stage14_final_evaluation_protocol.md` + `stage14_metric_baseline_contract.md`'nin
   SHA-256'si, freeze manifest v2'de kayitli degerle eslesmeli (herhangi
   bir dosya degisirse REDDEDILIR).
8. **Canonical runtime** -- calistirilan ortamin Python (major.minor) ve
   sklearn (exact) versiyonlari, freeze manifest v2'dekiyle eslesmeli.
9. **Audit log writable** -- audit log dizinine yazilabildigi dogrulanir.

**Herhangi biri basarisiz olursa:** `GateError` veya
`AlreadyEvaluatedError` raise edilir, `UnlockToken` URETILMEZ, 2015
verisine hicbir satir OKUNMAZ. Basarisizlik, audit log'a
`pre_unlock_checks_failed` olarak kaydedilir.

## 4. Unlock Sonrasi

Her kontrol gectiginde: `UnlockToken` uretilir (audit log:
`unlock_token_issued`), `FinalEvaluationRunner.run(token)` cagirilir,
token **tam olarak bir kez** tuketilir (`token.consume()`), 2015 verisi
**bir kez** okunur, rapor `stage14_final_evaluation_report.json`'a yazilir.

## 5. Bu Asamada Ne Yapildi, Ne Yapilmadi

| Eylem | Durum |
|---|---|
| `evaluation/` paketi implement edildi | YAPILDI |
| Synthetic/development-only testler yazildi ve PASSED | YAPILDI |
| `stage14_evaluation_freeze_manifest_v2.json` olusturuldu | YAPILDI |
| `PreUnlockGate.unlock()`, REAL authorization phrase + REAL dataset path ile cagrildi | **YAPILMADI** |
| `evaluation.cli` CLI'si CALISTIRILDI | **YAPILMADI** |
| 2015 satiri OKUNDU | **YAPILMADI** |
| `stage14_final_evaluation_report.json` OLUSTURULDU | **YOK (henuz uretilmedi)** |
