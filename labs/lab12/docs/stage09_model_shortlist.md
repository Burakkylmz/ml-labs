# LAB12 — Stage 09 Model Shortlist

## 1. Shortlisting Objective

Stage 10 Hyperparameter Optimization icin zaman/hesaplama maliyeti harcamaya deger
2-3 (veya daha az) modeli, gercek CV kanitiyla belirlemek.

## 2. Accepted Baseline

Business Reference: B4 (Hierarchical Median, 8694.56 USD). %5 improvement threshold
**provisional bir engineering target'tir**, business-approved SLA degildir.

## 3. Candidate Ranking

M05 (5808.51) < M04 (5880.35) < M03 (6151.90) < M06 (6236.25) < M02 (7993.60) < M01
(8029.16) USD pooled MAE.

## 4. Predictive Performance

M05 (XGBoost): B4'e gore %33.2 iyilesme -- en iyi. M04 (ExtraTrees): %32.4 -- en iyi
bagging alternatifi.

## 5. Fold Stability

M05 fold-std=665 (en stabil ust-performans modeli). M04 fold-std=935. Linear modeller
(ozellikle M02, std=1634) daha az stabil.

## 6. Tail Risk

M05 High-Cost MAE=17260 (en iyi). M04 High-Cost MAE=18353. Her ikisi de underprediction
rate'i baseline'in %100'unden anlamli olcude dusurdu (M05: %85.0, M04: %89.8).

## 7. Computational Cost

M05 fit~0.11s, predict~0.01s. M04 fit~0.15s, predict~0.08s. Her ikisi de bu olcekte
operasyonel olarak onemsiz.

## 8. Complexity

M05 (gradient boosting, 200 agac) ve M04 (100 agac, bagging) orta complexity'dedir --
Ridge'den daha karmasik ama is gereksinimlerini asmiyor.

## 9. Model Family Diversity

Shortlist **2 farkli model ailesini** temsil ediyor: Gradient Boosting (M05) ve
Bagging (M04) -- zorla eklenmedi, her ikisi de kendi ailesinde en iyi performans
gosteren ve tum kriterleri (meaningful improvement, stability, negligible negative
rate) karsilayan modellerdir.

## 10. Final Candidates

**Shortlisted: M05 (XGBoost), M04 (ExtraTrees).**

## 11. Rejected Alternatives

Yok -- hicbir model "Rejected for Optimization" statusune dusmedi (hepsi B4'u asti).

## 12. Inconclusive Results

**M01 (Ridge): Inconclusive** -- B4'u asiyor (%7.7) ama %2.95 negatif tahmin orani
tasiyor, bu riski acikca belirsiz birakiyor.

**Conditional Candidates:** M03 (RF, Bagging-icinde M04'ten daha zayif, redundant),
M06 (LightGBM, Boosting-icinde M05'ten daha zayif, redundant), M02 (ElasticNet, %8.1
iyilesme ama yuksek fold-fold varyans).

## 13. Business SLA Limitation

**Business-approved bir SLA/KPI threshold yoktur.** %5 improvement, sadece provisional
bir engineering reference noktasidir -- deployment acceptance criterion degildir, final
production basarisini garanti etmez.

## 14. Stage 10 Readiness

**GO.** 2 model-family-diverse, gercek kanitla desteklenen aday (M05 XGBoost, M04
ExtraTrees) belirlendi. Stage 10, bu iki model uzerinde kontrollu hyperparameter
optimization gerceklestirecektir (bkz `stage10_optimization_contract.md`).
