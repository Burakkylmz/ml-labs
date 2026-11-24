# LAB12 — Stage 12 Explainability Design

## 1. Purpose

Stage 11'de kabul edilen frozen point predictor'in (M04-T003, ExtraTrees)
genel ve yerel davranisini, model-specific (SHAP TreeExplainer) ve
model-agnostic (Permutation Importance) yontemlerle acmak -- **modeli
degistirmeden**.

## 2. Frozen Model Contract

M04-T003 (ExtraTrees): `{n_estimators=200, min_samples_split=10,
min_samples_leaf=2, max_features=0.8, max_depth=12, bootstrap=False,
random_state=42}`. Stage 11'in fitted estimator artifact'i persist
edilmemisti; bu nedenle ayni configuration ve full eligible development
population (2006-2013, n=4987) uzerinde yeniden fit edildi.
**Numerical identity check**: refit model, Stage 11'in 2014 external
predictions'i ile **0.000000 USD** farkla eslesti (n=819).

## 3. Explainability Scope

Ana aciklamalar: M04-T003 (ExtraTrees). Ikincil karsilastirma: M05-T000
(XGBoost) -- Stage 11'in "marjinal olarak daha kotu ama yakin" external MAE
bulgusu nedeniyle dahil edildi.

## 4. Feature Lineage

Raw features (6) -> `ColumnTransformer` -> 43 encoded dimension. Her encoded
feature icin raw source/group/encoding mapping `stage12_feature_attribution_schema.json`'da
kayitlidir.

## 5. Global Methods

(1) Impurity-based Tree Importance (`stage12_tree_importance.csv`) -- sinirlama:
cardinality/correlation hassasiyeti. (2) Permutation Importance
(`stage12_permutation_importance.csv`, MAE scoring, development population,
n_repeats=10). (3) Mean Absolute SHAP (`stage12_global_shap_importance.csv`).

## 6. Local Methods

SHAP Waterfall, 5 deterministic case (Typical/High-Predicted/Low-Predicted/
High-Error-2014/Model-Disagreement-2014) -- bkz
`stage12_local_explanations.csv`.

## 7. SHAP Theory

Shapley value: $\phi_j = \sum_{S \subseteq N \setminus \{j\}}
\frac{|S|!(|N|-|S|-1)!}{|N|!}[f(S\cup\{j\}) - f(S)]$. `TreeExplainer`,
tree-based modeller icin bunu polynomial time'da exact hesaplar.

## 8. Background Policy

Varsayilan: `tree_path_dependent` (ayri background dataset gerektirmez).
Alternatif: `interventional` (deterministic 200-row development background,
`explanation_sample_seed=42`). Her ikisi de 2014/2015 target bilgisi
KULLANMAZ.

## 9. Output Scale

Raw USD (`model_output="raw"`) -- Stage 11'in target tanimi (orijinal olcek,
transformasyonsuz) ile tutarli.

## 10. Computational Budget

Deterministic explanation sample = 200 gözlem (seed=42). SHAP smoke test
(5 gözlem) -> full sample (200) -> stability check (3 seed x 200). Toplam
SHAP calls bounded; full-data SHAP interaction tensor HESAPLANMADI.

## 11. Leakage Prevention

Tum explainability hesaplamalari development population (2006-2013) veya
Stage 11'in 2014 descriptive-analysis-icin-onaylanmis predictions'ina
dayanir. 2015 hicbir yerde okunmadi.

## 12. Limitations

(1) Permutation Importance in-sample (training data) uzerinde yaniltici
olabilir -- bu notebook development population uzerinde hesapladi (ayrica
bkz `stage12_explanation_reliability.md`). (2) SHAP additivity tolerance
icinde ama tam sifir degil (floating-point, max diff ~1.9e-10 USD). (3)
XGBoost (M05-T000) acik SHAP sonuclari, Stage 11'in cross-environment
instability riskini tasir.
