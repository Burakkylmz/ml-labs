# LAB12 — Stage 10 Search Space Rationale

## 1. Purpose

Bu belge, M04 (ExtraTrees) ve M05 (XGBoost) icin tanimlanan bounded search space'lerin
gerekcesini belgeler.

## 2. ExtraTrees Parameters

`n_estimators` (ensemble buyuklugu), `max_depth` (agac derinlik siniri), `min_samples_leaf`
(yaprak smoothing), `min_samples_split` (split complexity), `max_features` (feature
diversity).

## 3. ExtraTrees Search Bounds

`n_estimators: [80,120,200,300]`, `max_depth: [6,8,12,None]`, `min_samples_leaf:
[2,3,5,10]`, `min_samples_split: [2,5,10]`, `max_features: [0.6,0.8,1.0]`. `bootstrap=
false` sabit tutuldu (Stage 09 policy).

## 4. ExtraTrees Parameter Interactions

Gercek sensitivity sonuclari (`stage10_parameter_sensitivity.csv`): `max_depth` ile
Pooled MAE arasinda **guclu negatif korelasyon** (-0.84, derin agaclar bu orneklemde
daha iyi), `min_samples_leaf` ile **pozitif korelasyon** (+0.45, kucuk yaprak daha
iyi). En iyi trial (M04-T003), `max_depth=12` (at_max boundary) ve `min_samples_leaf=2`
(at_min boundary) kullaniyor -- search space'in bu yonde genisletilmesi gelecekte
degerlendirilebilir (ama bu, optimumun kesinlikle disarida oldugunu kanitlamaz).

## 5. XGBoost Parameters

`n_estimators`, `learning_rate`, `max_depth`, `min_child_weight`, `subsample`,
`colsample_bytree`, `reg_lambda`, `reg_alpha`, `gamma`.

## 6. XGBoost Search Bounds

9 parametre, her biri 3-4 deger -- 16 trial bu genis uzayin kucuk bir orneklemidir.

## 7. XGBoost Parameter Interactions

`min_child_weight` ile Pooled MAE arasinda guclu pozitif korelasyon (+0.70 -- kucuk
min_child_weight bu orneklemde daha iyi); `max_depth` ile negatif korelasyon (-0.54).
En iyi trial (M05-T000=referans) butun parametrelerde "interior" (boundary'de degil) --
search'un referanstan daha iyi bir nokta bulamadigini destekliyor.

## 8. Fixed Parameters

ExtraTrees: `bootstrap=False, random_state=42, n_jobs=2`. XGBoost:
`objective="reg:squarederror", tree_method="hist", random_state=42, n_jobs=2`.

## 9. Parameter Sampling Strategy

`sklearn.model_selection.ParameterSampler(random_state=42)` -- deterministic, frozen
before execution. Reference (T000) ayrica eklendi ve asla sample'lanan listeden
dedupe edilmedi (farkli key seti nedeniyle yapisal olarak garanti).

## 10. Interaction Coverage

16 trial, XGBoost'un 9-boyutlu uzayinda butun interaction'lari kapsayamaz --
`learning_rate x n_estimators` gibi iliskiler sadece descriptive olarak incelendi
(`stage10_parameter_interactions.csv`).

## 11. Runtime Considerations

128 fit toplam ~90-100 saniyede tamamlandi -- bu olcekte operasyonel bir engel yok.

## 12. Search-Space Limitations

16 trial/model, global optimum garantisi sunmaz. Cross-environment calistirmada
(local vs Docker) XGBoost icin farkli "en iyi trial" secildi (~%0.10 fark) -- bu,
search space'in ince-taneli (fine-grained) bir optimum bulmada XGBoost'un kendi
threading-duyarli hist algoritmasi tarafindan sinirlandigini gosteriyor.
