# LAB12 — Stage 07 Feature Contract

## 1. Contract Version

stage07-v1

## 2. Dataset Fingerprint

SHA-256: `9cffdb4ab8c6135b0f999c91b3a5c6e88a3c3dfc28c7c85feb9e97f986e3578a` -- Stage
01-03 -> Stage 05 -> Stage 06 -> Stage 07 boyunca degismeden dogrulandi.

## 3. Stage 05 Protocol Fingerprint

`b87ca0fde5fd9ddef45f191a0bb1c3e4e2a014b9c9641be5e8d20bb2458935e7` -- notebook icinde
yeniden hesaplanip birebir eslesti (Critical Gate PASSED).

## 4. Observation Unit

Shipment (`ASN/DN #`) -- Stage 03.5 Shipment Data Contract korunmustur.

## 5. Target Definition

`Freight Cost (USD)` -- hicbir feature'a girdi olarak kullanilmadi (mandatory exclusion,
programatik olarak dogrulandi).

## 6. Prediction-Time Feature Policy

Her feature icin `Prediction_Time_Availability` durumu Section 04 feature catalogunda
(`stage07_feature_catalog.csv`) kayitlidir: Confirmed Available / Conditionally Available /
Unknown / Excluded. Yuksek predictive signal, availability kosulunu gecersiz kilmaz
(D-006 Weight ornegi).

## 7. Core Feature Set (Candidate A)

Numeric: `Line_Item_Qty_Sum`, `Line_Item_Value_Sum`. Categorical: `Shipment_Mode`,
`INCO_Term`, `Country`, `Product_Group`. **Decision: Recommended for Next Stage.**
Pooled MAE: Ridge=7974.86 USD, RF=6151.74 USD.

## 8. Extended Feature Set (Candidate B)

Core + `Line_Item_Count`, `Distinct_Item_Description_Count`, `Distinct_Molecule_Count`,
`Line_Item_Value_Mean`, `Line_Item_Value_Max`, `Value_Dispersion` (numeric); +
`Managed_By`, `Fulfill_Via`, `First_Line_Designation` (categorical). **Decision:
Acceptable Alternative.** Pooled MAE: Ridge=7921.12 USD, RF=6239.42 USD (RF icin F0'dan
daha kotu -- Value grubu nedeniyle, bkz `stage07_ablation_study.md`).

## 9. Reduced Feature Set (Candidate C)

Filter `SelectKBest(mutual_info_regression, k=10)`, Extended Feature Set'in encoded
(post-OneHot) uzayinda. **Decision: Conditional** -- encoded-feature-level secimdir, raw
feature listesi olarak tam ifade edilemez (bkz `stage07_feature_selection_evidence.md`
Section 11, Jaccard stability=0.483).

## 10. Conditional Sensitivity Set (Candidate D)

Extended Feature Set + `Weight_KG` (D-006 Unknown) [+ `Scheduled_Month`/`Scheduled_Quarter`
(D-007 Conditional) ayri senaryo olarak]. **Decision: Sensitivity-Only -- production-ready
olarak degerlendirilmez**, performans etkisi (RF icin -542 USD gibi buyuk bir iyilesme)
D-006/D-007 kararlarini DEGISTIRMEZ.

## 11. Feature Lineage

Tam izlenebilirlik `stage07_feature_lineage.csv`'dedir (14 feature, Source_Columns ->
Transformation -> Aggregation -> Business_Justification -> Prediction_Time_Requirement
-> Data_Quality_Risk -> Leakage_Risk).

## 12. Aggregation Rules

Numeric: `sum()` (Qty/Value toplami), `mean()`/`max()` (Value istatistikleri), `count()`/
`nunique()` (Composition). Categorical: `first()` (shipment-level tekil deger).
Stage 03.5 aggregation semantics'i korunmustur.

## 13. Preprocessing Dependencies

Frozen (Stage 06 "Preferred" tier'dan tasindi): `SimpleImputer(strategy="median")` +
`StandardScaler` (numeric); `SimpleImputer(strategy="constant", fill_value="Missing")` +
`OneHotEncoder(handle_unknown="ignore", min_frequency=10)` (categorical). Tum feature-set
karsilastirmalarinda **sabit** (Frozen Configuration Rule) -- sadece `ColumnTransformer`
kolon listeleri degisti.

## 14. Model Family Compatibility

Sadece **Ridge** (alpha=10.0) ve **Random Forest** (n_estimators=80, max_depth=8,
min_samples_leaf=3) probe estimator'lari ile dogrulandi (Stage 06'dan degismeden).
**Bu, final model secimi degildir** -- Stage 09, farkli model aileleri (XGBoost,
LightGBM, vb.) ile yeniden degerlendirme yapacaktir.

## 15. Schema Validation Requirements

Her feature config, `ColumnTransformer`'in `numeric_features`/`categorical_features`
listeleriyle birebir eslesmelidir; `Has_Numeric_Target` filtresi her zaman fold-training/
validation populasyonuna ayri ayri uygulanmalidir (frozen membership degismez).

## 16. Inference Requirements

Tum feature'lar stateless ve deterministiktir -- inference zamaninda sadece ilgili
shipment'in kendi kayitlari uzerinden hesaplanabilir (baska bir shipment'in bilgisine
ihtiyac yoktur, Stage 03.5'teki 0 cross-shipment dependency bulgusuyla tutarli).

## 17. Known Limitations

- D-006 (Weight) ve D-010 (Qty/Value aggregation) hala acik.
- Line_Item_Value tabanli feature'lar %13.97 bundling riski tasir.
- Sadece 4 CV fold -- istatistiksel guven sinirli.
- One-factor-at-a-time ablation, grup-arasi etkilesim etkilerini yakalamaz.
- Sadece 2 probe estimator ile dogrulandi.

## 18. Stage 08 Handoff

Stage 08 (Baseline Development), Candidate A (Minimal Core) ile baslamalidir -- en
guvenli, en az riskli baslangic noktasi. Candidate B, engineered feature'larin katkisini
test etmek icin ikinci bir baseline olarak kullanilabilir.

## 19. Stage 09 Handoff

Stage 09 (Model Training & Benchmarking), Candidate A/B/C'yi farkli model aileleriyle
yeniden degerlendirmelidir -- Stage 07'nin Ridge/RF-ozel bulgulari (ozellikle Value
grubunun RF icin redundant olmasi) baska model aileleri icin farkli sonuclanabilir.
Candidate D, SADECE sensitivity analizi icin kullanilmali, production karsilastirmasina
DAHIL EDILMEMELIDIR.
