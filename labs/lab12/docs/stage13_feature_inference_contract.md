# LAB12 — Stage 13 Feature Inference Contract

## 1. Feature Schema

Stage 07 Minimal Core: numeric=`[Line_Item_Qty_Sum, Line_Item_Value_Sum]`,
categorical=`[Shipment_Mode, INCO_Term, Country, Product_Group]`.

## 2. Required Fields

Tum 6 Minimal Core feature'i **required**'dir -- `FeatureSchema.required_fields`
tum feature'lari kapsar. Bir field eksikse `MISSING_REQUIRED_FIELD` ile
REJECTED (field presence, value missingness'ten AYRI kontrol edilir).

## 3. Nullable Fields

Tum feature'lar **value olarak** null/NaN olabilir -- bu durumda
preprocessing (median imputation / constant-fill "Missing") devreye girer.
Field'in KENDISI eksik olamaz, ama DEGERI eksik olabilir.

## 4. Numeric Validation

- String -> `INVALID_FIELD_TYPE` (sessiz coercion YOK, orn. "ten thousand" kabul edilmez).
- Infinity -> `INVALID_NUMERIC_VALUE`.
- Negatif -> `INVALID_NUMERIC_VALUE` (Line_Item_Qty_Sum/Value_Sum negatif olamaz).
- NaN -> missing olarak kabul edilir (imputation'a birakilir).

## 5. Categorical Validation

- Non-string -> `INVALID_FIELD_TYPE`.
- Null -> missing olarak kabul edilir (constant-fill "Missing").
- Unknown category (fitted encoder'in `categories_`'inde yok) -> **REJECTED DEGIL**,
  `UNKNOWN_CATEGORY` risk flag'i ile ACCEPTED (training contract'in
  `OneHotEncoder(handle_unknown="ignore")` politikasiyla tutarli).

## 6. Unknown Categories

Design karari: Stage 06/07 preprocessing contract'i zaten
`handle_unknown="ignore"` kullaniyor -- bu, "unknown category prediction'i
engellemesin" seklinde bir tasarim niyetidir. Stage 13 bunu SADECE bir risk
flag olarak yansitir, hard-reject etmez.

## 7. Feature Engineering Lineage

`Line_Item_Qty_Sum`/`Line_Item_Value_Sum`: raw line-item kayitlarinin
shipment-seviyesinde SUM aggregation'i (Stage 03.5/07). Stage 13, bu
aggregation'i yeniden implement ETMEZ -- canonical input zaten
shipment-seviyesindedir (bkz Section 13 "Inference Entry Contract": raw
line-item-to-shipment ETL'i Stage 13 kapsaminda DEGILDIR).

## 8. Shipment-Level Semantics

Bir shipment -> bir prediction. Cross-shipment aggregation veya duplicated
line-item aggregation inference sirasinda YAPILMAZ (zaten shipment-level
girdi alinir).

## 9. Feature Ordering

`FreightCostPredictor._predict_raw()`, `pd.DataFrame(cleaned_records,
columns=list(self.schema.all_features))` ile DAIMA explicit kolon sirasi
kullanir -- girdi dict'inin key sirasi **onemsizdir** (test edildi,
`08_reordered_keys`).

## 10. Training–Inference Parity

Training (Stage 11 full-dev refit) ile inference (Stage 13 predictor)
ayni `ColumnTransformer` (fitted, persist edilmis) kullanir -- farkli
encoding/imputation/scaling riski YOKTUR (ayni fitted object).

## 11. Invalid Input Handling

`INVALID_SHIPMENT_STRUCTURE` (non-dict), `MISSING_REQUIRED_FIELD`,
`UNKNOWN_FIELD` (strict schema), `INVALID_FIELD_TYPE`,
`INVALID_NUMERIC_VALUE` -- hepsi `FeatureSchemaError` ile REJECTED, sessiz
fallback YOK.

## 12. Known Availability Risks

D-006 (Weight_KG, Unknown) ve D-007 (label timestamp, Conditional) Minimal
Core schema'da zaten YOKTUR -- bu nedenle bir "unavailable feature" test
case'i olusturulamaz; risk, her prediction'da
`UNVERIFIED_FEATURE_AVAILABILITY` flag'i ile yapisal olarak disclose edilir.
