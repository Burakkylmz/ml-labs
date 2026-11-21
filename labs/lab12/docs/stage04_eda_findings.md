# LAB12 — Stage 04 EDA Findings

## 1. Executive Summary

Stage 04, Shipment Data Contract (Stage 03.5) üzerinde, önceden sabitlenmiş bir **EDA
Isolation Protocol** (cutoff: 2013-12-31) altında kapsamlı bir istatistiksel keşif
gerçekleştirmiştir. Freight Cost hedefi güçlü sağa-çarpık ve ağır-kuyruklu bulunmuştur
(skewness≈5.36, excess kurtosis≈53.9). Weight (Kilograms) gerçek ama nonlinear bir sinyal
taşımaktadır (Spearman ρ≈0.73) ama prediction-time availability'si hâlâ doğrulanamamıştır.
INCOTERM-temelli selection bias, tamamen bağımsız bir historical alt-kümede (Population B/C)
**yeniden doğrulanmıştır.** Hiçbir preprocessing yöntemi seçilmemiş, yalnızca test edilebilir
hipotezler ve bir 5-deneyli Stage 06 deney matrisi üretilmiştir.

## 2. Dataset & Shipment Contract

SCMS Delivery History (SHA-256 doğrulandı, Stage 01-03 ile birebir eşleşti). Shipment Data
Contract (Stage 03.5): observation unit = shipment, primary key = `ASN/DN #`, 0 contract
violation (hiçbir shipment'ta >1 numeric anchor).

## 3. EDA Isolation Protocol

Cutoff = **2013-12-31**, `Scheduled Delivery Date` temelli, **target dağılımına bakılmadan**
önceden belirlendi. `Scheduled Delivery Date`'in business-valid prediction-time timing'i hâlâ
`Conditional`'dır (D-007) — bu alan burada yalnızca **geçici bir proxy** olarak kullanılmıştır.

## 4. Analysis Population

| Popülasyon | Tanım | N |
|---|---|---:|
| A — Structural Audit | Tüm shipment'lar | 7030 |
| B — EDA Historical | Sched Date ≤ cutoff | 5551 |
| C — Labeled EDA | B ∩ numeric positive target | 4987 |
| D — Protected Future | Sched Date > cutoff | 1479 |

Population D, hiçbir target-dependent analizde kullanılmamıştır (notebook içinde explicit
assert ile doğrulandı).

## 5. Target Distribution

Count=4987, Mean≈10456 USD, Median≈5820 USD, Skewness≈5.36, Excess Kurtosis≈53.9, P95≈33230
USD, P99≈76398 USD, Max≈289653 USD. Ortalama, median'ın ~1.8 katı — güçlü sağa-çarpıklık.

## 6. Numerical Feature Analysis

- **Weight_KG** (DIAGNOSTIC ONLY, D-006 Unknown): Pearson r≈0.14, Spearman ρ≈0.73, log-log
  Pearson r≈0.73 — zayıf linear ama güçlü monoton/çarpımsal ilişki.
- **Line_Item_Qty_Sum**: Spearman ρ≈0.64 — prediction-time available, aggregation rule D-010
  Pending.
- **Line_Item_Value_Sum**: Spearman ρ≈0.70 — aynı şekilde.
- Qty_Sum ve Value_Sum arasında olası multicollinearity — feature removal kararı
  **alınmamıştır.**

## 7. Categorical Feature Analysis

Shipment Mode (Air n=3411, Truck n=792, Air Charter n=324, Ocean n=249) ve INCO Term (8
kategori) arasında medyan freight cost farklılıkları gözlenmiştir. Air vs Truck için
Mann-Whitney U: p≈0.0002 (istatistiksel olarak anlamlı), ama medyan farkı (~1140 USD)
**practical significance** açısından ayrıca değerlendirilmelidir.

## 8. Outlier Diagnostics

IQR upper fence ≈30696 USD; Population C'nin **%5.8'i** bu sınırın üzerinde. Bu uç değerler
tüm Shipment Mode'larda dağılmış durumda (tek bir moda yoğunlaşmamış) — bu, gerçek operasyonel
kayıtlar olabileceğine işaret eder (kanıtlanmamış bir gözlem). **Hiçbir satır silinmemiş veya
capping uygulanmamıştır.**

## 9. Temporal Stability

Median Freight Cost 2006'da ≈2830 USD'den 2013'te ≈7568 USD'ye yükselmiştir (~2.7x).
Numeric-target coverage aynı dönemde %82.7'den %96.0'a yükselmiştir. Bu artışların kesin nedeni
(inflation, fuel price, vb.) bu veri kümesinde **doğrudan gözlenmemiştir** — nedensel bir iddia
yapılmamıştır.

## 10. Selection Bias

Target-eligible ve non-eligible shipment popülasyonlarının INCOTERM kompozisyonu **belirgin
biçimde farklıdır** — bu, Stage 03.5'in bütün-dataset bulgusunun, tamamen bağımsız bir
historical alt-kümede de doğrulandığını gösterir (daha güçlü bir kanıt).

## 11. Statistical Evidence

5 maddelik Experiment Matrix (EXP-01...EXP-05) oluşturulmuştur — her biri Hypothesis, Candidate
Methods, Model Family, Primary/Secondary Metrics, Evaluation Protocol, Leakage Control ve
Acceptance Criteria içerir (bkz. `stage04_statistical_evidence.csv`).

## 12. Engineering Implications

- Target heavy-tail → log transformation **test edilebilir bir hipotezdir**, zorunlu değildir.
- Weight'in gerçek sinyali var ama availability riski nedeniyle ana feature set'inden
  **varsayılan olarak dışlanmıştır** (D-006 ile tutarlı).
- Line Item Qty/Value aggregation'ı (D-010) çözülmeden bu feature'lar kesinleştirilemez.
- Outlier'lar silinmemeli; capping yalnızca training fold üzerinde fit edilerek test
  edilmelidir (Stage 06).

## 13. Feature Availability Constraints

Weight_KG: Unknown Availability / Diagnostic Only. Line_Item_Qty_Sum/Value_Sum: Conditionally
Available (D-010). Shipment_Mode: Conditionally Available (360 satır eksik). INCO_Term/
Country/Product_Group: Available.

## 14. Key Risks

1. Weight availability hâlâ doğrulanamadı.
2. Line Item Qty/Value aggregation kuralı hâlâ Pending.
3. Temporal distribution shift (hem cost seviyesi hem coverage) gözlemlendi — Stage 05 split
   tasarımını etkilemeli.
4. Selection bias modelleme boyunca izlenmelidir.

## 15. Limitations

- `Scheduled Delivery Date`'in business-valid prediction-time olduğu kesin kanıtlanmamıştır.
- Observation independence (shipment-level) varsayımı, tekrarlanan vendor'lar veya ortak
  procurement olayları nedeniyle zayıflayabilir — bu notebook'ta ayrıca test edilmemiştir.
- Bootstrap CI'lar (Advanced Challenge 2) standart shipment-level resampling kullanır; cluster
  dependence varsa gerçek belirsizlik daha büyük olabilir.

## 16. Stage 05 Recommendations

- Split, `ASN/DN #` üzerinde **group-aware** olmalı.
- Chronological split, temporal trend (Section 9) göz önüne alınarak tasarlanmalı.
- 2015 kısmi yıl olduğundan held-out test döneminde dikkatle ele alınmalı.

## 17. Stage 06 Recommendations

`docs/stage06_preprocessing_experiment_plan.md`'deki 5 deney (EXP-01...EXP-05), aynı CV folds,
aynı seed, en az 1 linear + 1 tree-based model üzerinde çalıştırılmalıdır.

## 18. Stage 07 Recommendations

Feature Engineering adayları: Row_Count (shipment item count, prediction-time available),
calendar features (Conditional, D-007'ye bağlı), Shipment Mode × INCO Term interaction (test
edilebilir hipotez). Product diversity adayı **null bulgu** olarak not edilmiştir (0 varyans).
Weight-based feature'lar D-006 çözülmeden gated kalmalıdır.
