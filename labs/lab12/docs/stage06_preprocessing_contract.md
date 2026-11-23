# LAB12 — Stage 06 Preprocessing Contract

## 1. Purpose and Non-Finality

Bu belge, Stage 07'ye taşınacak **aday** preprocessing politikalarını dondurur. **Bu bir
final production pipeline spesifikasyonu değildir** — Stage 07'de model seçimi
tamamlandığında, model-özgü kararlar (özellikle target transformation ve scaling)
yeniden değerlendirilebilir.

## 2. Frozen Feature Allowlist

Numeric: `Line_Item_Qty_Sum`, `Line_Item_Value_Sum`. Categorical: `Shipment_Mode`,
`INCO_Term`, `Country`, `Product_Group`. Bu liste Stage 07'ye **değiştirilmeden** taşınır;
genişletme/azaltma yeni bir qualification/evidence turu gerektirir.

## 3. Excluded Features and Rationale

`Weight_KG`: D-006 (Unknown availability) nedeniyle ana setten dışlandı; yalnızca
sensitivity analizinde (Challenge 1) kullanıldı. Hedef-türevi herhangi bir feature (`Freight
Cost (USD)`'den hesaplanan hiçbir alan) ana sete dahil edilmedi.

## 4. Missing Value Policy

Numeric: `SimpleImputer(strategy="median")`, fold-training'den fit. Categorical:
`SimpleImputer(strategy="constant", fill_value="Missing")`. EXP-01 sonucu Inconclusive
olduğundan Missing Indicator **varsayılan pipeline'a dahil edilmemiştir** (gerekirse
Stage 07'de `Weight_KG` eklenirse yeniden değerlendirilir).

## 5. Categorical Encoding Policy

**Tercih edilen: `OneHotEncoder` + rare-category grouping (`min_frequency=10`,
`handle_unknown="ignore"`).** `OrdinalEncoder` **reddedilmiştir** (hem semantik hem ölçülen
kanıt — bkz. `stage06_experiment_results.md` Section 4).

## 6. Scaling Policy (Model-Dependent)

Random Forest / ağaç-tabanlı modeller: scaling **gereksiz** (ölçülen fark <0.4 USD).
Ridge / doğrusal modeller: `MinMaxScaler` adayı en iyi ölçülen sonucu verdi, ancak tek bir
uç değere duyarlılığı nedeniyle **"Acceptable" (Preferred değil)** kategorisindedir;
Stage 07'de final model doğrusal bir aile ise bu karar yeniden gözden geçirilmelidir.

## 7. Outlier Treatment Policy

`QuantileCapper(lower_q=0.01, upper_q=0.99)`, fold-training'den fit, yalnızca **numeric
feature'lara** uygulanır. **Target değeri hiçbir zaman capping/removal'a uğramaz.** Ridge
için Acceptable, Random Forest için Inconclusive (gerekirse atlanabilir).

## 8. Target Transformation Policy

**Varsayılan: Original scale.** Log/log1p dönüşümü **model-özgüdür**: Ridge için kesin
olarak reddedilmiştir (retransformation bias, pooled MAE 8001→59,303 USD); Random Forest
için marjinal olarak kabul edilebilir (Acceptable) fakat "Preferred" ilan edilecek kadar
büyük bir fark değildir. Stage 07'de final model ailesi netleşmeden bu politika
**değiştirilmemelidir.**

## 9. Unknown Category Handling at Inference

`OneHotEncoder(handle_unknown="ignore")` veya `OrdinalEncoder(unknown_value=-1)` — hangi
encoder seçilirse (OrdinalEncoder reddedildiği için fiilen OneHotEncoder) bu davranış
**zorunludur**, çünkü fold-training'de görülmeyen `Country` değerleri validation'da
tekrarlı olarak gözlendi (3-5 unseen kategori/fold).

## 10. CV Fitting Boundary Rule

**Zorunlu kural:** Her preprocessing parametresi (imputer median'ı, encoder kategorileri,
scaler istatistikleri, capper quantile'ları) **yalnızca fold training verisinden** fit
edilir; fold validation/Stage05 Validation(2014)/Protected Test(2015)'e sadece `transform`
uygulanır. Bu kural notebook içinde programatik olarak doğrulanmıştır (OOF shipment
key'lerinin Training split'ine ait olduğu kontrolü).

## 11. Pipeline Architecture Contract

```
ColumnTransformer([
    ("numeric", Pipeline([imputer, (capper?), (scaler?)]), NUMERIC_FEATURES),
    ("categorical", Pipeline([imputer, encoder]), CATEGORICAL_FEATURES),
])
Pipeline([("preprocessor", ...), ("model", probe_estimator)])
  -> optionally wrapped in TransformedTargetRegressor(func=log/log1p, inverse_func=exp/expm1)
```

Bu mimari Stage 07'ye **yapısal olarak** taşınır; model eklenmesi/değiştirilmesi sadece
`("model", ...)` adımını değiştirir, `ColumnTransformer` şeması sabit kalır.

## 12. Probe Estimator Specification (Not Final Models)

Ridge(`alpha=10.0`) ve RandomForestRegressor(`n_estimators=80, max_depth=8,
min_samples_leaf=3, random_state=42, n_jobs=2`) — **bunlar sadece preprocessing etkisini
ayırt etmek için sabit "cetvel" modelleridir, Stage 07'nin final model adayları değildir.**
Stage 07, bu iki estimator'ın ötesinde (XGBoost, LightGBM, vb.) yeni bir model seçim süreci
yürütecektir.

## 13. Reproducibility Requirements

`random_seed=42` (config'den). Referans pipeline iki kez fit edilip tahminlerin
`np.allclose` ile eşleştiği doğrulanmıştır. Multi-threaded RandomForest (`n_jobs=2`) için
bit-bazında birebir eşitlik **garanti edilmez** (bilinen, kabul edilen sınırlama);
`np.allclose` toleransı yeterli kabul edilmiştir.

## 14. Decisions Deferred to Stage 07

- D-006 (Weight_KG availability) — hâlâ Unknown; sensitivity-only kullanım sürüyor.
- D-010 (Line Item Qty/Value aggregation across product types) — hâlâ Pending.
- Hangi model ailesinin (Ridge, Random Forest, XGBoost, LightGBM, vb.) final adayı
  olacağı — Stage 06, sadece 2 probe estimator ile preprocessing'i karşılaştırdı.
- Target transformation ve scaling kararları, final model ailesi netleşmeden
  **koşulludur** (bkz. Section 6, 8).

## 15. Engineering Decision Cross-References

D-033 — D-042 (bkz. `engineering_decisions.md`): Stage 05 protokol doğrulaması, feature
allowlist dondurma, pipeline mimarisi, EXP-01...EXP-05 kararları, reproducibility
doğrulaması.

## 16. Stage 07 Handoff Checklist

- [x] Frozen feature allowlist (Section 2) sabit.
- [x] Missing value / encoding / outlier politikaları (Section 4, 5, 7) belirlendi.
- [ ] Scaling ve target transformation politikaları (Section 6, 8) **model seçimi
      sonrası yeniden teyit edilmelidir.**
- [x] CV fitting boundary kuralı (Section 10) programatik olarak doğrulandı.
- [x] Reproducibility doğrulandı (local + Docker, 0 hata, 0 uyarı).
- [ ] D-006, D-010 açık kararlar — Stage 07 başlamadan önce domain confirmation önerilir
      (zorunlu değil, risk kaydı olarak taşınır).
