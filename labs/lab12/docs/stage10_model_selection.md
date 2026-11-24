# LAB12 — Stage 10 Model Selection

## 1. Selection Objective

Stage 11 external validation'a hangi hyperparameter configuration'lari gonderilmeli,
gercek development-CV kanitiyla belirlemek.

## 2. Candidate Models

M04 (ExtraTrees), M05 (XGBoost) -- Stage 09'un shortlisted modelleri.

## 3. Reference Configurations

M04: `n_estimators=100, max_depth=8, min_samples_leaf=3` (5880.35 USD). M05:
`n_estimators=200, max_depth=5, learning_rate=0.05, subsample=0.8,
colsample_bytree=0.8, reg_lambda=1.0` (5818.29 USD).

## 4. Tuned Configurations

M04: `n_estimators=200, min_samples_split=10, min_samples_leaf=2, max_features=0.8,
max_depth=12` (5686.34 USD). M05: **degismedi** (referansin kendisi en iyi trial).

## 5. Pooled MAE

M04 Tuned: 5686.34 USD (**en iyi genel sonuc**). M05: 5818.29 USD.

## 6. High-Cost Performance

M04 Tuned High-Cost MAE=17626.69 USD (referanstan daha iyi, 18353.31 USD'den).
M05 High-Cost MAE=17119.78 USD (degismedi).

## 7. Negative Predictions

M04: 0 (referans ve tuned). M05: 3 (referans ve tuned, degismedi) -- kucuk bir risk
notu, otomatik veto sebebi degil.

## 8. Prediction Bias

M04 Tuned Bias=-1427.57 USD (referanstan -1519.74'ten az negatif -- hafif iyilesme).
M05 Bias=-1161.81 USD (degismedi).

## 9. Fold Stability

M04 Tuned fold-std=810.23 (referans 934.69'dan daha stabil). M05 fold-std=666.27
(degismedi, zaten en stabil model).

## 10. Generalization Gap

M04 Tuned Gen_Gap=2512.67 (referans 2179.13'ten biraz daha yuksek -- training setine
biraz daha fazla uyum, ama 4/4 fold'da validation performansi hala daha iyi). M05
Gen_Gap=2960.49 (degismedi).

## 11. Runtime & Complexity

M04 Tuned mean fit time=0.684s (referans 0.336s'den ~2x daha yavas, daha fazla
agac/derinlik nedeniyle) -- bu olcekte operasyonel bir engel degil. M05=0.133s.

## 12. Selection Optimism

M04'un best trial'i, 16 configuration'in en iyisi olarak **adaptif olarak secildi** --
bu development-CV'ye ozel bir sonuctur, bagimsiz bir dogrulama degildir. M05'te hicbir
trial referansi gecemedigi icin bu risk M05 icin daha az gecerlidir (referans zaten
"secilen" konfigurasyon).

## 13. Provisional Primary Candidate

**M04 (ExtraTrees), M04-T003.** En dusuk Pooled MAE, 4/4 fold'da tutarli iyilesme,
high-cost performansta da iyilesme, 0 negatif tahmin.

## 14. Independent Family Alternative

**M05 (XGBoost), M05-T000 (= Stage 09 referansi).** Farkli model ailesi (Gradient
Boosting vs Bagging), en stabil fold performansi, tuning'den bagimsiz guclu bir
baseline.

## 15. Remaining Risks

Sadece 16 trial/model (global optimum garantisi yok); XGBoost search'u hicbir robust
iyilesme bulamadi; cross-environment (local/Docker) calistirmalar XGBoost icin farkli
"en iyi trial" secebiliyor (~%0.10 fark, inconclusive buyuklugunde); business-approved
SLA yok; D-006/D-007/D-010 acik.

## 16. Stage 11 Readiness

**GO.** Iki model-family-diverse, development-CV-kanitli aday (M04 tuned Primary, M05
reference Alternative) Stage 11 External Validation Contract'ina donduruldu.
