# LAB12 — Stage 09 Model Experiment Design

## 1. Purpose

Alti model ailesinin (Ridge, ElasticNet, Random Forest, ExtraTrees, XGBoost, LightGBM)
freight cost prediction performansini, Stage 05'in dondurulmus CV protokolu ve Stage 07
Minimal Core feature contract'i altinda, adil ve karsilastirilabilir sekilde
degerlendirmek.

## 2. Business Objective

Pre-Shipment Freight Cost Estimation icin, accepted business baseline'i (B4) gercek ve
tutarli olcude asan model aday(lar)ini belirlemek.

## 3. Dataset Contract

SCMS Delivery History, shipment-level (`ASN/DN #`). Dataset SHA-256 Stage 01-09 boyunca
degismeden dogrulandi.

## 4. Stage 05 Evaluation Protocol

Frozen 4-fold Expanding-Window CV (validation yillari 2010-2013), development population
(Train=5551, eligible=4987) -- degistirilmeden kullanildi, protokol fingerprint'i yeniden
hesaplanip dogrulandi.

## 5. Stage 08 Baseline References

B4 (Hierarchical Median, Pooled MAE=8694.56 USD) ve B1 (Global Mean, Pooled MAE=9106.34
USD) -- gercek Stage 08 artifact'larindan (`stage08_oof_predictions.csv`) yeniden
hesaplanip dogrulandi (Gate D), hardcode edilmedi.

## 6. Stage 07 Feature Contract

**Primary benchmark: Minimal Core** (`Line_Item_Qty_Sum`, `Line_Item_Value_Sum`;
`Shipment_Mode`, `INCO_Term`, `Country`, `Product_Group`). **Secondary (exploratory):
Extended Eligible** (15 feature) -- sadece best-of-family 3 model uzerinde.

## 7. Model Families

| ID | Model | Family |
|---|---|---|
| M01 | Ridge | Regularized Linear |
| M02 | ElasticNet | Regularized Linear |
| M03 | RandomForestRegressor | Bagging |
| M04 | ExtraTreesRegressor | Bagging |
| M05 | XGBRegressor | Gradient Boosting |
| M06 | LGBMRegressor | Gradient Boosting |

## 8. Fixed Estimator Configurations

Sabit, optimize edilmemis: Ridge(alpha=10.0), ElasticNet(alpha=1.0, l1_ratio=0.5),
RandomForest(n_estimators=80, max_depth=8, min_samples_leaf=3), ExtraTrees
(n_estimators=100, max_depth=8, min_samples_leaf=3), XGBoost(n_estimators=200, max_depth=5,
learning_rate=0.05), LightGBM(n_estimators=200, learning_rate=0.05, num_leaves=31). Early
stopping **kullanilmadi**.

## 9. Model-Specific Preprocessing

Ridge/ElasticNet: median imputation + `StandardScaler` (numeric), rare-category OneHot
(categorical). RF/ExtraTrees/XGBoost/LightGBM: median imputation (scaling YOK), rare-
category OneHot. Target transformation: **None** (original scale, D-039 Ridge+log
instability'den kacinilarak).

## 10. Experiment Registry

24 primary fit (6 model x 4 fold) + 12 secondary fit (3 model x 4 fold) + 8
reproducibility rerun = **44 toplam fit** (`stage09_experiment_registry.json`,
`stage09_reproducibility_report.json`).

## 11. Fair Comparison Rules

Fair Comparison Gate: tum modeller ve B1/B4, **ayni 3252 validation shipment**
uzerinde degerlendirildi (programatik olarak dogrulandi).

## 12. Computational Budget

Planli: ~36 fit. Gercek: 44 fit (reproducibility reruns dahil). Tum fit/predict
sureleri <1 saniye.

## 13. Leakage Controls

Her fold icin preprocessing/estimator **yalnizca fold-training** uzerinde fit edildi.
2014/2015 hicbir hucrede okunmadi (programatik assert). OOF leakage audit: tum shipment
key'leri Training split'ine ait (dogrulandi).

## 14. Reproducibility

`random_seed=42`. M05 (XGBoost) iki kez fit edildi, tahminler `np.allclose` ile
eslesti. Local ve Docker "temiz kernel" execution'lari 0 hata ile tamamlandi (14.8s,
16.3s).

## 15. Limitations

- Sadece 4 (kismen bagimli) CV fold.
- Sabit (optimize edilmemis) hyperparameters -- bu bir benchmark'tir, tuning degildir.
- Secondary feature experiment, primary CV sonucuna dayandigi icin exploratory/adaptive-
  selection riski tasir.
- XGBoost/LightGBM'in kendi ic rastgeleligi (thread-based) nedeniyle tekrarlanan
  calismalar arasinda kucuk (ondalik USD seviyesinde) farklar gorulebilir.
