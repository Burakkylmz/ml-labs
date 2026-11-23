# LAB12 — Stage 10 Optimization Contract

**Bu dokuman optimization implementation DEGILDIR -- yalnizca bir sonraki asamanin
sozlesmesidir.**

## 1. Purpose

Stage 10 Hyperparameter Optimization'in sinirlarini, girdi contract'ini ve basarim
kriterlerini onceden belgelemek.

## 2. Dataset Fingerprint

SHA-256: `9cffdb4ab8c6135b0f999c91b3a5c6e88a3c3dfc28c7c85feb9e97f986e3578a`.

## 3. Stage 05 Protocol Fingerprint

`b87ca0fde5fd9ddef45f191a0bb1c3e4e2a014b9c9641be5e8d20bb2458935e7`.

## 4. Shortlisted Models

**M05 (XGBRegressor, Gradient Boosting)** ve **M04 (ExtraTreesRegressor, Bagging)**.

## 5. Fixed Starting Configurations

M05: n_estimators=200, max_depth=5, learning_rate=0.05, subsample=0.8,
colsample_bytree=0.8, reg_lambda=1.0, tree_method=hist. M04: n_estimators=100,
max_depth=8, min_samples_leaf=3. Bu degerler Stage 10 aramasinin **baslangic
noktasidir**, henuz optimize edilmemistir.

## 6. Feature Set Policy

Varsayilan: Stage 07 Minimal Core (6 feature). Extended Eligible, Section 12/Challenge
3 bulgularina gore **exploratory** kalir (M04/M05 icin kucuk/karisik etki olculdu) --
confirmatory kanit olmadan Stage 10'un varsayilan feature setine YUKSELTILMEMELIDIR.

## 7. Preprocessing Contract

M04 icin scaling yok, rare-category OneHot categorical. M05 icin ayni (tree-based,
scaling'e gerek yok). Stage 06/07'den reused, Stage 10'da yeniden optimize
edilmeyecek.

## 8. Primary Metric

Pooled OOF MAE (USD).

## 9. Secondary Metrics

Pooled RMSE, WAPE (%), Bias (pred-actual), High-Cost MAE, Underprediction Rate.

## 10. Tail-Risk Constraints

Stage 10 tuning, Stage 09'un High-Cost MAE veya Underprediction Rate degerlerini
**acik bir gerekce olmadan kotulestirmemelidir** (M05: High-Cost MAE=17260,
Underprediction=%85.0; M04: High-Cost MAE=18353, Underprediction=%89.8).

## 11. Hyperparameter Optimization Boundaries

Stage 10'da tanimlanacak -- bu notebookta **calistirilmadi**. Arama sinirlari, Stage
09'un sabit degerleri etrafinda makul bir aralikta olmalidir (orn. XGBoost
max_depth ∈ [3,8], n_estimators ∈ [100,400]) -- kesin degerler Stage 10'un kendi
tasarim surecine aittir.

## 12. Temporal CV Rules

Stage 05'in dondurulmus 4-fold Expanding-Window CV'si **degistirilmeden** yeniden
kullanilmalidir. Yeni split olusturulmamalidir.

## 13. Search Budget

Stage 10'da tanimlanacak. Bu notebook sadece 2 model icin arama alani onerir, bir
arama sayisi/sinirlamasi belirlemez.

## 14. Selection Bias Controls

Hyperparameter search, **frozen CV validation fold'larini early stopping veya
search-decision icin kullanmamalidir** -- nested CV veya train-only validation
design'i Stage 10'da tasarlanmalidir (bu notebook'un Stage 09 kisitlamasiyla
tutarli).

## 15. Validation/Test Isolation

2014 Validation ve 2015 Protected Test, Stage 10'da da **kullanilamaz** -- Stage
11/14 icin saklanmistir.

## 16. Reproducibility

`random_seed=42`. Her finalist icin refit-twice + `np.allclose` kontrolu zorunludur
(Stage 09'da M05 icin dogrulandi).

## 17. Known Limitations

Sadece 4 CV fold; sabit (optimize edilmemis) baslangic konfigurasyonlari; business-
approved SLA yok; XGBoost/LightGBM'in thread-tabanli run-to-run kucuk farkliliklari.

## 18. Stage 10 Entry Criteria

**GO.** En az 2 model-family-diverse, gercek ve fold-tutarli iyilesme gosteren aday
(M05, M04) belirlendi; dondurulmus protokol ve feature contract hazir.
