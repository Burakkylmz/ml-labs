# LAB12 — Stage 13 Model Inference Contract

**Bu belge Stage 13 implementasyonu DEGILDIR -- yalnizca bir sonraki asamanin
tasarim sozlesmesidir. Stage 12'de production endpoint olusturulmamistir.**

## 1. Purpose

Stage 13'un (Model Persistence & Inference) nasil bir contract uzerinde
insa edilecegini tanimlamak.

## 2. Frozen Point Predictor

M04-T003 (ExtraTrees), full eligible development (2006-2013, n=4987)
uzerinde fit edildi. Stage 11 External MAE (2014) = 6,485.63 USD.
Refit identity check: Stage 11 reference predictions ile **0.000000 USD**
fark.

## 3. Feature Schema

`stage07-v1-minimal-core`: numeric=`[Line_Item_Qty_Sum, Line_Item_Value_Sum]`,
categorical=`[Shipment_Mode, INCO_Term, Country, Product_Group]`.

## 4. Preprocessing Contract

Median imputation (numeric), constant-fill "Missing" + rare-category OneHot
(`min_frequency=10`, `handle_unknown="ignore"`), scaling yok.

## 5. Model Configuration

`{n_estimators=200, min_samples_split=10, min_samples_leaf=2, max_features=0.8,
max_depth=12, bootstrap=False, random_state=42}`.

## 6. Model Versioning

`model_id=M04-T003`, `feature_schema_version=stage07-v1-minimal-core`,
`dataset_fingerprint=9cffdb4a...578a`, `stage05_protocol_fingerprint=b87ca0fd...`.

## 7. Prediction Output

`prediction_usd` (float, raw scale, no target transformation).

## 8. Prediction Validation

Girdi feature'lari schema'ya uymali; bilinmeyen kategoriler `OneHotEncoder`'in
`handle_unknown="ignore"` davranisina dusmelidir (tum-sifir dummy satiri) --
bu durum `UNKNOWN_CATEGORY` risk flag'i ile isaretlenmelidir.

## 9. Explainability Output

Status: **Approved for Stage 13 Prototype.** Methods: `tree_importance`,
`permutation_importance`, `shap_tree_explainer`. Attribution schema version:
`stage12-v1`. SHAP background policy: `tree_path_dependent` (default),
`interventional` (documented alternative, farkli sonuc uretebilir).

## 10. Explanation Metadata

Her explanation output'u, hangi background policy ve hangi model
version'iyla uretildigini acikca tasimalidir (background sensitivity
Section 13 bulgusu nedeniyle).

## 11. Uncertainty Status

**Research Only / Disabled by Default.** `interval_outcome=Production
Interval Not Approved`. Object B (research calibration replicas), Object
A'nin (frozen point predictor) version-matched bir calibration artifact'i
DEGILDIR.

## 12. Calibration Dependency

Herhangi bir gelecekteki interval output'u, Object A ile AYNI fitted
estimator'a (full development, 2006-2013) dayanan, dogru bicimde
version-matched bir calibration seti gerektirir -- bu su an MEVCUT DEGILDIR.

## 13. Interval Availability Policy

`interval_lower_usd`/`interval_upper_usd` alanlari, gecerli bir calibration
contract'i olusturulana kadar **NULL/disabled** olmalidir.

## 14. Risk Flags

`UNKNOWN_CATEGORY`, `MISSING_CRITICAL_FEATURE`,
`PREDICTION_OUTSIDE_REFERENCE_RANGE`, `HIGH_UNCERTAINTY`,
`INTERVAL_NOT_CALIBRATED`, `PREDICTION_TIME_AVAILABILITY_UNVERIFIED`.
Bu flag'ler training-only diagnostics ve onaylanmis contract'tan uretilir --
label-based veya validation-based post-hoc threshold KULLANILMAZ.

## 15. Error Handling

Eksik kritik feature veya finite-olmayan girdi degeri, tahmin yerine
acik bir hata/risk flag dondurmelidir (sessiz fallback yok).

## 16. Reproducibility

ExtraTrees (M04-T003): tam reproducibility (local/Docker byte-exact).
XGBoost (M05-T000, sadece secondary comparison icin): cross-environment
instability bilinmektedir -- herhangi bir XGBoost cikisi, hangi ortamda
hesaplandigini acikca belirtmelidir.

## 17. Security & Data Handling

Shipment-level girdi verisi PII icermez (ASN/DN #, Country, Shipment Mode,
Product Group, miktarlar). Prediction loglari, kullanicinin diger
uygulamalarindan izole saklanmalidir (bu Stage'in kapsaminda implement
edilmemistir, sadece tasarim notu).

## 18. Protected Test Policy

2015 Protected Test, Stage 14'e kadar **tamamen kapali kalmalidir** -- bu
sozlesme veya Stage 13 implementasyonu 2015 verisine erismemelidir.

## 19. Stage 13 Entry Criteria

**CONDITIONAL GO.** Point predictor + explainability: Approved for
Prototype. Uncertainty/interval: Research Only, varsayilan olarak devre
disi. Business-approved SLA hala YOK -- Stage 13 "production-ready" iddiasi
URETEMEZ.
