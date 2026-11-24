# LAB12 — Stage 11 External Validation Design

## 1. Objective

Stage 10'un development-CV ile secilen iki frozen candidate'ini (M04-T003 Primary,
M05-T000 Alternative), hicbir zaman egitim/tuning/feature selection icin
kullanilmamis 2014 external validation populasyonu uzerinde **ilk kez** degerlendirmek.

## 2. Pre-Validation Integrity Gates

| Gate | Kontrol | Sonuc |
|---|---|---|
| A | Dataset SHA-256 = `9cffdb4ab...578a` | PASSED |
| B | Stage05 protocol fingerprint recompute + split sayilari (Train=5551, Validation=910, Protected_Test=569) + sifir overlap | PASSED |
| C | Stage10 frozen candidate registry (`M04-T003`, `M05-T000`) parametre butunlugu | PASSED |
| D | Stage07 Minimal Core feature contract + Stage08 B1/B4 dev-CV degerleri (contextual only) | PASSED |
| E | Evaluation kurallarinin dondurulmasi (primary metric, high-cost tanimi, tie-break policy) | PASSED |
| F | Ortam/bagimlilik versiyonlari (python, sklearn, xgboost) | PASSED |

## 3. Full Development Refit Policy

Stage 10'un fold-bazli fit edilmis modelleri **2014 inference icin kullanilmaz**.
M04-T003 ve M05-T000 (ve B1/B4 baseline'lari) **butun eligible development
population** (2006-2013, N=4987) uzerinde sifirdan yeniden egitildi.

## 4. Evaluation Population Audit

2014 toplam shipment=910 (`Split=="Validation"`). Bu, **otomatik olarak** scorable
sample sayisi degildir -- eligibility ayrica olculdu: `Has_Numeric_Target==True`
olan **819** shipment (%90.0 label coverage), 91 shipment haric tutuldu.

## 5. Label Usage Contract

2014 target degerleri **sadece**: eligibility belirleme, scoring, residual hesaplama,
hata diagnostikleri, segment analizleri icin kullanildi. **Hicbir zaman**: training,
tuning, feature selection, transformation fitting, threshold optimizasyonu,
recalibration icin kullanilmadi.

## 6. 2015 Protected Test Isolation

2015 kayitlari `shipment_view` icinde yapisal olarak mevcuttur (raw CSV butun
donemleri kapsar), ancak **hicbir hucre** 2015 `Freight_Cost_USD` degerlerini
okumadi, aggregate etmedi, tahmin uretmedi veya herhangi bir metrik hesaplamadi.

## 7. One-Time Validation Policy

Bu notebook, 2014 uzerinde **tek bir** skorlama turu calistirir. 2014 sonuclarini
gorduktan sonra: yeniden skorlama, post-hoc clipping, model ayarlamasi, yeni
hyperparameter search, yeni feature selection veya target transformation degisikligi
**yapilmamistir**.

## 8. High-Cost Threshold Freezing

`HIGH_COST_THRESHOLD` = full eligible development targetlarinin P90'i = **23,897.32
USD**, 2014 target degerleri okunmadan **once** hesaplandi ve dondu.

## 9. Metric Contract

Primary: MAE (USD). Secondary: RMSE, Median AE, WAPE, Bias (`pred-actual`), P90/P95
Abs Error, High-Cost MAE/RMSE/Bias/Underprediction Rate, Negative Prediction Rate.

## 10. Fair Comparison Gate

Butun 4 predictor (M04-T003, M05-T000, B1, B4), **ayni 819 eligible shipment**
uzerinde programatik olarak dogrulanarak degerlendirildi.
