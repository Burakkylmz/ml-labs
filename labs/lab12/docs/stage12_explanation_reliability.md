# LAB12 — Stage 12 Explanation Reliability

## 1. Reliability Objective

SHAP/Permutation Importance degerlerinin ne kadar guvenilir, stabil ve
dogru yorumlandigini (ve YANLIS yorumlanma risklerini) degerlendirmek.

## 2. Correlated Features

Stage 07'nin bulgusu (Value-grubu feature'lar permutation importance'ta
onemli gorunurken ablation'da RF performansini bazen iyilestirmesi)
yeniden degerlendirildi: `Line_Item_Qty_Sum` ve `Line_Item_Value_Sum`, hem
Permutation hem de Grouped SHAP'te en yuksek iki feature -- yuksek
importance + correlated information + redundancy riski birlikte
gozlemlenmistir. Bu **nedensel bir kanit degildir**, yalnizca correlated
information / attribution redistribution olasiligidir.

## 3. Background Sensitivity

`tree_path_dependent` (egitim path frekanslarini kullanir) vs
`interventional` (acik background dataset, feature correlation yapisini
kirar) karsilastirmasi (50 gözlem, deterministic 200-row background):

| Feature | tree_path_dependent | interventional | |Diff| |
|---|---:|---:|---:|
| Line_Item_Qty_Sum | yuksek | farkli | **1231.07** USD |
| Product_Group | orta | farkli | 765.18 USD |
| Line_Item_Value_Sum | yuksek | farkli | 388.59 USD |
| INCO_Term | orta | farkli | 489.80 USD |
| Country | orta | farkli | 301.28 USD |
| Shipment_Mode | dusuk | farkli | 83.64 USD |

En buyuk fark `Line_Item_Qty_Sum`'da -- bu feature'in `Line_Item_Value_Sum`
ile correlated olmasi, marginal (interventional) ve conditional
(tree_path_dependent) contribution arasindaki ayrismayi buyutebilir.

## 4. Attribution Stability

3 farkli deterministic background sample (seed=42,7,123, her biri n=200)
uzerinde Grouped SHAP ranking'i **tamamen stabil** (rank range=0, tum 6
feature icin) -- `stage12_explanation_stability.csv`.

## 5. Encoded Feature Mapping

43 encoded dimension, `stage12_feature_attribution_schema.json`'da raw
source/group/encoding ile eslendi. Grouping metodu: dummy columns'un
row-bazinda SIGNED SHAP toplami (mean absolute degil) -- bu, her dummy'nin
mean absolute SHAP'ini toplamaktan **farkli bir islemdir** ve source-level
importance'i daha dogru temsil eder.

## 6. Ranking Agreement

Permutation Importance vs Grouped SHAP: **Spearman rank correlation=0.943**
(n=6 raw feature). Yuksek uyum, iki farkli (model-agnostic/model-specific)
yontemin tutarli bir sinyal buldugunu gosterir.

## 7. Model-Specific Differences

ExtraTrees (bagging) ve XGBoost (boosting), Case E'de (model disagreement,
2014) farkli top-feature contribution uretti -- model mimarisi farkliligi,
hata degil.

## 8. Causal Interpretation Limitations

Bu notebook boyunca acikca belirtildi: SHAP values model attribution'dir,
nedensel kanit degildir. "Feature X degistirilirse maliyet tam SHAP degeri
kadar degisir" ifadesi hicbir yerde kullanilmamistir.

## 9. Risks (ve Bir Gercek Hata Duzeltmesi)

**Onemli Kendi-Denetim Bulgusu:** Permutation Importance'in ilk
implementasyonu, sklearn'in zaten dogru isaretli dondurdugu
`importances_mean` degerini (`scoring="neg_mean_absolute_error"` icin
`MAE_permuted - MAE_baseline`, pozitif=onemli) gereksiz yere negate etti --
bu, TUM feature'larin yanlislikla NEGATIF importance gostermesine neden
oldu ("in-sample pitfall" seklinde yanlis yorumlanabilirdi). Sentetik bir
sinyal/noise fixture ile sklearn'in gercek isaret kuralinin dogrulanmasi
uzerine kod duzeltildi; dogru (pozitif, sensible) sonuclar elde edildi.
Bu, projenin "gercek veriyle dogrulanmamis sonuc uretme" ilkesine uygun
olarak, yayina alinmadan once yakalanip duzeltilmistir.

Diger riskler: (1) Correlated features importance'i feature'lar arasinda
PAYLASTIRABILIR. (2) Background/perturbation assumption secimi
attribution'i materyal olarak degistirebilir (Section 3). (3) XGBoost
acik aciklamalar Stage 11'in cross-environment instability riskini tasir.

## 10. Engineering Decisions

Bkz `engineering_decisions.md` D-119 — D-127.
