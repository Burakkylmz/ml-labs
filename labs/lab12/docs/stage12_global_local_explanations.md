# LAB12 — Stage 12 Global & Local Explanations

## 1. Global Importance (Tree, Impurity-Based)

Encoded-dimension ranking (`stage12_tree_importance.csv`) -- categorical
source feature'larin importance'i dummy columns arasinda bolunur,
yorumlama icin Section 3/4'teki grouped/permutation sonuclarina bakilmalidir.

## 2. Permutation Importance

Development population (n=4987) uzerinde, MAE scoring, n_repeats=10:

| Raw Feature | Importance Mean (USD) |
|---|---:|
| Line_Item_Qty_Sum | 4,329.66 |
| Line_Item_Value_Sum | 4,056.44 |
| Country | 2,461.00 |
| INCO_Term | 1,382.01 |
| Product_Group | 1,356.92 |
| Shipment_Mode | 732.93 |

**Not:** Ilk denemede bu feature'larin tumu yanlislikla NEGATIF cikti --
kod incelemesinde bunun sklearn `permutation_importance`'in zaten dogru
isaretli (`MAE_permuted - MAE_baseline`) degerini gereksiz yere negate eden
bir hatadan kaynaklandigi tespit edildi ve duzeltildi (bkz
`stage12_explanation_reliability.md` Section 9).

## 3. SHAP Global Importance

Mean Absolute SHAP (encoded, top-3): `Line_Item_Value_Sum` (4369.95),
`Line_Item_Qty_Sum` (3556.98), `INCO_Term_EXW` (1789.78).

## 4. Feature Group Attribution (Grouped/Semantic SHAP)

Row-wise signed sum (dummy columns) -> mean |.| per raw feature
(`stage12_grouped_shap_importance.csv`). Ranking Permutation Importance ile
**Spearman=0.943** uyum gosterir (n=6 raw feature).

## 5. SHAP Additivity

Max |prediction - (baseline + sum(phi))| = **1.89e-10 USD** (n=200,
floating-point tolerance icinde). Explanation baseline $E[f(X)]$ = 10,456.22
USD -- **bu, Stage 08'in B1 Global Mean baseline'iyla sayisal olarak
cakismaktadir (coincidental ama beklenen: her ikisi de training target
ortalamasini temsil eder), Stage 08'in business baseline KARARI ile ayni
kavram DEGILDIR.**

## 6. Local Cases

| Case | Predicted (USD) | Not |
|---|---:|---|
| A — Typical | 7,745.63 | Development, median magnitude |
| B — High Predicted | 96,820.07 | Development, en yuksek tahmin |
| C — Low Predicted | 1,449.82 | Development, en dusuk tahmin |
| D — High Abs Error (2014) | 88,109.69 (actual=9,857.35, err=78,252.34) | Stage 11 2014 residual'inden secildi |
| E — Model Disagreement (2014) | ExtraTrees=73,232.78 vs XGBoost=95,654.76 (diff=22,421.97) | Stage 11'in largest-disagreement bulgusuyla ayni shipment (ASN-23441) |

## 7. Waterfall Interpretations

Her case icin base_value'dan predicted degere giden en etkili 8 feature
gosterildi. **"Feature X degistirilirse maliyet SHAP degeri kadar degisir"**
ifadesi her yerde acikca YANLIS olarak isaretlendi -- bu causal inference
gerektirir ve bu notebookta yapilmamistir.

## 8. Model Disagreements

Case E'de ExtraTrees ve XGBoost'un ayni shipment icin farkli top-feature
contribution uretmesi gozlemlendi -- bagging vs boosting mimarisi farki
olarak yorumlandi, hata olarak degil.

## 9. High-Cost Case Diagnostics

Case D (actual=9,857.35, predicted=88,109.69) ekstrem bir overprediction
ornegidir -- Stage 11'in genel underprediction egiliminin TEK ISTISNASI
olarak degil, yuksek-varyans bir vaka olarak dokumante edildi.

## 10. Conclusions

Permutation Importance ve Grouped SHAP guclu bir sinyal uyumu gosteriyor
(Spearman=0.943). SHAP additivity dogrulandi. Local case studies, model
attribution'in ne anlama geldigini (ve neyin YANLIS yorum oldugunu) acik
ornekler uzerinden gostermistir.
