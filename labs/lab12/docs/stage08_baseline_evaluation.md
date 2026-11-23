# LAB12 — Stage 08 Baseline Evaluation

## 1. Experiment Registry

5 baseline (B0-B4), 4 frozen CV fold = **20 planli fit**; reproducibility rerun (+8) ile
**28 gercek fit** (`stage08_reproducibility_report.json`).

## 2. Frozen CV Protocol

Stage 05 protokol fingerprint'i (`b87ca0fd...8935e`) notebook icinde yeniden hesaplanip
birebir eslesti. 4 fold, validation yillari 2010-2013.

## 3. Fold Sample Counts

| Fold | Train | Validation |
|---|---:|---:|
| 1 | 1735 | 780 |
| 2 | 2515 | 776 |
| 3 | 3291 | 861 |
| 4 | 4152 | 835 |

## 4. Metrics

MAE, RMSE, Median Absolute Error, WAPE, Bias (pred-actual convention), High-Cost MAE
(fold-training P90+ threshold).

## 5. B0 Results

Pooled MAE: **9226.37 USD**, RMSE: 17,773.47 USD, Bias: -7136.96 USD (net underprediction
-- median her zaman mean'in altindadir sag-kuyruklu dagilimda).

## 6. B1 Results

Pooled MAE: **9106.34 USD**, RMSE: 16,586.13 USD, Bias: -3222.33 USD. **B0'dan daha
iyi** -- training-population-optimal Median'in validation doneminde Mean'i asamadigi
gercek bir ornek.

## 7. B2 Results

Pooled MAE: **8791.55 USD**, Fallback Rate: 0.000 (Shipment_Mode'da development-eligible
populasyonda pratik olarak unseen-category sorunu yok).

## 8. B3 Results

Pooled MAE: **9145.64 USD**, Fallback Rate: 0.001. B0'a kiyasla marjinal iyilesme --
INCOTERM segmentasyonu tek basina guclu bir sinyal degil.

## 9. B4 Results

Pooled MAE: **8694.56 USD** (en iyi), Fallback Rate: 0.041. Fallback dagilimi (4 fold
ortalamasi): COMBINED_SEGMENT cogunlukta, PARENT_FALLBACK ve GLOBAL_FALLBACK kucuk bir
pay (`stage08_fallback_diagnostics.csv`).

## 10. OOF Aggregation

16,260 OOF prediction satiri (5 baseline x 3252 eligible validation observation). Her
shipment her baseline icin tam bir kez temsil edildi (leakage audit: tum shipment key'leri
Training split'ine ait, programatik dogrulandi).

## 11. Paired Comparisons

| Karsilastirma | Sonuc |
|---|---|
| B2 vs B3 | B2 daha iyi (tum 4 fold'da) |
| B2 vs B4 | B4 daha iyi (-96.99 USD pooled) |
| B3 vs B4 | B4 daha iyi |

## 12. Segment Performance

Shipment Mode bazinda segment-level MAE/Bias (`stage08_segment_error_analysis.csv`, 152
satir) -- B4, cogu segment'te B0/B2/B3'ten daha dusuk veya esdeger MAE gosteriyor.

## 13. Tail-Risk Analysis

**Kritik bulgu:** Fold-training P90+ (high-cost) shipment'larda, **5 baseline'in
HEPSINDE %100 underprediction rate** gozlendi. Bu, median/mean-tabanli constant
predictor'larin sag-kuyruklu bir dagilimda yapisal olarak kacinilmaz bir ozelligi --
tasarim kusuru degil, basit baseline'larin temel sinirlamasidir.

## 14. Bias

Tum baseline'lar negatif (underprediction) pooled bias gosterdi -- B1 (Mean, -3222.33)
B0'dan (Median, -7136.96) daha az negatif, cunku mean sag-kuyruktan daha fazla "cekilir".

## 15. Stability

Fold-fold MAE dalgalanmasi, Stage 06'daki ~%30'luk paterne benzer sekilde devam ediyor --
4 fold uzerinden kesin istatistiksel guven sinirlidir.

## 16. Computational Cost

Tum baseline fit+predict sureleri <0.01s (segment lookup/median hesaplama, ML model fit'i
degil) -- complexity farki pratik olarak onemsiz.

## 17. Statistical Uncertainty

4 (kismen bagimli, expanding-window) fold uzerinden hesaplandi. Naive independent-fold
p-value hesaplanmadi; yon tutarliligi (B2/B4'un B0'dan 4 fold'un 4'unde de daha iyi
olmasi) pratik kanit olarak kullanildi.

## 18. Engineering Conclusions

- B1 (Mean), B0'dan (Median) daha iyi -- **genel bir kural olarak sunulmamalidir**,
  bu CV'ye ozgu bir bulgudur.
- B2 (Shipment Mode), tek-segment baseline'lar arasinda en guclusu.
- B4 (Hierarchical), en iyi genel performans ama B2'ye kiyasla kucuk bir kazanc.
- Tum baseline'lar, high-cost shipment'larda yapisal olarak underpredict ediyor --
  Stage 09 modelleri bu zayifligi asmalidir.
