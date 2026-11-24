# LAB12 — Stage 14 Phase B: Final Evaluation Protocol

**Bu belge, 2015 Protected Test'e erisimden ONCE dondurulmustur.** Bu
belgenin SHA-256 fingerprint'i (`evaluation/freeze.py:compute_doc_fingerprint`),
`stage14_evaluation_freeze_manifest_v2.json`'a kaydedilir ve her unlock
denemesinde yeniden dogrulanir (`evaluation/gate.py`) -- bu belge
degisirse, unlock REDDEDILIR.

## 1. Population

- **Granularity:** Shipment-level (`ASN/DN #` = `Shipment_Key`), Stage 03.5
  ile ayni semantics.
- **Split membership:** `artifacts/stage05_split_manifest.csv`'nin
  `Split == "Protected_Test"` satirlari -- **frozen, Stage 05'te
  uretildi**, bu asamada yeniden hesaplanmadi.
- **Target eligibility:** Bir shipment group'u eligible'dir ancak ve
  ancak grubun TAM OLARAK BIR numeric (`pd.to_numeric` ile parse edilebilen)
  `Freight Cost (USD)` satiri varsa (`evaluation/population.py:resolve_shipment_targets`).
  Sifir numeric satir (referans-only) VEYA birden fazla numeric satir
  (ambiguous anchor) -> **ineligible, degerlendirme DISI**.
- **Duplicate shipment handling:** `drop_duplicates("ASN/DN #")` --
  her eligible shipment TAM OLARAK bir kez skorlanir.
- **Input schema:** Stage 07 Minimal Core (degismedi):
  `Line_Item_Qty_Sum`, `Line_Item_Value_Sum` (numeric, raw satirlarin
  SUM'u), `Shipment_Mode`, `INCO_Term`, `Country`, `Product_Group`
  (categorical, raw satirlarin FIRST'u) -- Stage 07'nin aggregation
  semantics'i (`numeric->sum()`, `categorical->first()`).
- **Prediction-time feature policy:** Hicbir yeni feature
  EKLENMEDI/degistirilmedi. `evaluation/population.py:resolve_shipment_features`,
  Stage 13'un inference contract'inin (`REQUIRED_SCHEMA_FIELDS`) BEKLEDIGI
  alanlari uretir -- Stage 13'un kendisi bu aggregation'i YAPMAZ (D-146),
  bu adim sadece evaluation katmaninda, raw satirlardan shipment-level
  kayida gecerken gereklidir.

## 2. Primary Metric

**MAE (USD)** -- `mean(|actual - prediction|)`, yalnizca `prediction_validity
== "valid"` olan shipment'lar uzerinde (bkz. Section 3, Invalid Prediction
Policy).

## 3. Secondary Metrics

| Metrik | Birim | Formul |
|---|---|---|
| RMSE | USD | `sqrt(mean((actual-prediction)^2))` |
| Median AE | USD | `median(\|actual-prediction\|)` |
| WAPE | % | `100 * sum(\|actual-prediction\|) / sum(\|actual\|)` |
| Bias | USD | `mean(prediction-actual)`; negatif = sistematik underprediction |
| P90 AE | USD | `percentile(\|actual-prediction\|, 90)` |
| P95 AE | USD | `percentile(\|actual-prediction\|, 95)` |
| Prediction Validity Rate | % | `100 * valid / total eligible` |
| Negative Prediction Count | count | raw (clip edilmemis) tahminlerden `<0` olanlarin sayisi |
| High-Cost MAE | USD | MAE, `actual >= HIGH_COST_THRESHOLD_USD` alt kumesinde |
| High-Cost Underprediction Rate | % | `100 * (prediction<actual) / n` (high-cost alt kumesinde) |

**Invalid Prediction Policy:** Stage 13'un D-149 karari DEGISMEDEN
uygulanir -- negatif/non-finite tahminler clip edilmez, `prediction_validity="invalid"`
olarak raporlanir ve MAE/RMSE/vb. hata metriklerinden HARIC TUTULUR (ama
`Prediction_Validity_Rate` paydasinda SAYILIR).

**Missing-value handling:** Metrik formullerinde NaN/missing deger YOKTUR
-- her eligible shipment'in tek bir numeric target'i ve Stage 13'un
schema'sinin kabul ettigi (missing-degere-izin-verilen ama missing-alana-izin-verilmeyen)
bir feature kaydi vardir.

## 4. High-Cost Threshold (Frozen, Provenance)

`HIGH_COST_THRESHOLD_USD = 23897.32` -- Stage 11'de, **2014 verisi
okunmadan ONCE**, 2006-2013 eligible development population'in (n=4987)
P90'i olarak dondurulmustur (`stage11_external_validation_results.md`
Section 5). Bu deger 2014 icin degismeden kullanildi ve **ayni frozen-before-the-period-is-read
politikasiyla**, 2015 icin de DEGISTIRILMEDEN/yeniden hesaplanmadan
kullanilacaktir.

## 5. Model & Preprocessing (Degismedi)

`FreightCostPredictor` (Stage 13, `labs/lab12/inference/`) TEK kaynak --
bu paket tarafindan reimplement EDILMEDI. Model retrain EDILMEDI,
preprocessing DEGISTIRILMEDI, feature set DEGISTIRILMEDI. Uncertainty/interval
cikisi KAPALI kalir (`request_interval` hicbir zaman cagirilmaz --
Phase B skorlamasi sadece point prediction kullanir).

## 6. Tek Seferlik Calisma Politikasi

`evaluation.gate.UnlockToken`, `PreUnlockGate.unlock()` tarafindan
uretilir ve `FinalEvaluationRunner.run()` tarafindan TAM OLARAK bir kez
tuketilir (`token.consume()`). Protected Test verisi, bir calisma
icinde EN FAZLA bir kez okunur. Zaten tamamlanmis bir rapor varsa,
`allow_rerun=True` + ayri bir onay OLMADAN yeniden calisma REDDEDILIR
(`AlreadyEvaluatedError`).

## 7. Mimari Ozet

| Modul | Sorumluluk |
|---|---|
| `contracts.py` | Frozen sabitler, exception'lar, metric/baseline spec'leri |
| `population.py` | Development/Protected population loader'lari (token-gated) |
| `baselines.py` | B1 (Global Mean), B4 (Hierarchical Median) |
| `metrics.py` | Tum frozen metric formulleri |
| `acceptance.py` | Teknik (business-SLA DEGIL) kabul siniflandirmasi |
| `freeze.py` | Evaluation code/protocol fingerprint, freeze manifest v2 |
| `gate.py` | PreUnlockGate -- her unlock-oncesi kontrol |
| `runner.py` | FinalEvaluationRunner -- gercek Phase B mantigi, SADECE gate'ten gecerek erisilebilir |
| `cli.py` | Ayri, acik unlock komutu (bu asamada CAGRILMADI) |
