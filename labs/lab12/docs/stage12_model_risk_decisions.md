# LAB12 — Stage 12 Model Risk Decisions

## 1. Risk Overview

Stage 12, Stage 11'in kabul ettigi point predictor'i (M04-T003) degistirmeden
acikladi ve development-only bir interval research protokolu calistirdi.
Asagidaki 6 risk boyutu bu calismanin gercek sonuclarindan derlenmistir.

## 2. Explainability Reliability (R1)

**Status: Approved.** SHAP additivity dogrulandi (max diff 1.89e-10 USD).
Permutation Importance vs Grouped SHAP ranking agreement: Spearman=0.943.
Explanation stability 3 background seed arasinda PERFECT (rank range=0).
**Residual risk:** tree_path_dependent vs interventional perturbation
assumption, `Line_Item_Qty_Sum` icin ~1231 USD'lik materyal bir fark
yaratiyor -- hangi assumption'in "dogru" oldugu kullanim amacina baglidir.

## 3. Model Stability (R5)

**Status: Mixed.** ExtraTrees (M04-T003): refit identity check 0.000000 USD,
local/Docker SHAP/calibration sonuclari BYTE-EXACT ozdes. XGBoost (M05-T000):
Stage 11'in belgeledigi cross-environment prediction instability (shipment
basina $9,338'a kadar fark) herhangi bir XGBoost-tabanli aciklama/calisma
icin de gecerlidir.

## 4. Calibration Validity (R3)

**Status: Production Interval Not Approved.** Overall coverage gap: 80%
nominal icin -7.0%, 90% nominal icin -6.9% -- ikisi de orneklem gurultusu
bandinin disinda. High-cost segment coverage: %43.6 (90% nominal) --
genel coverage'dan cok daha kotu.

## 5. High-Cost Shipment Risk (R2)

**Status: Confirmed, Unresolved.** Stage 11: point prediction seviyesinde
%89.9 underprediction. Stage 12: interval seviyesinde %43.6 coverage ve
%48-58 upper-bound miss rate (fold'a bagli). Bu iki bagimsiz bulgu AYNI
altta yatan riski (high-cost shipment'lar icin model/interval guvenilirligi
dusuk) farkli mercekten dogrulamaktadir.

## 6. Temporal Shift

Undercoverage'in 4 outer fold'un hepsinde tutarli kalmasi, bunun
distribution shift / temporal nonstationarity ile iliskili olabilecegini
gosterir -- kesin mekanizma ayristirilamamistir, ama tek bir anomalili
yila izole edilmemistir.

## 7. Label Selection Bias

Development ve 2014'te ~%90 label coverage (Stage 11 bulgusu) -- bu
calibration/evaluation'in sadece label-eligible subpopulation uzerinde
gecerli oldugu anlamina gelir; eligible-olmayan %10'un gercek maliyet
dagilimi bilinmemektedir.

## 8. Unresolved Feature Availability

D-006 (Weight_KG, Unknown prediction-time availability) ve D-007 (label
timestamp, Conditional) degismeden acikta kaldi -- Stage 12 bu kararlari
DEGISTIRMEMISTIR.

## 9. Model Output Validity

Point prediction: her zaman finite, non-negative (0 negatif tahmin, Stage
11 2014 bulgusu). Interval: RAW lower bound %58.1 oraninda negatif (Freight
Cost negatif olamayacagi icin bu, interval'in dogrudan kullaniminda bir
sinirlamadir -- clipped-display varyanti ayri raporlandi, gizlice
UYGULANMADI).

## 10. Business SLA Limitations

Bu proje icin business-approved monetary tolerance veya asymmetric loss
function YOKTUR. Bu dokuman "production-ready" veya "SLA satisfied" sonucu
**URETMEMEKTEDIR**.

## 11. Approved Outputs

- Frozen point prediction (M04-T003) -- Approved for Stage 13 Prototype.
- Global/Local explainability (Tree/Permutation/SHAP) -- Approved for
  Stage 13 Prototype.

## 12. Research-Only / Conditional / Rejected Outputs

- XGBoost (M05-T000) secondary explanation -- **Conditional** (cross-environment
  risk inherited from Stage 11).
- Prediction intervals (Object B) -- **Production Interval Not Approved**
  (Research Only / Disabled by Default).

## 13. Stage 13 Readiness

**CONDITIONAL GO.** Point predictor ve explainability outputlari Stage 13
prototipine tasinabilir. Uncertainty/interval output'u varsayilan olarak
DEVRE DISI birakilmali, version-matched bir calibration contract'i
olusturulana kadar.
