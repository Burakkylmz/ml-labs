# LAB12 — Stage 08 Baseline Design

## 1. Overview

Bu belge, Stage 08'de gelistirilen 5 baseline modelin (B0-B4) tasarim gerekcesini,
matematiksel davranisini ve fallback politikasini belgeler.

## 2. Business Objective

Pre-Shipment Freight Cost Estimation icin, Stage 09 ML modellerinin asmasi gereken
istatistiksel ve business referans seviyelerini olusturmak.

## 3. Dataset Contract

SCMS Delivery History, shipment-level (`ASN/DN #`). Dataset SHA-256 ve Stage 05 protokol
fingerprint'i notebook icinde yeniden dogrulanmistir.

## 4. Evaluation Contract

Stage 05'in dondurulmus 4-fold Expanding-Window CV'si (validation yillari 2010-2013),
development population (Train split, n=5551, eligible=4987) -- degistirilmeden
kullanilmistir.

## 5. Baseline Model Definition

| Baseline | Aciklama | Kullanilan Feature |
|---|---|---|
| B0 | Global Median | Yok |
| B1 | Global Mean | Yok |
| B2 | Shipment Mode Median | Shipment_Mode |
| B3 | INCOTERM Median | INCO_Term |
| B4 | Hierarchical Segment Median | Shipment_Mode + INCO_Term |

## 6. Global Mean (B1)

$\hat y = \operatorname{mean}(y_{train})$ -- squared-error (MSE) objective'i icin optimal
constant predictor. Pooled MAE (gercek CV): **9106.34 USD**.

## 7. Global Median (B0)

$\hat y = \operatorname{median}(y_{train})$ -- absolute-error (MAE) objective'i icin
optimal constant predictor (training population uzerinde). Pooled MAE (gercek CV):
**9226.37 USD**.

**Onemli bulgu:** Training population uzerinde teorik olarak MAE-optimal olan Median,
bu CV'de Mean'den **daha kotu** performans gosterdi (9226.37 vs 9106.34 USD) -- training
population uzerinde optimal olmanin, temporal distribution shift altinda validation
doneminde de optimal kalacagini garanti etmedigini gosteren gercek bir ornektir.

## 8. Shipment Mode Median (B2)

Fold-training uzerinde her Shipment Mode icin median hesaplanir; unseen/missing ->
global median fallback. Pooled MAE: **8791.55 USD** (fallback rate: 0.000). Tek-segment
baseline'lar arasinda en iyisi.

## 9. INCOTERM Median (B3)

Ayni yaklasim INCO_Term'e uygulanir. Pooled MAE: **9145.64 USD** (fallback rate: 0.001).
B0'a kiyasla marjinal iyilesme.

## 10. Hierarchical Median (B4)

Fallback hiyerarsisi: Combined (Mode+INCOTERM) -> Mode -> INCOTERM -> Global. Pooled MAE:
**8694.56 USD** (fallback rate: 0.041) -- butun baseline'lar arasinda en iyisi, B2'ye
kiyasla kucuk ama gercek bir iyilesme (-96.99 USD).

## 11. Fallback Policy

Sirali fallback: once combined segment (min_support>=10 ise), sonra Shipment_Mode
(min_support>=10 ise), sonra INCO_Term (min_support>=10 ise), son olarak global median.
Reason code'lar: `GLOBAL_MEDIAN`, `GLOBAL_MEAN`, `MODE_MEDIAN`, `INCOTERM_MEDIAN`,
`COMBINED_SEGMENT`, `PARENT_FALLBACK`, `GLOBAL_FALLBACK`.

## 12. Minimum Support

`min_support=10` -- **evrensel bir istatistiksel kural degildir**. Gercek development-
eligible training verisinde, 17 (Mode x INCOTERM) kombinasyonundan **8'i (%47) 10'dan az
gozlem** iceriyor -- bu, threshold'un fallback mekanizmasini anlamli sayida gercek
senaryoda devreye sokacagini gosterir.

## 13. Prediction-Time Feature Availability

`Shipment_Mode` ve `INCO_Term`, Stage 07 Minimal Core Feature Contract'inin bir alt
kumesidir -- prediction-time availability zaten dogrulanmistir. INCOTERM'in numeric
target availability ile olasi iliskisi (Stage 03.5/04) ayrica not edilmistir -- bu
otomatik leakage anlamina gelmez, ancak deployment semantics'i ayri degerlendirilmelidir.

## 14. Leakage Prevention

Her baseline icin segment medianlari/mean'leri **yalnizca fold-training** uzerinde fit
edildi; validation target degerleri hicbir fitting isleminde kullanilmadi (programatik
olarak dogrulandi: `HierarchicalSegmentBaseline.predict()` metodu `y` parametresi almaz).

## 15. Implementation Architecture

Uc kucuk, test edilebilir class: `GlobalStatisticBaseline`, `SegmentMedianBaseline`,
`HierarchicalSegmentBaseline` (hepsi `fit`/`predict` arayuzu). Buyuk bir framework
gelistirilmedi. 8 unit-level fixture testi (known/unknown/low-support/missing/single-
observation segment senaryolari) sentetik veriyle gecti.

## 16. Reproducibility

`random_seed=42`. Referans pipeline (B4) iki kez fit edildi, tahminler `np.allclose` ile
birebir eslesti. Local ve Docker "temiz kernel" execution'lari 0 hata ile tamamlandi;
dataset hash her iki ortamda sabit kaldi.
