# LAB12 — Stage 05 Evaluation Contract

## 1. Evaluation Objective

Shipment-level Freight Cost (USD) tahmini için leakage-safe, reproducible bir evaluation
protokolü sabitlemek.

## 2. Development Population

Training (< 2014-01-01, 5551 shipment, 4987 eligible).

## 3. Train/Validation/Test Policy

Train: model development + training-only CV. Validation (2014): Stage 11'de frozen finalist
değerlendirmesi. Protected Test (2015): Stage 14'te tek seferlik final evaluation.

## 4. Internal CV Protocol

Expanding-Window, 4 fold (validation yılları 2010-2013), `gap_days=0`, calendar-aware,
group-aware (0 overlap doğrulandı).

## 5. Grouping Rules

Primary key: `ASN/DN #`. Her shipment tam olarak bir split'e ve (training içindeyse) ilgili
fold'lara group-aware biçimde atanır.

## 6. Temporal Gap Policy

Default: 0-day gap. 30/60-günlük senaryolar yalnızca **protokol tasarımı sensitivity
senaryoları** olarak belgelenmiştir — doğrulanmış label settlement lag değerleri değildir.

## 7. Target Label Availability

Gerçek bir freight settlement/booking timestamp bu veri setinde **yoktur.** `Scheduled
Delivery Date` bir proxy'dir. D-007 Conditional kalmaya devam eder.

## 8. Allowed Metrics

Stage 06+'da tanımlanacak (MAE/RMSE/vb., Stage 04'ten taşınan deneyler). Bu belge metrik
seçmez.

## 9. Preprocessing Fit Boundaries

Her fold için: preprocessing pipeline **yalnızca fold training data** üzerinde fit edilir;
fold validation data'ya sadece `transform` uygulanır. Validation(2014)/Test(2015) **asla** fit
için kullanılmaz.

## 10. Hyperparameter Tuning Restrictions

Stage 06-10: yalnızca training-only internal CV üzerinde. Validation(2014) hyperparameter
tuning için **kullanılmaz** (Stage 11'e kadar).

## 11. External Validation Usage

2014 Validation, Stage 11'de **önceden belirlenmiş finalistlerin** sınırlı değerlendirmesi
içindir — adaptif/tekrarlı model seçimi için değildir.

## 12. Test Evaluation Usage

2015 Protected Test, Stage 14'te **bir kez** kullanılacaktır.

## 13. Model Finalization Policy

Final refit stratejisi (Training-only vs Training+Validation), Stage 11'de model
sabitlendikten **sonra ve test erişiminden önce** kararlaştırılacaktır — bu belgede
**seçilmemiştir.**

## 14. Protocol Versioning

`protocol_version: stage05-v1`, deterministic protocol fingerprint ile (bkz.
`stage05_protocol_fingerprint.json`).

## 15. Leakage Prevention Invariants

Bkz. `docs/stage05_leakage_risk_register.md` ve notebook Section 13'teki 7 invariant kontrolü
(hepsi PASS).

## 16. Future Stage Integration

Stage 06-10: Training-only CV (bu contract'ı kullanır). Stage 11: Frozen 2014 evaluation.
Stage 12: Calibration, test tuning olmadan. Stage 13: Persistence. Stage 14: One-time test
evaluation.
