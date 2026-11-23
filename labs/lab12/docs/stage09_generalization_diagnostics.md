# LAB12 — Stage 09 Generalization Diagnostics

## 1. Purpose

Modelleri sadece ortalama metrikler uzerinden degil, failure mode'lari (generalization
gap, tail risk, bias, extreme errors) uzerinden degerlendirmek.

## 2. Training-Validation Gap

`stage09_generalization_gap.csv` -- her model icin Mean_Training_MAE vs
Mean_Validation_MAE. Buyuk gap, overfitting VEYA temporal distribution shift'ten
kaynaklanabilir -- ikisi tam ayristirilamaz; bu notebook'ta gap tek basina overfitting
kaniti olarak sunulmadi.

## 3. Temporal Stability

Fold-level MAE heatmap (`stage09_cv_results.csv`) -- XGBoost (M05) en dusuk fold-fold
std'ye (665.48) sahip en iyi performans gosteren modeldir; ElasticNet (M02) en yuksek
std'ye (1634.11) sahiptir.

## 4. Residual Analysis

Residual convention: $e = y - \hat y$ (bias convention ile ters isaretli). Residual
histogramlari (M01, M04, M05 ornek olarak) sag-kuyruklu target'in model tahminlerinde
de iz birakan asimetrik bir hata dagilimi gosteriyor.

## 5. High-Cost Segment

Stage 08 ile ayni tanim: $HighCost = y_{val} \geq P90(y_{fold\_train})$, threshold
yalnizca fold-training'den. High-Cost MAE: M05=17260, M04=18353, M03=18630,
M06=17865, M02=25107, M01=23215 USD.

## 6. Underprediction

**Kritik bulgu:** Stage 08'deki 5 baseline'in HEPSİ %100 underprediction gosterirken,
Stage 09 modelleri bu oraniyi **dusurdu** (ama ortadan kaldirmadi): M04=89.8%,
M01=89.4%, M02=92.5%, M03=86.2%, M06=83.1%, M05=85.0%. Bu, gercek ama **kismi** bir
iyilesmedir -- hicbir model high-cost segmentte sistematik underprediction'i tamamen
ortadan kaldirmadi.

## 7. Prediction Bias

Tum modeller negatif (underprediction) pooled bias gosterdi: M05=-1226, M04=-1520,
M03=-1353, M06=-1333, M02=-2120, M01=-1615 USD -- ancak hepsi Stage 08 baseline'larindan
(B4=-6489, B0=-7137) **cok daha az negatif** -- gercek bir iyilesme.

## 8. Extreme Errors

Top-1%/Top-5% error contribution (`stage09_residual_diagnostics.csv`) -- en kotu %1
tahmin, toplam absolute error'un onemli bir kismini olusturuyor (model aileleri
arasinda farkli oranlarda); bu analiz sadece development OOF uzerinde yapildi.

## 9. Segment-Level Errors

Shipment Mode/Country/Product Group bazinda MAE/Bias (`stage09_segment_error_analysis.csv`,
3 ornek model icin). Kucuk segmentlerde (n<5) metrik hesaplanmadi -- descriptive, kesin
genelleme yapilmadi.

## 10. Error Distribution

Absolute Error ECDF (M01, M04, M05) -- tree/boosting modellerin hata dagilimi, linear
modellerden daha "sivri" (dusuk hatalarda daha fazla yogunlasma) gorunuyor.

## 11. Model Family Risks

- **Linear (M01/M02):** Negatif tahmin riski (ozellikle M01, %2.95); yuksek fold-fold
  varyans (M02).
- **Bagging (M03/M04):** Negatif tahmin riski yok; orta generalization gap.
- **Boosting (M05/M06):** En iyi performans, ancak kucuk oranda negatif tahmin riski
  (M05 %0.12, M06 %0.25).

## 12. Operational Risks

Tum modellerin fit/predict suresi <1 saniye -- bu olcekte operasyonel bir engel yok.
Negatif tahminler, raw model output'u uzerinden scoring yapildigi icin (post-hoc
clipping uygulanmadi) acikca gorunur kalmistir.

## 13. Limitations

Sadece 4 CV fold; sabit hyperparameters; XGBoost/LightGBM'in kendi ic thread-tabanli
rastgeleligi nedeniyle kucuk run-to-run farkliliklar gorulebilir.

## 14. Conclusions

Stage 09 modelleri, Stage 08 baseline'larinin iki temel zayifligini (yuksek MAE, %100
high-cost underprediction) **gercek ama kismi** olarak iyilestirdi. Hicbir model bu
zayifliklari tamamen ortadan kaldirmadi -- Stage 10/11'de bu sinirlamalar hala
gecerlidir.
