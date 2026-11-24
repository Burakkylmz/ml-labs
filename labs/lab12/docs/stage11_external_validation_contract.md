# LAB12 — Stage 11 External Validation Contract

**Bu belge Stage 11 implementasyonu DEGILDIR -- yalnizca bir sonraki asamanin
sozlesmesidir. 2014 hicbir sekilde bu notebookta kullanilmamistir.**

## 1. Objective

Stage 10'un development-CV-secilmis provisional candidate'larini, bagimsiz bir
degerlendirme (2014 external validation) ile dogrulamak.

## 2. Dataset Fingerprint

SHA-256: `9cffdb4ab8c6135b0f999c91b3a5c6e88a3c3dfc28c7c85feb9e97f986e3578a`.

## 3. Stage 05 Protocol Fingerprint

`b87ca0fde5fd9ddef45f191a0bb1c3e4e2a014b9c9641be5e8d20bb2458935e7`.

## 4. Development Population

Training=5551, Target-eligible=4987 (2006-2013).

## 5. External Validation Period

2014-01-01 — 2014-12-31.

## 6. Protected Test Period

2015-01-01 ve sonrasi (gercek max tarih: 2015-12-31).

## 7. Candidate Models

**Primary:** M04 (ExtraTrees), Trial M04-T003, Pooled MAE (dev-CV)=5686.34 USD.
**Alternative:** M05 (XGBoost), Trial M05-T000 (= Stage 09 referansi), Pooled MAE
(dev-CV)=5818.29 USD.

## 8. Frozen Hyperparameters

M04: `{n_estimators=200, min_samples_split=10, min_samples_leaf=2, max_features=0.8,
max_depth=12, bootstrap=False, random_state=42, n_jobs=2}`. M05: `{n_estimators=200,
max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
tree_method="hist", random_state=42, n_jobs=2}`.

## 9. Frozen Feature Set

Stage 07 Minimal Core: numeric=`[Line_Item_Qty_Sum, Line_Item_Value_Sum]`,
categorical=`[Shipment_Mode, INCO_Term, Country, Product_Group]`.

## 10. Frozen Preprocessing

Median imputation (numeric), constant-fill "Missing" + rare-category OneHot
(`min_frequency=10`) (categorical), **scaling yok** (tree-based modeller).

## 11. Target Definition

`Freight Cost (USD)`, original scale, **transformasyon yok**.

## 12. Primary Metric

Pooled OOF MAE (USD).

## 13. Secondary Metrics

Pooled RMSE, WAPE (%), Bias (pred-actual), High-Cost MAE, High-Cost Underprediction
Rate.

## 14. High-Cost Risk Policy

Threshold = **ilgili donemin kendi training population'inin** P90'i -- 2014 target
degerleri threshold fitting icin **asla** kullanilmaz.

## 15. Negative Prediction Policy

Raw (unclipped) tahminler uzerinden scoring -- negatif tahminler sayilir ve
raporlanir, otomatik olarak veto edilmez (M05 icin ~3/3252 bekleniyor).

## 16. Statistical Uncertainty

Development-CV secimi **adaptive'dir** (selection optimism) -- Stage 11, bu
configuration'larin **ilk bagimsiz degerlendirmesidir**.

## 17. Evaluation Procedure

Primary ve Alternative candidate, **butun eligible development population** (2006-2013)
uzerinde yeniden fit edilmeli, sonra **bir kez** 2014 uzerinde skorlanmali.

## 18. Candidate Selection Rules

Primary candidate (M04 tuned) tercih edilir, **meger ki** 2014 sonuclari acik bir
tersine donus gostersin -- her iki candidate de MUTLAKA skorlanmalidir.

## 19. Tie-Breaking Policy

2014 pooled MAE farki, Stage 08-10'da gozlenen fold-fold gurultu bandi icindeyse
(kabaca birkac yuz USD), daha dusuk complexity/daha stabil candidate (M05) tercih
edilir.

## 20. No-Retuning Restriction

Stage 11'de **yeni hyperparameter search yapilamaz** -- configuration'lar bu
belgeyle dondurulmustur.

## 21. Known Limitations

Sadece 16 trial/model orneklendi (global optimum garantisi yok); XGBoost search
robust bir iyilesme bulamadi; business-approved SLA yok; D-006 (Weight), D-007 (label
timestamp), D-010 (Qty/Value aggregation) acik.

## 22. Stage 11 Entry Criteria

**GO.** Iki dondurulmus, model-family-diverse candidate configuration, development-CV
kanitiyla belgelendi.
