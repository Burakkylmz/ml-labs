# LAB12 — Stage 10 Optimization Results

## 1. Experiment Registry

32 configuration (16/model, T000 referans dahil) x 4 fold = **128 fit**
(`stage10_optimization_registry.json`, `stage10_trial_manifest.csv`).

## 2. Reference Models

M04 (ExtraTrees) T000: 5880.35 USD. M05 (XGBoost) T000 (bu trial loop'ta): 5818.29 USD.

## 3. Trial Budget

16 trial/model, hicbir trial sonucu gorulmeden sabitlendi.

## 4. ExtraTrees Search Results

En iyi trial: **M04-T003** (`n_estimators=200, min_samples_split=10,
min_samples_leaf=2, max_features=0.8, max_depth=12`) = **5686.34 USD**.
**+3.30% iyilesme**, 4/4 fold'da tutarli (Mean_Delta=-190.21 USD).

## 5. XGBoost Search Results

En iyi trial: **M05-T000 (referansin kendisi)**. Hicbir sampled trial (15 aday)
referansi gecemedi. **+0.00% iyilesme -- Tuning Benefit Inconclusive.**

## 6. Pooled MAE Ranking

M04-T003 (5686.34) < M05-T000 (5818.29) < M04-T000 (5880.35).

## 7. Fold-Level Metrics

M04 tuned, 4/4 fold'da referanstan daha iyi (fold-level heatmap,
`stage10_temporal_stability.csv`). M05'te hicbir fold'da hicbir sampled trial
referansi gecemedi.

## 8. Parameter Sensitivity

M04: `max_depth` (corr=-0.84), `min_samples_leaf` (corr=+0.45) en etkili parametreler.
M05: `min_child_weight` (corr=+0.70), `max_depth` (corr=-0.54) en etkili parametreler
(`stage10_parameter_sensitivity.csv`). **Bu korelasyonlar 16 trial'lik kucuk bir
orneklemden geliyor -- descriptive'dir, causal degildir.**

## 9. Parameter Interactions

`stage10_parameter_interactions.csv`: M05 learning_rate x n_estimators corr=-0.42,
max_depth x min_child_weight corr=-0.35. Kucuk ornek buyuklugu nedeniyle kesin
interaction kaniti olarak sunulmuyor.

## 10. Search Progress

Best-so-far egrileri (`stage10_optimization_progress.csv`): M04'te iyilesme trial 3'te
geldi ve sonrasinda sabit kaldi; M05'te best-so-far hicbir zaman T000'in altina
dusmedi (bu local calistirmada).

## 11. Baseline Improvement

M04 tuned, Stage 08 B4'e (8694.56 USD) gore %34.6, B1'e (9106.34 USD) gore %37.5
iyilesme gosteriyor. M05 (degismeden), B4'e gore %33.1 iyilesme.

## 12. Statistical Uncertainty

4 (kismen bagimli, expanding-window) fold uzerinden hesaplandi. M04'un 4/4 fold'da
tutarli iyilesmesi pratik kanit olarak kullanildi; naive p-value hesaplanmadi.

## 13. Computational Cost

M04: mean fit time referans=0.336s, tuned=0.684s (daha fazla agac/derinlik). M05:
mean fit time=0.133s (T000=best, degismedi).

## 14. Failed Trials

**0 failed trial** -- tum 32 configuration (128 fit) basariyla tamamlandi, hicbir
NaN/infinite prediction/runtime error olusmadi.

## 15. Reproducibility

M04'un en iyi trial'i iki kez fit edildi, tahminler birebir eslesti (`np.allclose`).
**Kritik bulgu:** XGBoost'un referans skoru, (a) Stage 09'un orijinal raporuna gore
(5808.51 vs 5818.29, bu oturumda, %0.17 fark) ve (b) local'e gore Docker'da (5818.29
vs Docker'da farkli bir trial'in 5802.50 secilmesi, %0.10 fark) kucuk farkliliklar
gosterdi -- **her ikisi de XGBoost'un `hist` tree_method'unun thread-sayisina bagli
floating-point non-determinism'inden kaynaklaniyor**, kontrollu bir `n_jobs` deneyiyle
dogrulandi (bkz `stage10_reproducibility_report.json`). ExtraTrees (bootstrap=False)
HER IKI ortamda da birebir aynı sonucu uretti (%0.000 fark) -- bu, sorunun XGBoost'a
ozgu oldugunu teyit ediyor.

## 16. Engineering Conclusions

- M04 (ExtraTrees) icin tuning **gercek ve tutarli** bir iyilesme buldu.
- M05 (XGBoost) icin tuning **hicbir robust iyilesme bulamadi** -- referans korunuyor.
- Her iki sonuc da development-CV'ye **adaptif** olarak secilmistir -- Stage 11
  bagimsiz dogrulamasi gereklidir.
