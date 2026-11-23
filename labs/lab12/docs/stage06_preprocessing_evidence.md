# LAB12 — Stage 06 Preprocessing Evidence

## 1. Scope and Purpose

Bu belge, Stage 06 notebook'unda üretilen **ham kanıtları** (diagnostics) toplar. Karar
gerekçeleri `stage06_experiment_results.md`'de, dondurulmuş politika `stage06_preprocessing_contract.md`'dedir. Bu belge **hiçbir karar içermez** — yalnızca ölçülen durumu raporlar.

## 2. Stage 05 Protocol Recovery Verification

Dataset SHA-256 (`9cffdb4ab...578a`) Stage 01-03 → Stage 05 → Stage 06 boyunca değişmeden
doğrulandı. Stage 05 protokol fingerprint'i (`b87ca0fd...8935e`) notebook içinde yeniden
hesaplanıp birebir eşleştiği doğrulandı. Frozen CV fold manifest (`stage05_cv_fold_manifest.csv`,
16975 satır) hiç değiştirilmeden okundu.

## 3. Feature Allowlist and Exclusions

Ana probe feature set: `Line_Item_Qty_Sum`, `Line_Item_Value_Sum` (numeric); `Shipment_Mode`,
`INCO_Term`, `Country`, `Product_Group` (categorical). `Weight_KG`, D-006 (Unknown
availability) nedeniyle ana setten **dışlandı**, yalnızca Challenge 1'de sensitivity amaçlı
kullanıldı.

## 4. Missing Value Evidence (EXP-01)

| Feature | Missing Rate (%) |
|---|---|
| Line_Item_Qty_Sum | 0.00 |
| Line_Item_Value_Sum | 0.00 |
| Shipment_Mode | 4.23 |
| INCO_Term | 0.00 |
| Country | 0.00 |
| Product_Group | 0.00 |

Ana numeric feature'larda **gerçek eksik değer yok** (fold-training düzeyinde de 4 fold'un
hepsinde 0.0 doğrulandı). `Shipment_Mode`'daki %4.23 eksiklik, zaten kategorik pipeline'ın
`constant="Missing"` adımıyla ele alınıyor; `SimpleImputer(strategy="median")`'ın hiçbir
gerçek imputation yapmadığı doğrulandı.

## 5. Categorical Cardinality and Encoding Evidence (EXP-02)

| Candidate | Output Feature Count |
|---|---|
| one_hot | 57 |
| ordinal | 6 |
| rare_category_one_hot (min_frequency=10) | 43 |

`Country`'nin yüksek kardinalitesi (43 ülke), OneHot'ta boyut patlamasına (57 kolon)
neden oluyor; rare-category grouping bunu 43'e indiriyor. Fold başına unseen-category sayımı:
Fold 1-3'te `Country` için 3-5 unseen kategori gözlendi (fold-training setinde hiç görülmeyen,
validation'da çıkan ülkeler) — `handle_unknown="ignore"` / `unknown_value=-1` ile ele alındığı
doğrulandı.

## 6. Numeric Distribution and Scaling Evidence (EXP-03)

| Feature | Mean | Std | Median | Skew |
|---|---|---|---|---|
| Line_Item_Qty_Sum | 25,660.74 | 48,479.05 | 5,478.0 | 3.94 |
| Line_Item_Value_Sum | 219,803.17 | 388,672.17 | 74,200.0 | 4.06 |

Her iki feature de ağır sağa çarpık (skew≈4) — mean/std tabanlı `StandardScaler`'ın bu
dağılımları tam normalize edemeyeceği teyit edildi; bu, karar aşamasında dikkate alınması
gereken bir gözlemdir (karar değil).

## 7. Outlier / Quantile Capping Evidence (EXP-04)

| Feature | P1 | P99 | Capped Fraction (%) |
|---|---|---|---|
| Line_Item_Qty_Sum | 7.0 | 233,547.4 | 1.99 |
| Line_Item_Value_Sum | 95.1 | 2,158,059.6 | 2.01 |

Capped fraction ~%2 (beklenen, çünkü P1/P99 tanımı gereği budama). Capping, **training
fold'dan öğrenilen eşiklerle** yapıldı; validation'a sadece `transform` (clip) uygulandı.
Target'ın kendisi **hiçbir zaman** capping/removal'a uğramadı.

## 8. Target Distribution and Transformation Evidence (EXP-05)

| Transform | Skewness | Excess Kurtosis |
|---|---|---|
| original | 5.36 | 53.86 |
| log | -0.37 | 0.34 |
| log1p | -0.35 | 0.19 |

Log/log1p dönüşümü, dağılımı istatistiksel olarak büyük ölçüde normalleştiriyor (skew≈5.36 →
≈-0.37). Ancak bu, **tahmin performansının otomatik olarak iyileşeceği anlamına gelmez** —
bkz. `stage06_experiment_results.md` Section 7 (retransformation bias bulgusu).

## 9. Weight_KG Sensitivity-Only Evidence (Challenge 1)

`Weight_KG`, D-006 kapsamında ana sete eklendiğinde (sadece bu challenge'da), fold training
setlerinde gerçek eksik değerler içeriyor (Stage 03.5'te belirlendiği gibi). Missing
Indicator eklenmesi, Random Forest üzerinde ölçülebilir fakat küçük bir fark üretti; Ridge
üzerinde ölçülebilir fark üretmedi (ayrıntılı sayılar: `stage06_experiment_results.md`
Section 11).

## 10. Rare-Category Threshold Sensitivity Evidence (Challenge 2)

`min_frequency` değeri 5/10/20/50 arasında değiştirildiğinde çıkış boyutu ve Ridge Pooled MAE
nasıl değişti — ayrıntılı tablo `stage06_experiment_results.md` Section 12'dedir. Bu belge
sadece threshold'un **output dimension'ı monoton olarak değiştirdiğini** gözlem olarak kaydeder.

## 11. Pipeline Architecture Evidence

`sklearn.Pipeline` + `ColumnTransformer` mimarisi, tüm 5 deney boyunca **tek bir tutarlı
API** ile çalıştı. Her fold için **yeni bir pipeline instance'ı** oluşturulup fit edildi (fold'lar
arası state sızıntısı riski yapısal olarak ortadan kaldırıldı).

## 12. Probe Estimator Behavior Evidence

Ridge(alpha=10.0): tüm fit'ler <0.02s (önemsiz hesaplama maliyeti). RandomForestRegressor
(n_estimators=80, max_depth=8, min_samples_leaf=3, n_jobs=2): en büyük fold'da (train=4152)
tek fit ~1-3s. Toplam 124 CV fit, standalone script üzerinde **66.7 saniyede** tamamlandı.

## 13. Fold-Level Stability Evidence

Smoke-test referans konfigürasyonunda (median imputation, one_hot, no scaling, Ridge) fold
başına MAE: Fold 1: 6922.19, Fold 2: 7037.34, Fold 3: 8923.32, Fold 4: 8955.30. Fold'lar
arası ~%30'luk dalgalanma, yalnızca 4 fold'un istatistiksel güvenini sınırladığını teyit eder
(Stage 05'te zaten not edilen risk).

## 14. Negative Raw Prediction Evidence

Tüm deneylerde, clip-öncesi (raw) negatif tahmin sayıları kaydedildi ve **tüm adaylara
tutarlı biçimde uygulanan non-negative clip politikası** doğrulandı (hiçbir aday için özel
muamele yapılmadı).

## 15. Leakage Audit Evidence

`stage06_oof_predictions.csv`'deki (91,056 satır) tüm shipment key'lerin Training split'ine
ait olduğu, kod içinde programatik bir `issubset` kontrolüyle doğrulandı. 2014/2015 target
değerlerine bu notebook'ta **hiçbir hücrede** erişilmedi.

## 16. Reproducibility Evidence

Referans pipeline (median/one_hot/no-scaling/Ridge) iki kez yeniden fit edildi; tahminler
`np.allclose` ile birebir eşleşti (`reproducible_predictions_on_rerun: true`). Local (`uv run`)
ve Docker (`ml-lab` container) ortamlarında ayrı ayrı "temiz kernel" execution'ları **0 hata,
0 uyarı** ile tamamlandı; dataset hash her iki ortamda da değişmeden kaldı.

## 17. Summary of Evidence-Based Findings

- Ana feature set'te gerçek missing value yok → EXP-01 kanıtı zayıf/sıfır farklılık öngörür.
- `Country`'nin yüksek kardinalitesi encoding boyutunu önemli ölçüde etkiler.
- Numeric feature'lar ağır sağa çarpık; scaling'in model ailesine göre farklı davranması
  beklenir (Ridge ölçek-hassas, Random Forest ölçek-bağımsız).
- Target aşırı çarpık (skew≈5.36); log dönüşümü dağılımı normalleştirir ama bu otomatik
  performans iyileştirmesi garanti etmez.
- Tüm pipeline'lar leakage-safe şekilde fold-training-only fit edildi ve bu programatik
  olarak doğrulandı.
