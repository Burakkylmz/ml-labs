# LAB12 — Stage 09 Benchmark Contract

## 1. Dataset Fingerprint

SHA-256: `9cffdb4ab8c6135b0f999c91b3a5c6e88a3c3dfc28c7c85feb9e97f986e3578a` -- Stage
01-08 boyunca degismeden dogrulandi.

## 2. Evaluation Protocol Fingerprint

`b87ca0fde5fd9ddef45f191a0bb1c3e4e2a014b9c9641be5e8d20bb2458935e7` (Stage 05, Stage 08'de
yeniden dogrulandi).

## 3. Feature Contract

Segment baseline'lari (B2-B4), Stage 07 Minimal Core Feature Contract'inin bir alt
kumesini (`Shipment_Mode`, `INCO_Term`) kullanir. Stage 09 modelleri, Stage 07'nin
Candidate A/B/C feature set'lerinden birini kullanmalidir (bkz
`stage07_feature_contract.md`).

## 4. Baseline Registry

B0 (Global Median), B1 (Global Mean), B2 (Shipment Mode Median), B3 (INCOTERM Median),
B4 (Hierarchical Segment Median) -- tam tanimlar `stage08_baseline_registry.json`'da.

## 5. Accepted Reference Baselines

**Statistical Reference:** B1 (Global Mean), Pooled MAE=9106.34 USD.
**Business Reference:** B4 (Hierarchical Segment Median), Pooled MAE=8694.56 USD.

## 6. Primary Metric

Pooled Out-of-Fold MAE (USD).

## 7. Secondary Metrics

Pooled RMSE, Median Absolute Error, WAPE (%), Bias (pred-actual convention), High-Cost
Segment MAE.

## 8. High-Cost Segment Evaluation

$HighCost = y_{val} \geq P90(y_{fold\_train})$ -- threshold yalnizca fold-training'den
hesaplanir. **Kritik bulgu:** tum 5 baseline, bu segmentte %100 underprediction rate
gosterdi -- Stage 09 modelleri bu zayifligi olcumsel olarak asip asmadigini
raporlamalidir.

## 9. Bias Evaluation

$Bias = mean(prediction - actual)$. Pozitif = overprediction, negatif = underprediction.
Bu convention Stage 09'da da korunmalidir.

## 10. Model Comparison Rules

- Stage 09 modelleri **ayni** dataset fingerprint ve CV protocol fingerprint uzerinde
  degerlendirilmelidir.
- Ayni development CV evaluation population (2014/2015 erisimi yok).
- **Stage 06-07 Ridge/Random Forest probe sonuclari yalnizca contextual referanstir** --
  farkli feature set (Stage 06/07 core+extended vs Stage 08'in sadece 2 kategorik
  feature'i) ve farkli preprocessing policy'leri nedeniyle bu baseline'larla
  **dogrudan karsilastirilamaz**. Stage 09, probe modelleri yeniden egitmeden, kendi
  benchmarking surecini bu contract uzerinden yurutmelidir.

## 11. Statistical Uncertainty

4 expanding-window fold, bagimsiz degil. Paired fold delta'lari ve yon tutarliligi
kullanilmali; naive independent-fold p-value hesaplanmamalidir.

## 12. Runtime Reporting

Fit+predict suresi her model/fold icin raporlanmali; local/Docker arasindaki runtime
farklari model kalitesinin gostergesi olarak yorumlanmamalidir.

## 13. Acceptance Criteria

Orijinal-scale MAE, RMSE, high-cost segment error, bias, fold-level stability,
unseen/missing category robustness, prediction-time availability, inference
simplicity, maintenance cost, reproducibility -- hepsi birlikte degerlendirilmelidir.
**%5 MAE improvement provisional bir engineering threshold'dur, business-approved SLA
degildir.**

## 14. Validation/Test Restrictions

2014 Validation ve 2015 Protected Test, Stage 09 model selection'inda **kullanilamaz** --
Stage 11 (external validation) ve Stage 14 (one-time test) icin saklanmistir.

## 15. Stage 09 Readiness

**CONDITIONAL GO.** Referans baseline'lar (B1 statistical, B4 business), degerlendirme
metrikleri ve kabul kriterleri belgelendi. Acik riskler: business-approved SLA yok,
sadece 4 CV fold, INCOTERM deployment-semantics incelemesi beklemede (D-007/INCOTERM
riski).
