# LAB12 — Stage 09 Comparative Benchmark Results

## 1. Experiment Overview

6 model, Stage 05'in dondurulmus 4-fold CV'si, Stage 07 Minimal Core feature set
uzerinde degerlendirildi.

## 2. Evaluation Population

3252 eligible validation observation (4 fold toplami) -- B1/B4 ile birebir ayni
(Fair Comparison Gate PASSED).

## 3. Model Configurations

Bkz `stage09_model_experiment_design.md` Section 8-9.

## 4. Linear Model Results

| Model | Pooled MAE | RMSE | Bias | Negative Preds |
|---|---:|---:|---:|---:|
| M01 Ridge | 8029.16 | 14824.53 | -1614.56 | 96 (2.95%) |
| M02 ElasticNet | 7993.60 | 15108.16 | -2120.35 | 0 |

ElasticNet, Ridge'den hafifce daha iyi ve **hic negatif tahmin uretmedi** -- L1
cezasi, bu veri setinde daha "korunakli" tahminler uretiyor.

## 5. Bagging Results

| Model | Pooled MAE | RMSE | Bias |
|---|---:|---:|---:|
| M03 Random Forest | 6151.90 | 12750.82 | -1353.05 |
| M04 ExtraTrees | 5880.35 | 12414.33 | -1519.74 |

ExtraTrees, Random Forest'tan **daha iyi** performans gosterdi -- rastgele split
threshold'larinin bu veri setinde variance reduction acisindan fayda sagladigi
gorulüyor.

## 6. Boosting Results

| Model | Pooled MAE | RMSE | Bias |
|---|---:|---:|---:|
| M05 XGBoost | 5808.51 | 12015.81 | -1226.13 |
| M06 LightGBM | 6236.25 | 12597.62 | -1332.63 |

XGBoost, LightGBM'den belirgin olarak daha iyi -- **butun 6 modelin en iyisi**.

## 7. Six-Model Benchmark (Pooled MAE Ranking)

M05 (5808.51) < M04 (5880.35) < M03 (6151.90) < M06 (6236.25) < M02 (7993.60) < M01
(8029.16).

## 8. B4 Comparison (Business Reference, 8694.56 USD)

| Model | Improvement vs B4 |
|---|---:|
| M05 | **%33.2** |
| M04 | %32.4 |
| M03 | %29.2 |
| M06 | %28.3 |
| M02 | %8.1 |
| M01 | %7.7 |

Tum 6 model B4'u gercek olcude asti; tree-based/boosting modeller linear modellerden
cok daha fazla iyilesme gosterdi.

## 9. B1 Comparison (Statistical Reference, 9106.34 USD)

Ayni siralama, daha buyuk yuzdeler: M05 %36.2, M04 %35.4, M03 %32.4, M06 %31.5, M02
%12.2, M01 %11.8.

## 10. Fold-Level Results

Fold-level MAE heatmap (`stage09_cv_results.csv`) -- iyilesme 4 fold'un hepsinde
tutarli yonde (Fair Comparison Gate + Paired Fold Comparisons ile dogrulandi).

## 11. Pooled Metrics

Pooled metrikler, fold validation-count agirlikli ortalamadir (basit fold-average
degildir) -- `pooled_metric()` fonksiyonu ile hesaplandi.

## 12. Paired Comparisons

| Karsilastirma | Sonuc |
|---|---|
| Ridge vs ElasticNet | ElasticNet hafifce daha iyi |
| RF vs ExtraTrees | ExtraTrees daha iyi |
| XGBoost vs LightGBM | XGBoost daha iyi |
| Best Linear (M02) vs Best Tree-Ensemble (M04) | Tree-ensemble cok daha iyi |
| Best Bagging (M04) vs Best Boosting (M05) | Boosting hafifce daha iyi |

## 13. Secondary Feature Set Experiment (Exploratory)

Extended Eligible (15 feature), best-of-family (M02, M04, M05) uzerinde test edildi:

| Model | Core MAE | Extended MAE | Fark |
|---|---:|---:|---:|
| M02 | 7993.60 | 7947.12 | -46.47 (hafif iyilesme) |
| M04 | 5880.35 | 5924.49 | +44.14 (hafif kotulesme) |
| M05 | 5808.51 | 5938.73 | +130.22 (kotulesme) |

**Bulgu:** Extended feature set, model aileleri arasinda **tutarsiz** bir etki
gosterdi -- linear model icin hafif fayda, tree-based modeller icin hafif zarar. Bu,
Stage 07'nin "No Selection genelde daha iyi" ve "Value grubu redundant" bulgularıyla
tutarlidir. Bu sonuc **exploratory**'dir (adaptive selection riski).

## 14. Statistical Uncertainty

4 (kismen bagimli) fold uzerinden hesaplandi. Yon tutarliligi (B4'u asma, tum fold'larda)
pratik kanit olarak kullanildi; naive independent-fold p-value hesaplanmadi.

## 15. Model Ranking

M05 > M04 > M03 > M06 > M02 > M01 (Pooled MAE'ye gore, en iyiden en kotuye).

## 16. Conclusions

- Tree-based/boosting modeller (M03-M06), linear modellerden (M01-M02) **buyuk
  farkla** daha iyi performans gosterdi.
- XGBoost (M05) genel en iyi model; ExtraTrees (M04) en iyi bagging alternatifi.
- ElasticNet, Ridge'e kiyasla negatif tahmin riskini ortadan kaldirdi.
- Extended feature set'in etkisi model-bagimli ve kucuk -- confirmatory bir kanit
  degildir.
