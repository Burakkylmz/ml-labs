# LAB12 — Stage 06 Preprocessing Experiment Plan

## 1. Scope

Bu belge, Stage 06'da **hangi** preprocessing işlemlerinin denenmesi gerektiğini ve seçim
kararının **nasıl** verileceğini tanımlar. **Henüz seçilmiş bir preprocessing pipeline
içermez.**

## 2. Experiment Principles

- Her deney, Stage 04'teki gerçek istatistiksel kanıtlara dayanır.
- Her deney en az bir linear (Ridge) ve bir tree-based model üzerinde çalıştırılır — bir
  preprocessing yönteminin etkisi modelden bağımsız değildir.
- Capping/scaling/encoding parametreleri **yalnızca training fold** üzerinde fit edilir.
- Nihai seçim, aynı CV folds, aynı seed, aynı metrik seti üzerinde yapılır.

## 3. Missing Value Handling Candidates

| Candidate | Evidence | Status |
|---|---|---|
| No Imputation | Line_Item_Qty/Value_Sum %100 complete (Population C) | Pending Validation |
| Median Imputation | Weight_KG'de 23/4987 eksik, heavy-tailed | Pending Validation |
| Missing Indicator | Weight missingness INCO Term ile ilişkili (Stage 03.5) | Pending Validation |
| Exclusion of Structurally Unavailable Features | D-006 (Weight Unknown) | Pending Validation |

## 4. Encoding Candidates

| Feature | Candidate | Rationale |
|---|---|---|
| Shipment_Mode | OneHotEncoder + Explicit Unknown | Düşük cardinality (4+missing) |
| Vendor_INCO_Term | OneHotEncoder + Rare Category Grouping | 8 kategori, bazıları n<10 |
| Country | Rare Category Grouping / Native Categorical | 43 kategori (yüksek cardinality) |
| Product_Group | OneHotEncoder | 5 kategori |

`LabelEncoder` nominal feature'lar için **varsayılan olarak önerilmemektedir.**

## 5. Scaling Candidates

| Candidate | Rationale |
|---|---|
| No Scaling | Tree-based modeller için kontrol |
| StandardScaler | Standart Ridge seçimi, ama skew≈5.4 mean/std'yi bozabilir |
| RobustScaler | Median/IQR tabanlı, heavy-tail'e daha dayanıklı aday (kanıtlanmamış üstünlük) |
| MinMaxScaler | Max≈290k USD'lik tekil bir uç değere aşırı hassas olabilir |

## 6. Outlier Treatment Candidates

| Candidate | Note |
|---|---|
| Keep All Valid Observations | Kontrol adayı |
| IQR-Based Flagging | Diagnostic kolon, model girdisi değil |
| Quantile Capping | Threshold yalnızca training fold'dan |
| Logarithmic Transformation | Section 05 target transformation ile bağlantılı |
| Robust Scaling | Section 06 ile bağlantılı |

Extreme-but-valid shipment kaybı riski (**Business Question**, Stage 04 Section 08) açıkça
kaydedilmiştir.

## 7. Target Transformation Candidates

Original / Log-Transformed / Log1p-Transformed. Karşılaştırma: original-scale MAE/RMSE,
high-cost segment error, bias, retransformation behavior.

## 8. Feature Availability Restrictions

Weight_KG: Unknown (D-006) — varsayılan olarak ana feature set'inden **dışlanmıştır**, ayrı
sensitivity deneyi (EXP-03) ile test edilecektir. Line_Item_Qty/Value_Sum: Conditional (D-010).

## 9. Cross-Validation Requirements

Group-aware (ASN/DN #) K-Fold; aynı fold'lar tüm deneylerde (EXP-01...EXP-05) kullanılır; aynı
random seed (42).

## 10. Metric Definitions

Primary: MAE (original USD scale). Secondary: RMSE, High-Cost Segment MAE (>P90), Bias
(mean signed error).

## 11. Comparison Methodology

Fold-level metrik değerleri + ortalama/std; paired performans farkları; aynı estimator
settings. Korelasyonlu CV fold'ları üzerinden naif p-value hesaplanmaz.

## 12. Statistical Evidence Requirements

Her deney sonucu: fold-level dağılım, ortalama fark, (gerekirse) confidence interval,
computational cost, high-cost segment stabilitesi raporlanmalıdır.

## 13. Complexity & Runtime Considerations

Rare Category Grouping ve Native Categorical Handling, OneHotEncoder'a kıyasla farklı
boyutluluk/training time dengesi getirir — EXP-04 bunu ölçer.

## 14. Acceptance Criteria

Her deney için Stage 04 Section 10 Experiment Matrix'teki (`stage04_statistical_evidence.csv`)
`Acceptance_Criteria` kolonuna bakınız — küçük farklar "kazanan" ilan edilmeden önce
pratik önem (USD cinsinden) açısından değerlendirilmelidir.

## 15. Open Decisions

- D-006 (Weight) — domain confirmation olmadan EXP-03 sonucu tek başına karar
  verdirmeyecektir.
- D-010 (Qty/Value aggregation) — Stage 04'te hâlâ Pending; Stage 06 deneylerinden önce
  çözülmesi önerilir.
- Hangi tree-based model family'nin (Random Forest/XGBoost/LightGBM) deney setinde
  kullanılacağı henüz seçilmemiştir.
