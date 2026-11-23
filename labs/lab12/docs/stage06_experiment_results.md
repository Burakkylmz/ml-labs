# LAB12 — Stage 06 Experiment Results

## 1. Scope

Bu belge, `stage06_preprocessing_evidence.md`'deki ham kanıtlar üzerinden yürütülen 5
kontrollü deneyin (EXP-01...EXP-05) **ölçülen sonuçlarını ve karşılaştırmalı
yorumlarını** raporlar. Tüm sonuçlar Stage 05'in dondurulmuş 4-fold Expanding-Window CV
protokolü üzerinde, training-only (2006-2013) verilerle üretilmiştir.

## 2. CV Protocol Reuse Confirmation

`stage05_protocol_fingerprint.json` ile bu notebook'ta yeniden hesaplanan fingerprint
(`b87ca0fd...8935e`) birebir eşleşti. Fold boyutları: Fold 1 (train=1735, val=780), Fold 2
(train=2515, val=776), Fold 3 (train=3291, val=861), Fold 4 (train=4152, val=835).

## 3. EXP-01 Results — Missing Value Handling

| Candidate | Estimator | Pooled MAE |
|---|---|---|
| median | Ridge | 8001.52 |
| median_with_indicator | Ridge | 8001.52 |
| median | Random_Forest | 6155.81 |
| median_with_indicator | Random_Forest | 6154.66 |

**Karar: Inconclusive / Deferred.** Ridge'de fark **tam olarak sıfır** (Missing Indicator
kolonu, gerçek eksik değer olmadığı için sabit/dejenere — Ridge katsayısı anlamsız). Random
Forest'ta fark (-1.08 USD pooled) pratik önemsiz. Ana feature set'te missing value
problemi fiilen yok; bu deney EXP-tasarımının doğruluğunu teyit etti ama ayırt edici bir
sinyal üretmedi.

## 4. EXP-02 Results — Categorical Encoding

| Candidate | Estimator | Pooled MAE |
|---|---|---|
| one_hot | Ridge | 8001.52 |
| ordinal | Ridge | 8259.28 |
| rare_category_one_hot | Ridge | 7959.65 |
| one_hot | Random_Forest | 6155.81 |
| ordinal | Random_Forest | 6160.71 |
| rare_category_one_hot | Random_Forest | 6151.90 |

**Karar: Ordinal reddedildi (hem semantik hem ölçülen kanıt).** Ordinal, Ridge'de +257.76
USD (pooled) daha kötü — mantıksal olarak da beklenen bir sonuç, çünkü `Country`/`INCO_Term`
gibi nominal feature'lara yapay bir sıralama dayatmak, Ridge'in doğrusal katsayı
yorumunu bozar. Rare-category grouping, her iki estimatörde de en iyi veya en yakın ikinci
sonucu verdi ve boyutu one_hot'un 57'sinden 43'e indirdi — **tercih edilen aday.**

## 5. EXP-03 Results — Feature Scaling

| Candidate | Ridge Pooled MAE | Random_Forest Pooled MAE |
|---|---|---|
| none | 8001.52 | 6155.81 |
| standard | 7993.14 | 6155.66 |
| robust | 7999.16 | 6155.62 |
| minmax | 7691.07 | 6155.50 |

**Karar: Model-Dependent.** Random Forest'ta fark pratik olarak sıfır (<0.4 USD aralığında)
— ağaç-tabanlı modellerin ölçek-bağımsızlığı doğrulandı. Ridge'de MinMaxScaler en iyi
sonucu verdi (-310.45 USD, none'a göre); bu, tek bir aşırı değerin (≈290k USD) min-max
normalizasyonunu bozabileceği teorik riskine **rağmen** ölçülen en iyi performans. Karar:
Ridge için MinMaxScaler aday olarak not edilir, ancak tek bir uç değere duyarlılığı
nedeniyle "Preferred" değil "Acceptable" kategorisinde bırakılmıştır.

## 6. EXP-04 Results — Outlier Treatment

| Candidate | Ridge Pooled MAE | Random_Forest Pooled MAE |
|---|---|---|
| keep | 8001.52 | 6155.81 |
| feature_iqr_capping | 7755.65 | 6155.62 |

**Karar: Ridge için Acceptable, Random Forest için Inconclusive.** Capping, Ridge'de
-245.87 USD pooled iyileşme sağladı (ağır sağa çarpık feature'ların Ridge'in doğrusal
duyarlılığını bozma riskini azaltması beklenen bir etki). Random Forest'ta fark önemsiz
(<0.2 USD) — split noktaları quantile-tabanlı olduğundan beklenen sonuç.

## 7. EXP-05 Results — Target Transformation (Kritik Bulgu)

| Candidate | Ridge Pooled MAE | Random_Forest Pooled MAE |
|---|---|---|
| original | 8001.52 | 6155.81 |
| log | **59,303.40** | 6069.22 |
| log1p | **59,084.12** | 6062.80 |

**Karar: Ridge için log/log1p KESİNLİKLE REDDEDİLDİ (Rejected); Random Forest için
Acceptable (marjinal iyileşme).**

**Düzeltilmiş/derinleştirilmiş bulgu (OOF prediction-level re-analiz, Stage 07 inceleme
sürecinde tespit edildi):** Pooled MAE blowup'u (8001.52 → 59,303.40 USD) **uniform bir
"retransformation bias" değil** — çok daha spesifik bir mekanizma:

- **Median absolute error Ridge+log için aslında DAHA İYİ** (3489.0 USD) **original
  scale'den** (4963.5 USD). Yani tipik/medyan shipment için log-transform doğru yönde
  çalışıyor.
- Ancak **3252 OOF tahminin sadece 7'si (%0.2)** 1,000,000 USD'yi aşan absürt tahminler
  üretiyor (en kötüsü: gerçek değer 43,548 USD iken tahmin **139,007,382 USD**). Bu 7
  tahmin, toplam MAE'nin **%80.1'ini** oluşturuyor (top-5 error sum / total error sum).
- Bu extreme tahminler **neredeyse tamamen Fold 2'de** yoğunlaşıyor: Fold 2 RMSE=5,004,844
  ve Bias=-200,312 USD, diğer fold'larda (1,3,4) RMSE 30,689-56,626 USD aralığında kalıyor
  — yani Fold 2, diğer 3 fold'dan **~100x** daha kötü.
- Mekanizma: Ridge log-uzayında fit edildiğinde, Fold 2'nin training verisinde nadir görülen
  bir feature kombinasyonu için orta büyüklükte bir log-space hata üretiyor; `np.exp()`
  geri-dönüşümü bu hatayı **katlanarak** büyütüyor (log-space'te ~birkaç birimlik bir sapma,
  dollar-space'te milyonlarca USD'lik bir sapmaya dönüşebilir).

**Sonuç olarak bu bulgu, hem "exponential inverse transformation amplification" hem de
"fold-specific instability" hem de "target transformation objective mismatch" (Ridge
log-uzayda squared-error'ı minimize ediyor, bu yaklaşık olarak medyan/relative hatayı
minimize eder; ama USD-space MAE ortalama hataya dayanır ve bir kaç ekstrem outlier
tarafından domine edilebilir) açıklamalarının **birleşimidir** — tek bir genel
"retransformation bias" ifadesi bu mekanizmayı tam yansıtmaz.

Random Forest'ta log/log1p küçük ama tutarlı bir iyileşme sağlıyor (-86-93 USD pooled) ve
bu tip extreme blowup'lar gözlenmedi — ağaç-tabanlı split'lerin ekstrapolasyona karşı
yapısal olarak daha dayanıklı olması bekleniyordu.

**Bu bulgunun pratik sonucu:** Target transformation kararı **tek bir "kazanan" ile
özetlenemez** — model ailesine göre tamamen ters sonuç verir, ve Ridge+log için MAE
blowup'u **birkaç fold-spesifik extreme tahminin** eseridir, genel bir dağılım-çapında
bozulma değildir. Stage 07'de hangi model ailesi seçilirse, target transformation kararı
o model ailesine özgü olarak yeniden değerlendirilmelidir; bu Stage 07'nin kapsamı
değildir.

## 8. Paired Fold-Delta Comparisons Summary

| Experiment | Candidate | Estimator | Mean Δ MAE | Folds Candidate Better / Reference Better |
|---|---|---|---|---|
| EXP-02 | ordinal | Ridge | +254.69 | 1 / 3 |
| EXP-02 | rare_category_one_hot | Ridge | -41.78 | 3 / 1 |
| EXP-03 | minmax | Ridge | -319.42 | 4 / 0 |
| EXP-04 | feature_iqr_capping | Ridge | -249.17 | 4 / 0 |
| EXP-05 | log | Ridge | **+53,556.62** | 0 / 4 |
| EXP-05 | log | Random_Forest | -90.62 | 2 / 2 |

MinMaxScaler ve IQR-capping, Ridge için **4 fold'un 4'ünde de** tutarlı şekilde reference'tan
daha iyi — bu, fold-fold gürültüsüne göre güvenilir bir sinyal (korelasyonlu fold'lar
üzerinden formal p-value hesaplanmadı, ama yön tutarlılığı güçlü bir pratik kanıttır).
Log transform, Ridge için **4 fold'un 4'ünde de** tutarlı şekilde kötü — bu da güçlü,
tutarlı bir "rejected" sinyalidir.

## 9. High-Cost Segment (P90+) Error Analysis

Fold-training P90 eşiği kullanılarak hesaplanan high-cost segment MAE, tüm deneyler
boyunca Random Forest için ~18,530-18,630 USD, Ridge için ~23,208-24,938 USD aralığında
kaldı (segment ortalama/std: bkz. `stage06_segment_error_analysis.csv`). Ordinal encoding,
Ridge'in high-cost segment hatasını da (24,937.52 vs 23,208.38) kötüleştirdi — EXP-02
kararını destekleyen ek kanıt.

## 10. Model-Dependent Divergence Summary (Ridge vs Random Forest)

Random Forest, tüm 5 deney boyunca Ridge'den tutarlı şekilde daha düşük pooled MAE verdi
(~6060-6160 vs ~7690-8260 USD) — bu PoC aşamasında ağaç-tabanlı modellerin bu feature seti
üzerinde doğrusal modellerden daha güçlü olduğuna işaret eder (Stage 04'teki nonlinear/
monotonic Weight-Freight ilişkisi bulgusuyla tutarlı). Bu, henüz final model seçimi
**değildir** — sadece iki sabit "probe" estimator'ın karşılaştırmalı davranışıdır.

## 11. Advanced Challenge 1 Results — Weight Missingness Sensitivity

`Weight_KG` ana sete eklenip Missing Indicator ile/without karşılaştırıldığında (D-006
sensitivity-only): Random Forest'ta indicator eklenmesi küçük bir fark üretti; Ridge'de
ölçülebilir fark yok. Bu, D-006'nın Stage 07'de çözülmeden bırakılmasının EXP-01 ana sonucu
üzerinde risk oluşturmadığını teyit eder.

## 12. Advanced Challenge 2 Results — Rare-Category Threshold Sensitivity

`min_frequency ∈ {5, 10, 20, 50}` için çıkış boyutu monoton olarak küçüldü (daha yüksek
threshold → daha az kategori → daha düşük boyut); Ridge pooled MAE, threshold'lar arasında
görece stabil kaldı (EXP-02'nin `min_frequency=10` seçiminin keskin bir eşik olmadığını
gösterir).

## 13. Advanced Challenge 3 Results — Scaling-Estimator Interaction

Ridge ve Random Forest'ın aynı scaling adayı için pooled MAE farkı (Ridge − RF) tüm
scaling adaylarında ~1500-1850 USD aralığında kaldı — scaling seçiminin kendisi bu farkı
kapatmıyor; iki model ailesi arasındaki temel performans farkı scaling'den bağımsız.

## 14. Advanced Challenge 4 Results — Log-Target Tail Error Study

High-cost segment MAE'si (P90+), log/log1p altında Random Forest için marjinal olarak
iyileşirken Ridge için **aşırı derecede kötüleşti** (retransformation bias, bkz. Section 7)
— tail-segment hatası genel pooled MAE bulgusuyla tam tutarlı.

## 15. Decision Matrix

| Experiment | Preferred | Acceptable | Rejected | Inconclusive/Deferred | Model-Dependent |
|---|---|---|---|---|---|
| EXP-01 (Missing) | — | — | — | ✓ | — |
| EXP-02 (Encoding) | rare_category_one_hot | one_hot | ordinal | — | — |
| EXP-03 (Scaling) | — | minmax (Ridge) | — | — | ✓ |
| EXP-04 (Outlier) | — | feature_iqr_capping (Ridge) | — | ✓ (RF) | — |
| EXP-05 (Target) | — | log/log1p (RF only) | log/log1p (Ridge) | — | ✓ |

## 16. Known Limitations of the Results

- Yalnızca 4 CV fold (2010-2013) — istatistiksel güven sınırlı, fold-fold MAE
  dalgalanması ~%30.
- One-factor-at-a-time tasarım, dimension'lar arası etkileşim etkilerini (örn.
  scaling×target-transform) ölçmez.
- Sadece 2 probe estimator (Ridge, Random Forest) test edildi; XGBoost/LightGBM gibi
  diğer model aileleri için bu sonuçlar genellenemez.
- Korelasyonlu fold'lar üzerinden formal istatistiksel anlamlılık testi (p-value)
  hesaplanmadı — yön tutarlılığı (Folds_Where_Candidate_Better) pratik kanıt olarak
  kullanıldı.
