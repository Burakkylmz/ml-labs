# LAB12 — Stage 10 Optimization Design

## 1. Overview

Bu belge, Stage 09'da kanitlarla secilmis iki model ailesini (M04 ExtraTrees, M05
XGBoost), sinirli ve tekrarlanabilir bir search budget altinda optimize eden Stage 10
sürecinin tasarimini belgeler.

## 2. Business Objective

Pre-Shipment Freight Cost Estimation icin, development-CV uzerinde kanitlanmis,
reproducible hyperparameter configuration'lari belirlemek -- final model secimi
**Stage 11 external validation'dan once yapilmaz**.

## 3. Dataset Contract

SHA-256: `9cffdb4ab8c6135b0f999c91b3a5c6e88a3c3dfc28c7c85feb9e97f986e3578a` -- Stage
01-10 boyunca degismeden dogrulandi.

## 4. Frozen CV Protocol

Stage 05'in 4-fold Expanding-Window CV'si (`b87ca0fd...8935e`), degistirilmeden yeniden
kullanildi -- 5 gate (A-E) + Gate F (dependency) programatik olarak dogrulandi.

## 5. Stage 09 Shortlist

M04 (ExtraTrees, Pooled MAE=5880.35 USD) ve M05 (XGBoost, Pooled MAE=5808.51 USD --
Stage 09'un orijinal raporu) -- her ikisi de gercek `stage09_model_shortlist.json`'dan
geri yuklendi.

## 6. Optimization Objective

**Pooled OOF MAE (USD)** -- Stage 08-09 ile ayni tanim.

## 7. Search Strategy

`sklearn.model_selection.ParameterSampler` + mevcut frozen CV runner (bounded manual
search) -- `RandomizedSearchCV`'nin varsayilan fold-score-averaging mekanizmasi
**kullanilmadi**, cunku bu pooled-metric tanimindan farkli bir objective uretebilirdi.

## 8. Search Budget

16 trial/model (T000 referans + 15 orneklenen) x 4 fold = **128 fit** -- butce hicbir
trial sonucu gorulmeden sabitlendi (`stage10_search_budget.json`).

## 9. Experimental Controls

Her trial: ayni frozen fold membership, ayni Minimal Core feature set, ayni target
eligibility, ayni preprocessing (median imputation, rare-category OneHot, scaling yok),
ayni scoring tanimlari.

## 10. Leakage Prevention

2014/2015 target degerleri hicbir hucrede okunmadi (programatik olarak tasarimla
garanti edildi). Early stopping kullanilmadi -- frozen validation fold'lar booster
konfigurasyon secimine sizmadi.

## 11. Trial Management

Her trial stable bir ID (`M04-T000`...`M04-T015`, `M05-T000`...`M05-T015`) ve config
fingerprint ile izlendi (`stage10_trial_manifest.csv`, FROZEN once execution).

## 12. Computational Resources

CPU uzerinde, `n_jobs=2` (estimator-level), outer loop sequential. Toplam 128 fit,
~90-100 saniyede tamamlandi (ortam yukune bagli).

## 13. Reproducibility

`random_seed=42`. M04'un en iyi trial'i iki kez fit edildi, tahminler `np.allclose` ile
eslesti. **Onemli bulgu:** XGBoost'un `hist` tree_method'u, thread-sayisina bagli kucuk
floating-point farkliliklar gosterebilir -- bu, kontrollu bir `n_jobs` deneyiyle
dogrulandi ve `stage10_reproducibility_report.json`'da belgelendi.

## 14. Selection Bias

16 configuration denenip en iyisinin secilmesi **selection optimism** riski tasir --
bu development-CV sonucu **bagimsiz bir dogrulama degildir**. Stage 11 (2014) bu
nedenle zorunludur.

## 15. Known Limitations

Sadece 16 trial, 5-9 boyutlu search space'lerin kucuk bir orneklemidir; XGBoost'ta hicbir
sampled trial referansi (bu oturumda) asamadi; cross-environment (local vs Docker)
calistirmalar, XGBoost icin ~%0.10 buyuklugunde farkli "en iyi trial" secimi uretebildi
-- bu, bulgunun zaten "inconclusive" olmasini guclendiren bir kanittir.
